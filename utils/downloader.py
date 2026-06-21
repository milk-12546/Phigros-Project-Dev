#!/usr/bin/env python3
"""
多线程下载器（工作窃取 + 直接写入 + 预分配空间）
完全兼容 Windows / Linux / macOS
"""

import os
import sys
import math
import time
import queue
import shutil
import signal
import atexit
import hashlib
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from tqdm import tqdm

# ---------- 全局停止与清理 ----------
_stop_event = threading.Event()
_cleanup_paths = []

def _cleanup():
    for path in _cleanup_paths:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
        except Exception:
            pass

atexit.register(_cleanup)

def _signal_handler(sig, frame):
    print("\n接收到中断信号，正在安全退出...")
    _stop_event.set()

try:
    signal.signal(signal.SIGINT, _signal_handler)
except (AttributeError, ValueError):
    pass
try:
    signal.signal(signal.SIGTERM, _signal_handler)
except (AttributeError, ValueError):
    pass


class _WorkStealingDownloader:
    def __init__(self, url, output_dir, num_threads=4, retries=3,
                 checksum=None, block_size=20*1024*1024,
                 timeout=30, chunk_size=8192, show_progress=True):
        self.url = url
        self.output_dir = output_dir
        self.num_threads = num_threads
        self.retries = retries
        self.checksum = checksum
        self.block_size = block_size
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.show_progress = show_progress

        parsed = urlparse(url)
        self.filename = os.path.basename(parsed.path) or "downloaded_file"
        self.output_path = os.path.join(output_dir, self.filename)

        self.total_size = 0
        self.downloaded_bytes = 0
        self.lock = threading.Lock()
        self.total_bar = None
        self.thread_bars = []
        self.task_queue = queue.Queue()

    def _get_file_info(self):
        with requests.head(self.url, timeout=self.timeout) as resp:
            resp.raise_for_status()
            size = int(resp.headers.get('Content-Length', 0))
            accept_ranges = resp.headers.get('Accept-Ranges', '').lower() == 'bytes'
            return size, accept_ranges

    def _calc_checksum(self, filepath, algo='md5'):
        hash_func = hashlib.new(algo)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def _verify(self):
        if not self.checksum:
            return True
        try:
            algo, expected = self.checksum.split(':', 1)
            algo = algo.lower()
            if algo not in hashlib.algorithms_available:
                raise ValueError(f"不支持的算法: {algo}")
            actual = self._calc_checksum(self.output_path, algo)
            if actual.lower() != expected.lower():
                if self.show_progress:
                    print(f"\n❌ 校验失败！期望 {expected}，实际 {actual}")
                return False
            if self.show_progress:
                print("\n✅ 校验通过！")
            return True
        except Exception as e:
            if self.show_progress:
                print(f"\n⚠️ 校验出错: {e}")
            return False

    def _worker(self, thread_id):
        """工作线程：循环取块，下载并直接写入文件"""
        pbar = tqdm(
            total=self.total_size,
            desc=f"T{thread_id+1}",
            position=thread_id + 1,
            leave=False,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            miniters=1,
            colour='green',
            disable=(not self.show_progress),
        )
        self.thread_bars.append(pbar)

        while not _stop_event.is_set():
            try:
                block = self.task_queue.get(timeout=1)
            except queue.Empty:
                if self.task_queue.unfinished_tasks == 0:
                    break
                else:
                    continue
            except Exception:
                break

            block_idx, start, end = block
            success = False
            for attempt in range(1, self.retries + 1):
                if _stop_event.is_set():
                    break
                try:
                    # 下载该块，直接写入文件
                    headers = {'Range': f'bytes={start}-{end}'}
                    with requests.get(self.url, headers=headers, stream=True,
                                      timeout=self.timeout) as resp:
                        resp.raise_for_status()
                        # 每个线程独立打开文件，写入自己的偏移区域
                        with open(self.output_path, "rb+") as f:
                            f.seek(start)
                            offset = start
                            for chunk in resp.iter_content(chunk_size=self.chunk_size):
                                if _stop_event.is_set():
                                    raise StopIteration("中断")
                                if chunk:
                                    f.write(chunk)
                                    offset += len(chunk)
                                    # 更新进度
                                    with self.lock:
                                        self.downloaded_bytes += len(chunk)
                                        pbar.update(len(chunk))
                                        if self.total_bar:
                                            self.total_bar.update(len(chunk))
                    # 验证块大小
                    written = offset - start
                    expected = end - start + 1
                    if written != expected:
                        raise RuntimeError(f"块大小不符: {written} vs {expected}")
                    success = True
                    break
                except Exception as e:
                    if attempt < self.retries:
                        wait = 2 ** attempt
                        pbar.write(f"T{thread_id+1} 块 {block_idx} 失败 ({attempt}/{self.retries}): {e}, {wait}s后重试")
                        time.sleep(wait)
                    else:
                        pbar.write(f"T{thread_id+1} 块 {block_idx} 重试 {self.retries} 次后仍失败")
                        raise RuntimeError(f"块 {block_idx} 下载失败: {e}") from e

            self.task_queue.task_done()
            if not success:
                raise RuntimeError(f"块 {block_idx} 最终失败")

        pbar.close()

    def download(self):
        try:
            size, supports_range = self._get_file_info()
            if not supports_range:
                if self.show_progress:
                    print("⚠️ 服务器不支持 Range，降级为单线程")
                self.num_threads = 1
            self.total_size = size
            if size == 0:
                if self.show_progress:
                    print("⚠️ 文件大小为 0，可能无法下载")
                return False

            # 生成任务块
            if self.num_threads > 1 and supports_range:
                num_blocks = math.ceil(size / self.block_size)
                for i in range(num_blocks):
                    start = i * self.block_size
                    end = min(start + self.block_size - 1, size - 1)
                    self.task_queue.put((i, start, end))
                if self.show_progress:
                    print(f"文件大小: {size} 字节，块大小: {self.block_size}，共 {num_blocks} 个块")
            else:
                self.task_queue.put((0, 0, size - 1))
                if self.show_progress:
                    print("单线程下载")

            # 实际线程数（不超过块数且适应终端）
            actual_threads = min(self.num_threads, self.task_queue.qsize())
            terminal_lines = shutil.get_terminal_size().lines if hasattr(shutil, 'get_terminal_size') else 24
            max_visible = terminal_lines - 2
            if actual_threads > max_visible and self.show_progress:
                self.show_progress = False
                if self.show_progress:  # 避免重复
                    print(f"线程数 {actual_threads} 超过终端行数，隐藏子进度条")

            # 预先创建目标文件并分配空间（Windows 兼容）
            if os.path.exists(self.output_path):
                os.remove(self.output_path)
            with open(self.output_path, "wb") as f:
                f.truncate(self.total_size)      # 预分配文件空间
            _cleanup_paths.append(self.output_path)   # 若中途失败，清理

            # 总进度条
            self.total_bar = tqdm(
                total=size,
                desc="Total",
                position=0,
                leave=True,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                colour='blue',
                disable=(not self.show_progress),
            )

            # 启动线程池
            with ThreadPoolExecutor(max_workers=actual_threads) as executor:
                futures = [executor.submit(self._worker, i) for i in range(actual_threads)]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        if self.show_progress:
                            print(f"\n❌ 线程异常: {e}")
                        _stop_event.set()
                        break

            # 检查是否有未完成的任务
            if self.task_queue.unfinished_tasks > 0:
                if self.show_progress:
                    print(f"\n⚠️ 有 {self.task_queue.unfinished_tasks} 个块未完成")
                return False

            self.total_bar.close()
            # 从清理列表中移除（下载成功）
            if self.output_path in _cleanup_paths:
                _cleanup_paths.remove(self.output_path)

            # 校验
            if self._verify():
                if self.show_progress:
                    print(f"✅ 下载完成！文件: {self.output_path}")
                return True
            else:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                return False

        except Exception as e:
            if self.show_progress:
                print(f"\n❌ 下载失败: {e}")
            return False


# ========== 对外接口 ==========
def download_file(
    url: str,
    output_dir: str = ".",
    num_threads: int = 4,
    retries: int = 3,
    checksum: str = None,
    block_size: int = 20 * 1024 * 1024,
    show_progress: bool = True,
    timeout: int = 30,
    chunk_size: int = 8192,
) -> str | None:
    os.makedirs(output_dir, exist_ok=True)
    downloader = _WorkStealingDownloader(
        url=url,
        output_dir=output_dir,
        num_threads=num_threads,
        retries=retries,
        checksum=checksum,
        block_size=block_size,
        timeout=timeout,
        chunk_size=chunk_size,
        show_progress=show_progress,
    )
    success = downloader.download()
    return downloader.output_path if success else None


def cli_main():
    parser = argparse.ArgumentParser(description="多线程下载器")
    parser.add_argument("url", help="下载链接")
    parser.add_argument("-o", "--output-dir", default=".", help="输出目录")
    parser.add_argument("-t", "--threads", type=int, default=4, help="线程数 (默认4)")
    parser.add_argument("-r", "--retries", type=int, default=3, help="重试次数 (默认3)")
    parser.add_argument("--checksum", help="校验和，如 'md5:abc'")
    parser.add_argument("--block-size", type=int, default=20*1024*1024, help="块大小(字节)，默认20MB")
    parser.add_argument("--timeout", type=int, default=30, help="超时秒数")
    parser.add_argument("--no-progress", action="store_true", help="不显示进度条")
    parser.add_argument("--chunk-size", type=int, default=8192, help="流式块大小")
    args = parser.parse_args()

    result = download_file(
        url=args.url,
        output_dir=args.output_dir,
        num_threads=args.threads,
        retries=args.retries,
        checksum=args.checksum,
        block_size=args.block_size,
        show_progress=not args.no_progress,
        timeout=args.timeout,
        chunk_size=args.chunk_size,
    )
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    cli_main()