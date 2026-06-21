import os

from core import taptap, resource_extractor as extract


#获取APK信息
apk_path, apk_ver, spec_ver = taptap.TapTapClient().get_apk("com.PigeonGames.Phigros-151.apk")

#检查上次版本
need_update = False
f = os.open("./temp/last.txt", os.O_RDWR | os.O_CREAT)
#last = os.read(f, 256).decode("utf-8")
last = "0"
if last and os.path.exists("./temp"):
    if spec_ver:
        if apk_ver != last:
            need_update = True
    else:
        if apk_ver != last:
            need_update = True
else:
    need_update = True

#如果需要更新资源
if need_update:
    #确保缓存目录存在
    os.makedirs("./temp", exist_ok=True)

    #提取游戏信息
    apk = extract.APK(apk_path)
    apk.info()

    #游戏资源映射
    mapping = apk.catalog()

    #游戏信息整理

    #关闭文件
    apk.close()

    #记录本次版本
    os.ftruncate(f, 0)
    os.lseek(f, 0, os.SEEK_SET)
    os.write(f, apk_ver.encode("utf-8"))

#资源提取流程

#关闭文件
os.close(f)