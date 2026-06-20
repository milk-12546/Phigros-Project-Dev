import json

from UnityPy import Environment
from utils import dxf


def parser(g, l, t):
    env = Environment()
    env.load_file(g, name="assets/bin/Data/globalgamemanagers.assets")
    env.load_file(l)
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()

        #歌曲相关信息
        if data.m_Script.get_obj().read().name == "GameInformation":
            gameInformation = obj.read_typetree(t["GameInformation"])

            #章节分类（歌曲 + 章节封面命名）
            chapter_data = {}
            chapters_name = {}
            for chapters in gameInformation["chapters"]:
                chapter_code = chapters["chapterCode"]
                chapter_name = chapters["songInfo"]["banner"]
                chapter_data.setdefault(chapter_name, [])
                for song in chapters["songInfo"]["songs"]:
                    song_id = song["songsId"]
                    chapter_data[chapter_name].append(song_id)
                #章节封面命名映射
                chapters_name[chapter_code] = chapter_name
                with open("./temp/chapters_name.json", "w", encoding="utf-8") as f:
                    json.dump(chapters_name, f, ensure_ascii=False, indent=4)
            #歌曲章节分类
            with open("./temp/chapters.json", "w", encoding="utf-8") as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=4)

            #歌曲信息（包含难度分类）
            song_info = {}
            special_level = {
                "AT": [],
                "Legacy": [],
                "nonRegular": {}
            }
            for key, songs in gameInformation["song"].items():
                for song in songs:
                    song_id = song["songsId"]
                    song_diff = {
                        level: [dxf.d2f(diff), charter]
                        for level, diff, charter in zip(song["levels"], song["difficulty"], song["charter"])
                        if diff > 0
                    }
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
            #难度分类
            with open("./temp/diff_mapping.json", "w", encoding="utf-8") as f:
                json.dump(special_level, f, ensure_ascii=False, indent=4)
            #歌曲信息
            with open("./temp/song_info.json", "w", encoding="utf-8") as f:
                json.dump(song_info, f, ensure_ascii=False, indent=4)