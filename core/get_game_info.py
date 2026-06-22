import json
import os.path

from UnityPy import Environment
from utils import dxf


def parser(g, l, t, temp_dir):
    print()
    #print("\033[34m[Debug]\033[0m   [get]: 准备提取游戏信息")
    env = Environment()
    env.load_file(g, name=r"assets\bin\Data\globalgamemanagers.assets")
    print("[Info]    [get]: \033[36m\"globalgamemanagers.assets\"\033[0m 已载入")
    env.load_file(l)
    print("[Info]    [get]: \033[36m\"level0\"\033[0m 已载入")
    game_information = None
    collections = None
    tips = None
    print()
    #print("\n\033[34m[Debug]\033[0m   [get]: 正在处理 \033[36m\"globalgamemanagers.assets\"\033[0m 和 \033[36m\"level0\"\033[0m")
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        #歌曲相关信息
        if data.m_Script.get_obj().read().name == "GameInformation":
            game_information = obj.read_typetree(t["GameInformation"])
            print("[Info]    [get]: \033[36m\"GameInformation\"\033[0m 已加载")
        #文件+头像 名字映射
        elif data.m_Script.get_obj().read().name == "GetCollectionControl":
            collections = obj.read_typetree(t["GetCollectionControl"], True)
            print("[Info]    [get]: \033[36m\"GetCollectionControl\"\033[0m 已加载")
        #Tips文本
        elif data.m_Script.get_obj().read().name == "TipsProvider":
            tips = obj.read_typetree(t["TipsProvider"], True)
            print("[Info]    [get]: \033[36m\"TipsProvider\"\033[0m 已加载")
    if not game_information:
        print("\033[31m[Error]\033[0m   [get]: \033[36m\"GameInformation\"\033[0m 加载失败")
    if not collections:
        print("\033[31m[Error]\033[0m   [get]: \033[36m\"GetCollectionControl\"\033[0m 加载失败")
    if not tips:
        print("\033[31m[Error]\033[0m   [get]: \033[36m\"TipsProvider\"\033[0m 加载失败")

# ========== GameInformation ========== #
    #章节分类（歌曲 + 章节封面命名）
    print("\n[get.chapter]    ========== 正在提取歌曲所属章节分类 ==========")
    chapter_data = {}
    chapters_name = {}
    for chapters in game_information["chapters"]:
        chapter_code = chapters["chapterCode"]
        chapter_name = chapters["songInfo"]["banner"]
        chapter_data.setdefault(chapter_name, [])
        for song in chapters["songInfo"]["songs"]:
            song_id = song["songsId"]
            chapter_data[chapter_name].append(song_id)
            print(f"    [Info]    [chapter.song]: \033[36m\"{song_id}\"\033[0m 归类为 \033[36m\"{chapter_name}\"\033[0m 章节")
        #章节封面命名映射
        chapters_name[chapter_code] = chapter_name
        print(f"    [Info]    [chapter.name]: \033[36m\"{chapter_code}\"\033[0m 命名映射为 \033[36m\"{chapter_name}\"\033[0m")
        with open(os.path.join(temp_dir, "chapters_name.json"), "w", encoding="utf-8") as f:
            json.dump(chapters_name, f, ensure_ascii=False, indent=4)
            print(f"    \033[32m[Save]\033[0m    [chapter.song]: \033[36m\"{chapter_name}\"\033[0m 章节的歌曲已添加至 \033[36m\"{os.path.join(temp_dir, "chapters_name.json")}\"\033[0m\n")
    #歌曲章节分类
    with open(os.path.join(temp_dir, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [chapter.name]: 章节命名已保存至 \033[36m\"{os.path.join(temp_dir, "chapters.json")}\"\033[0m")

    #歌曲信息（包含难度分类）
    print("\n[get.song]       ========== 正在提取歌曲信息 ==========")
    song_info = {}
    special_level = {
        "AT": [],
        "Legacy": [],
        "nonRegular": {}
    }
    for key, songs in game_information["song"].items():
        for song in songs:
            song_id = song["songsId"]
            #print(f"    \033[34m[Debug]\033[0m   [song.info]:  正在处理 \033[36m\"{song_id}\"\033[0m 的信息")
            song_diff = {
                level: [dxf.d2f(diff), charter]
                for level, diff, charter in zip(song["levels"], song["difficulty"], song["charter"])
                if diff > 0
            }
            color = {
                "EZ": "\033[32m[EZ]\033[0m",
                "HD": "\033[36m[HD]\033[0m",
                "IN": "\033[31m[IN]\033[0m",
                "AT": "[AT]",
                "Legacy": "[Legacy]"
            }
            space = " " * (28 - (len(song_diff) * 4 + (len(song_diff) - 1) if song_diff else 0))
            color_str = " ".join([color.get(d, f"\033[36m[{d}]\033[0m") for d in song_diff]) + space
            if "[Legacy]" in color_str:
                color_str = color_str.replace("[Legacy]    ", "[Legacy]")
                if "[AT]" not in color_str:
                    color_str = color_str.replace("[Legacy]     ", "     [Legacy]")
            print(f"    [Info]    [song.level]: {color_str} \033[36m\"{song_id}\"\033[0m 有 \033[36m{len(song_diff)}\033[0m 个难度")
            #难度过滤
            if "AT" in song_diff:
                special_level["AT"].append(song_id)
            if "Legacy" in song_diff:
                special_level["Legacy"].append(song_id)
            if "EZ" not in song_diff or "HD" not in song_diff or "IN" not in song_diff:
                if song_id not in special_level["nonRegular"]:
                    special_level["nonRegular"][song_id] = []
                if "EZ" not in song_diff:
                    special_level["nonRegular"][song_id].append("EZ")
                if "HD" not in song_diff:
                    special_level["nonRegular"][song_id].append("HD")
                if "IN" not in song_diff:
                    special_level["nonRegular"][song_id].append("IN")
            #歌曲信息
            song_info[song_id] = {
                "songName": song["songsName"],
                "composer": song["composer"],
                "illustrator": song["illustrator"],
                "levelInfo": song_diff,
                "previewTime": round(song["previewTime"], 4),
                "previewEndTime": round(song["previewEndTime"], 4),
                "hasDifferentMusic": song["hasDifferentMusic"],
                "hasDifferentCover": song["hasDifferentCover"]
            }
    #歌曲信息
    with open(os.path.join(temp_dir, "song_info.json"), "w", encoding="utf-8") as f:
        json.dump(song_info, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [song.info]:  歌曲信息已保存至 \033[36m\"{os.path.join(temp_dir, "song_info.json")}\"\033[0m")
    #难度分类
    with open(os.path.join(temp_dir, "level_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(special_level, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [song.level]: 难度分类已保存至 \033[36m\"{os.path.join(temp_dir, "level_mapping.json")}\"\033[0m")

    #单曲+文件+曲绘+头像
    print("\n[get.key]        ========== 正在提取键名分类 ==========")
    keys = {
        "single": [],
        "collection": {},
        "illustration": [],
        "avatar": []
    }
    for key in game_information["keyStore"]:
        #print(f"    \033[34m[Debug]\033[0m   [key.info]:  正在处理 \033[36m\"{key["keyName"]}\"\033[0m 的分类")
        if key["kindOfKey"] == 0:
            keys["single"].append(key["keyName"])
            print(f"    [Info]    [key.single]: \033[36m\"{key["keyName"]}\"\033[0m 归类为 \033[36m\"单曲\"\033[0m")
        if key["kindOfKey"] == 1:
            keys["collection"][key["keyName"]] = key["unlockTimes"]
            print(f"    [Info]    [key.collection]: \033[36m\"{key["keyName"]}\"\033[0m 归类为 \033[36m\"收藏品\"\033[0m ，共有 \033[36m{key["unlockTimes"]}\033[0m 个")
        if key["kindOfKey"] == 2:
            keys["illustration"].append(key["keyName"])
            print(f"    [Info]    [key.illustration]: \033[36m\"{key["keyName"]}\"\033[0m 归类为 \033[36m\"曲绘\"\033[0m")
        if key["kindOfKey"] == 3:
            keys["avatar"].append(key["keyName"])
            print(f"    [Info]    [key.avatar]: \033[36m\"{key["keyName"]}\"\033[0m 归类为 \033[36m\"头像\"\033[0m")
    with open(os.path.join(temp_dir, "keys.json"), "w", encoding="utf-8") as f:
        json.dump(keys, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [key.info]: 键名分类已保存至 \033[36m\"{os.path.join(temp_dir, "keys.json")}\"\033[0m")


# ========== GetCollectionControl ========== #
    #收藏品命名映射
    print("\n[get.name]       ========== 正在提取命名映射 ==========")
    items = {}
    files = {}
    for item in collections.collectionItems:
        if item.key in items:
            items[item.key][1] = item.subIndex
        else:
            items[item.key] = [item.multiLanguageTitle.chinese, item.subIndex]
    for key in items:
        files[key] = items[key][0]
        print(f"    [Info]    [collection.name]: \033[36m\"{key}\"\033[0m 命名映射为 \033[36m\"{items[key][0]}\"\033[0m")
    with open(os.path.join(temp_dir, "key_collection_name.json"), "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [collection.name]: 收藏品命名已保存至 \033[36m\"{os.path.join(temp_dir, "key_collection_name.json")}\"\033[0m\n")

    #头像命名映射
    avatars = {}
    for item in collections.avatars:
        avatars[item.addressableKey[7:]] = item.name
        print(f"    [Info]    [avatar.name]: \033[36m\"{avatars[item.addressableKey[7:]]}\"\033[0m 命名映射为 \033[36m\"{item.name}\"\033[0m")
    with open(os.path.join(temp_dir, "key_avatar_name.json"), "w", encoding="utf-8") as f:
        json.dump(avatars, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [avatar.name]: 头像命名已保存至 \033[36m\"{os.path.join(temp_dir, "key_avatar_name.json")}\"\033[0m")


# ========== TipsProvider ========== #
    #Tips文本
    print("\n[get.tip]        ========== 正在提取提示文本 ==========")
    with open(os.path.join(temp_dir, "tips.json"), "w", encoding="utf-8") as f:
        json.dump(tips.tips[0].tips, f, ensure_ascii=False, indent=4)
        print(f"    \033[32m[Save]\033[0m    [tip.text]: 提示文本已保存至 \033[36m\"{os.path.join(temp_dir, "tips.json")}\"\033[0m")