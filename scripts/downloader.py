import sys
import hashlib
import threading
from urllib import request
from tqdm import tqdm

class FileDownloader:
    def __init__(self, url:str, name:str, size:int=None, md5:str=None, ua:str="okhttp/5.3.2", thread_count:int=8):
        self.url = url
        self.name = name
        self.size = int(size) if size else None
        self.md5 = md5
        self.ua = ua
        self.thread_count = thread_count
        self.lock = threading.Lock()

    def _download_chunk(self, start, end, main_pbar, thread_id):
        chunk_size = end - start + 1
        sub_pbar = tqdm(
            total=chunk_size,
            unit="B",
            unit_scale=True,
            desc=f"{thread_id:02d}",
            position=thread_id + 1,
            leave=True,
            ncols=80,
            file=sys.stdout
        )

        try:
            headers = {
                "Range": f"bytes={start}-{end}",
                "User-Agent": self.ua
            }
            r = request.Request(self.url, headers=headers)

            with request.urlopen(r, timeout=30) as response:
                with open(self.name, "rb+") as f:
                    f.seek(start)
                    while True:
                        chunk = response.read(512 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        size = len(chunk)
                        sub_pbar.update(size)
                        with self.lock:
                            main_pbar.update(size)
        except Exception as e:
            with self.lock:
                tqdm.write(f"{thread_id}: {e}")
        finally:
            sub_pbar.close()

    def verify_md5(self):
        if not self.md5:
            return True

        md5_hash = hashlib.md5()
        with open(self.name, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)

        actual_md5 = md5_hash.hexdigest().lower()
        if actual_md5 == self.md5.lower():
            return True
        else:
            print(f"MD5 False: {self.md5} <-x- {actual_md5}")
            return False

    def start(self):
        file_size = self.size
        if not file_size:
            try:
                headers = {"User-Agent": self.ua}
                req = request.Request(self.url, headers=headers, method='HEAD')
                with request.urlopen(req, timeout=10) as res:
                    file_size = int(res.headers.get("Content-Length", 0))
            except:
                pass

        if not file_size or file_size <= 0:
            raise Exception("Size Error")

        with open(self.name, "wb") as f:
            f.truncate(file_size)

        chunk_size = file_size // self.thread_count
        main_pbar = tqdm(total=file_size, unit="B", unit_scale=True, desc="Total", position=0, ncols=80, file=sys.stdout)

        threads = []
        for i in range(self.thread_count):
            start = i * chunk_size
            end = file_size - 1 if i == self.thread_count - 1 else (i + 1) * chunk_size - 1
            t = threading.Thread(target=self._download_chunk, args=(start, end, main_pbar, i))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        main_pbar.close()
        print("\n" * (self.thread_count + 1))
        return self.name