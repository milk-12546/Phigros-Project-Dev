import os
from pyaxmlparser import APK


def get_apk_info(apk_path):
    if not os.path.isfile(apk_path):
        return None, None
    try:
        apk = APK(apk_path)
        code = int(apk.version_code)
        name = apk.version_name
        return code, name
    except Exception as e:
        print(f"{apk_path}: {e}")
        return None, None


def find_latest_apk(apk_dir):
    if not os.path.isdir(apk_dir):
        return None, None, None

    latest_code = -1
    latest_name = None
    latest_path = None

    for file in os.listdir(apk_dir):
        if not file.lower().endswith(".apk"):
            continue
        file_path = os.path.join(apk_dir, file)
        code, name = get_apk_info(file_path)
        if code is not None and code > latest_code:
            latest_code = code
            latest_name = name
            latest_path = file_path

    if latest_code == -1:
        return None, None, None
    return latest_code, latest_name, latest_path