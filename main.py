from core import taptap, resource_extractor as extract, get_game_info as game_info


#获取APK
apk_path, apk_ver = taptap.TapTapClient().get_apk("com.PigeonGames.Phigros-151.apk")
apk = extract.APK(apk_path)

#提取游戏信息
apk.info()

#游戏资源映射
mapping = apk.catalog()

#游戏信息整理

#关闭APK文件
apk.close()