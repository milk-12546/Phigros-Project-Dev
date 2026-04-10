import os
from pyaxmlparser import APK

def find_latest_apks(apk_dir):
    latest_versions = {}
    version_code = None
    version_name = None
    file_path = None

    for file in os.listdir(apk_dir):
        if file.endswith(".apk"):
            file_path = os.path.join(apk_dir, file)
            try:
                apk = APK(file_path)
                package = apk.package
                version_code = int(apk.version_code)
                version_name = apk.version_name

                if package not in latest_versions or version_code > latest_versions[package]["version_code"]:
                    latest_versions[package] = {
                        "version_code": version_code,
                        "version_name": version_name,
                        "path": file_path
                    }
            except Exception as e:
                print(f"{file}: {e}")

    for pkg, info in latest_versions.items():
        version_code = info["version_code"]
        version_name = info["version_name"]
        file_path = info["path"]

    return version_code, version_name, file_path