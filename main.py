import os

from core import taptap, resource_extractor as extract
from scripts import build


# ========== 获取APK信息 ========== #
apk_path, apk_ver, spec_ver = taptap.TapTapClient().get_apk("com.PigeonGames.Phigros-151.apk")

# ========== 检查上次版本 ========== #
need_update = False
os.makedirs("./output/info", exist_ok=True)
f = os.open("./output/info/info_ver.txt", os.O_RDWR | os.O_CREAT)
info_ver = os.read(f, 256).decode("utf-8")
if info_ver and os.path.exists("./temp"):
    if spec_ver:
        if apk_ver != info_ver:
            need_update = True
    else:
        if apk_ver != info_ver:
            need_update = True
else:
    need_update = True

#手动更新资源（临时调试）
need_update = True
# ========== 资源信息加载 ========== #
if need_update:
    #确保目录存在
    os.makedirs("./temp", exist_ok=True)

    #提取游戏信息
    apk = extract.APK(apk_path)
    apk.info()

    #游戏资源映射
    mapping = apk.catalog()

    #游戏信息整理
    build_info = build.Build("./temp", "./output", mapping, apk_ver)
    build_info.avatar()
    build_info.cover()
    build_info.song()

    #关闭文件
    apk.close()

    #记录本次版本
    os.ftruncate(f, 0)
    os.lseek(f, 0, os.SEEK_SET)
    os.write(f, apk_ver.encode("utf-8"))
else:
    pass

# ========== 资源提取流程 ========== #

# ========== 关闭文件 ========== #
os.close(f)