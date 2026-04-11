#Original source code from https://github.com/7aGiven/Phigros_Resource/blob/master/taptap.py
#Change in https://github.com/milk-12546/Phigros-Project-Dev/blob/main/CHANGELOG.md
import json
import os
import random
import string
import urllib.parse
import time
import hashlib
import uuid
from http.client import HTTPSConnection

import utils.downloader as downloader
import utils.apk_utils as apk_utils


class TapTapClient:
    def __init__(self, app_id: int = 165287):
        self.app_id = app_id
        self.host = "api.taptapdada.com"
        self.uid = uuid.uuid4()
        self.ua = "okhttp/5.3.2"
        self.x_ua = (
            "V=1&PN=TapTap&VN=2.94.0-rel.100300&VN_CODE=294001003&"
            f"LOC=CN&LANG=zh_CN&CH=default&UID={self.uid}&NT=1&"
            "SR=1200x2670&DEB=Xiaomi&DEM=Xiaomi+14&OSV=14"
        )
        self.quoted_x_ua = urllib.parse.quote(self.x_ua)

        self.conn = HTTPSConnection(self.host)

        self.apk_id = 0
        self.version_code = 0
        self.version_name = "0.0.0.0"

        self._fetch_remote_info()

        self.url = None
        self.name = None
        self.size = None
        self.md5 = None

    @staticmethod
    def _get_nonce():
        chars = string.ascii_lowercase + string.digits
        return "".join(random.sample(chars, 5))

    def _fetch_remote_info(self):
        path = f"/app/v2/detail-by-id/{self.app_id}?X-UA={self.quoted_x_ua}"
        self.conn.request("GET", path, headers={"User-Agent": self.ua})

        r = json.loads(self.conn.getresponse().read())

        download_data = r["data"]["download"]
        self.apk_id = download_data["apk_id"]
        self.version_code = download_data["apk"]["version_code"]
        self.version_name = download_data["apk"]["version_name"]

    def get_download_url(self):
        t = int(time.time())
        param = (
            f"abi=arm64-v8a,armeabi-v7a,armeabi&id={self.apk_id}&node={self.uid}"
            f"&nonce={self._get_nonce()}&sandbox=1&screen_densities=xhdpi&time={t}"
        )

        byte = f"X-UA={self.x_ua}&{param}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs"
        md5 = hashlib.md5(byte.encode()).hexdigest()
        body = f"{param}&sign={md5}"

        path = f"/apk/v1/detail?X-UA={self.quoted_x_ua}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.ua
        }
        self.conn.request("POST", path, body=body.encode(), headers=headers)

        r = json.loads(self.conn.getresponse().read())
        apk_info = r["data"]["apk"]
        self.url = apk_info["download"]
        self.name = apk_info["name"]
        self.size = apk_info["size"]
        self.md5 = apk_info["md5"]
        return self.url

    def get_apk(self, specific_ver: str = None, local_apk_dir: str = "./output/apks/"):
        os.makedirs(local_apk_dir, exist_ok=True)
        file_path, version_name = None, None

        if specific_ver:
            target_path = os.path.join(local_apk_dir, specific_ver)
            code, name = apk_utils.get_apk_info(target_path)
            if code is None:
                raise FileNotFoundError(f"指定的 APK 文件不存在或无效: {target_path}")
            print(f"使用指定版本: {name} (版本号 {code})\n路径: {target_path}")
            return target_path

        local_code, local_name, local_path = apk_utils.find_latest_apk(local_apk_dir)

        need_download = False
        if local_code is None:
            print("本地未找到任何 APK，将下载最新版本。")
            need_download = True
        elif local_code < self.version_code:
            print(f"本地版本: {local_name} ({local_code})")
            print(f"云端版本: {self.version_name} ({self.version_code})")
            answer = input("是否下载新版本？(Y/n): ").strip().lower()
            if answer != "n":
                need_download = True
            else:
                version_name = local_name
                file_path = local_path
        else:
            version_name = local_name
            file_path = local_path
            print("本地已是最新版本，无需下载")

        if need_download:
            download = downloader.FileDownloader(
                url=self.get_download_url(),
                name=os.path.join(local_apk_dir, self.name),
                size=self.size,
                md5=self.md5,
                ua=self.ua
            )
            file_path = download.start()
            if file_path is None:
                raise Exception("下载失败（MD5 校验未通过）")
            version_name = self.version_name
            print(f"新版本 {version_name} 下载完成")

        if file_path is None:
            raise Exception("无法获得有效的 APK 文件路径")
        print(f"使用版本: {version_name}\n路径: {file_path}")
        return file_path


if __name__ == "__main__":
    print(TapTapClient().get_download_url())