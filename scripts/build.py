import json
import os

from utils import fix_str as s


class Build:
    def __init__(self, temp_dir, output_dir, bundle_map, apk_ver):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.bundle_map = bundle_map
        self.apk_ver = apk_ver

    def avatar(self):
        print("\n[build.avatar]   ========== 正在建立头像资源信息映射 ==========")
        avatars_bundle = self.bundle_map["avatars"]
        with open(os.path.join(self.temp_dir, "key_avatar_name.json"), "r", encoding="utf-8") as f:
            avatar_dict = json.load(f)
            print(f"    [Info]    [build.avatar]: \033[36m\"{os.path.join(self.temp_dir, "key_avatar_name.json")}\"\033[0m 已加载")
        print()
        with open(os.path.join(self.output_dir, r".\info\avatar.tsv"), "w", newline="", encoding="utf-8") as tsv:
            tsv.write("key\tname\tbundle\n")
            for avatar in avatars_bundle:
                #print(f"    \033[34m[Debug]\033[0m   [avatar.name]:  正在处理 \033[36m\"{avatar}\"\033[0m 的命名")
                if avatar in avatar_dict:
                    avatar_name = avatar_dict[avatar]
                    print(f"    [Info]    [avatar.name]: \033[36m\"{avatar}\"\033[0m 命名映射为 \033[36m\"{avatar_name}\"\033[0m")
                else:
                    print(f"    \033[33m[Warning]\033[0m [avatar.name]: \033[36m\"{avatar}\"\033[0m 无对应头像命名，将使用默认文件名")
                    avatar_name = avatar
                tsv.write(f"{avatar}\t{avatar_name}\t{avatars_bundle[avatar]}\n")
            print(f"    \033[32m[Save]\033[0m    [avatar.build]: 头像索引已保存至 \033[36m\"{os.path.join(self.output_dir, r".\info\avatar.tsv")}\"\033[0m")

    def cover(self):
        print("\n[build.cover]    ========== 正在建立章节封面资源信息索引 ==========")
        covers_bundle = self.bundle_map["covers"]
        with open(os.path.join(self.temp_dir, "chapters_name.json"), "r", encoding="utf-8") as f:
            cover_dict = json.load(f)
            print(f"    [Info]    [build.cover]: \033[36m\"{os.path.join(self.temp_dir, "chapters_name.json")}\"\033[0m 已加载")
        print()
        with open(os.path.join(self.output_dir, r".\info\cover.tsv"), "w", newline="", encoding="utf-8") as tsv:
            tsv.write("name\tinstalled\tcover_bundle\tcoverBlur_bundle\n")
            cover_name = ""
            d = {"temp":[],"bundle":{},"installed":[]}
            for cover in covers_bundle:
                #print(f"    \033[34m[Debug]\033[0m   [cover.name]:  正在处理 \033[36m\"{cover}\"\033[0m 的命名")
                blur = False
                if cover.endswith("Blur"):
                    cover_fix_name = cover[:-4]
                    blur = True
                elif cover.endswith("BlurS"):
                    cover_fix_name = cover[:-5] + "S"
                    blur = True
                else:
                    cover_fix_name = cover
                for cover_id in cover_dict:
                    if cover_fix_name.startswith(cover_id):
                        d["temp"].append(cover)
                        if cover_fix_name.replace(cover_id, ""):
                            if not cover_fix_name[len(cover_id):].startswith("_"):
                                cover_fix_name = f"{cover_fix_name[:len(cover_id)]} {cover_fix_name[len(cover_id):]}"
                        cover_name = cover_fix_name.replace(cover_id, cover_dict[cover_id])
                        break
                if cover in d["temp"]:
                    d["bundle"].setdefault(cover_name, {"origin":"","blur":""})
                    if blur:
                        d["bundle"][cover_name]["blur"] = covers_bundle[cover]
                    else:
                        d["bundle"][cover_name]["origin"] = covers_bundle[cover]
                    print(f"    [Info]    [cover.name]: \033[36m\"{cover}\"\033[0m 命名映射为 \033[36m\"{cover_name}\"\033[0m")
                else:
                    print(f"    \033[33m[Warning]\033[0m [cover.name]: \033[36m\"{cover}\"\033[0m 无对应章节命名，将使用默认文件名")
                    d["bundle"].setdefault(cover_fix_name, {"origin":"","blur":""})
                    if blur:
                        d["bundle"][cover_fix_name]["blur"] = covers_bundle[cover]
                    else:
                        d["bundle"][cover_fix_name]["origin"] = covers_bundle[cover]
                if cover in cover_dict:
                    d["installed"].append(cover_name)
            for cover_name in d["bundle"]:
                i = ""
                if cover_name in d["installed"]:
                    i = True
                tsv.write(f"{cover_name}\t{i}\t{d["bundle"][cover_name]["origin"]}\t{d["bundle"][cover_name]["blur"]}\n")
            print(f"    \033[32m[Save]\033[0m    [cover.build]: 章节封面索引已保存至 \033[36m\"{os.path.join(self.output_dir, r".\info\cover.tsv")}\"\033[0m")

    def song(self):
        print("\n[build.song]     ========== 正在建立歌曲资源信息映射 ==========")
        songs_bundle = self.bundle_map["songs"]
        with open(os.path.join(self.temp_dir, "song_info.json"), "r", encoding="utf-8") as f:
            songs_info = json.load(f)
            print(f"    [Info]    [build.song]: \033[36m\"{os.path.join(self.temp_dir, "song_info.json")}\"\033[0m 已加载")
        with open(os.path.join(self.temp_dir, "chapters.json"), "r", encoding="utf-8") as f:
            chapters = json.load(f)
            print(f"    [Info]    [build.song]: \033[36m\"{os.path.join(self.temp_dir, "chapters.json")}\"\033[0m 已加载")
        with open(os.path.join(self.temp_dir, "level_mapping.json"), "r", encoding="utf-8") as f:
            levels = json.load(f)
            print(f"    [Info]    [build.song]: \033[36m\"{os.path.join(self.temp_dir, "level_mapping.json")}\"\033[0m 已加载")
        print()
        with open(os.path.join(self.output_dir, r".\info\song.tsv"), "w", newline="", encoding="utf-8") as tsv:
            tsv.write(
                "key\tname\tchapter\tcomposer\tillustrator\t"
                "difficultyEZ\tdifficultyHD\tdifficultyIN\tdifficultyAT\tdifficultyLegacy\t"
                "charterEZ\tcharterHD\tcharterIN\tcharterAT\tcharterLegacy\t"
                "previewStart\tpreviewEnd\tdifferentMusic\tdifferentCover\t"
                "music_bundle\till_bundle\tillBlur_bundle\tillLowRes_bundle\t"
                "chartEZ_bundle\tchartHD_bundle\tchartIN_bundle\tchartAT_bundle\tchartLegacy_bundle\t"
                "nonRegular\tisSP\t#\n"
            )

            def template(
                    key, song_name="", chapter="", song_composer="", song_illustrator="",
                    diff_ez="", diff_hd="", diff_in="", diff_at="", diff_legacy="",
                    charter_ez="", charter_hd="", charter_in="", charter_at="", charter_legacy="",
                    preview_start="", preview_end="", different_music="", different_cover="",
                    music_bundle="", ill_bundle="", ill_blur_bundle="", ill_low_res_bundle="",
                    ez_bundle="", hd_bundle="", in_bundle="", at_bundle="", legacy_bundle="",
                    non_regular="", sp="", num=""
            ):
                song_info = songs_info[key]
                song_bundle = songs_bundle[key]

                if chapter == "":
                    for banner in chapters:
                        if song_id in chapters[banner]: chapter = banner

                if song_name == "": song_name = song_info["songName"]
                if song_composer == "": song_composer = song_info["composer"]
                if song_illustrator == "": song_illustrator = song_info["illustrator"]
                if preview_start == "": preview_start = song_info["previewTime"]
                if preview_end == "": preview_end = song_info["previewEndTime"]

                if music_bundle == "": music_bundle = song_bundle["music"]
                if ill_bundle == "": ill_bundle = song_bundle["music"]
                if ill_blur_bundle == "": ill_blur_bundle = song_bundle["IllustrationBlur"]
                if ill_low_res_bundle == "": ill_low_res_bundle = song_bundle["IllustrationLowRes"]

                if key in levels["nonRegular"]:
                    non_regular = levels["nonRegular"][key]
                if "EZ" not in non_regular:
                    if ez_bundle == "": ez_bundle = song_bundle["Chart_EZ"]
                    if "EZ" in song_info["levelInfo"]:
                        if diff_ez == "": diff_ez = song_info["levelInfo"]["EZ"][0]
                        if charter_ez == "": charter_ez = song_info["levelInfo"]["EZ"][1]
                if "HD" not in non_regular:
                    if hd_bundle == "": hd_bundle = song_bundle["Chart_HD"]
                    if "HD" in song_info["levelInfo"]:
                        if diff_hd == "": diff_hd = song_info["levelInfo"]["HD"][0]
                        if charter_hd == "": charter_hd = song_info["levelInfo"]["HD"][1]
                if "IN" not in non_regular:
                    if in_bundle == "": in_bundle = song_bundle["Chart_IN"]
                    if "IN" in song_info["levelInfo"]:
                        if diff_in == "": diff_in = song_info["levelInfo"]["IN"][0]
                        if charter_in == "": charter_in = song_info["levelInfo"]["IN"][1]

                if song_id in levels["AT"] or key in levels["AT"]:
                    if at_bundle == "": at_bundle = song_bundle["Chart_AT"]
                    if "AT" in song_info["levelInfo"]:
                        if diff_at == "": diff_at = song_info["levelInfo"]["AT"][0]
                        if charter_at == "": charter_at = song_info["levelInfo"]["AT"][1]

                if song_id in levels["Legacy"] or key in levels["Legacy"]:
                    if legacy_bundle == "": legacy_bundle = song_bundle["Chart_Legacy"]
                    if "Legacy" in song_info["levelInfo"]:
                        if diff_legacy == "": diff_legacy = song_info["levelInfo"]["Legacy"][0]
                        if charter_legacy == "": charter_legacy = song_info["levelInfo"]["Legacy"][1]

                if different_music == "":
                    if song_info["hasDifferentMusic"]:
                        j = {}
                        for i in song_bundle:
                            if i.startswith("music_"):
                                j[i.replace("music_", "")] = song_bundle[i]
                        different_music = j

                if different_cover == "":
                    if song_info["hasDifferentCover"]:
                        j = {}
                        for i in song_bundle:
                            if i.startswith("Illustration_"):
                                j[f"{i.replace("Illustration_")}"] = "origin"
                                j[f"{i.replace("Illustration_")}"]["origin"] = song_bundle[i]
                            elif i.startswith("IllustrationBlur_"):
                                j[f"{i.replace("IllustrationBlur_")}"] = "blur"
                                j[f"{i.replace("IllustrationBlur_")}"]["blur"] = song_bundle[i]
                            elif i.startswith("IllustrationLowRes_"):
                                j[f"{i.replace("IllustrationLowRes_")}"] = "low_res"
                                j[f"{i.replace("IllustrationLowRes_")}"]["low_res"] = song_bundle[i]
                        different_cover = j

                if sp == "":
                    if not ez_bundle and not hd_bundle and in_bundle and not at_bundle:
                        sp = True

                if song_id in songs_info:
                    num = list(songs_info.keys()).index(song_id) + 1

                tsv.write(
                    f"{song_id}\t{song_name}\t{chapter}\t{song_composer}\t{song_illustrator}\t"
                    f"{diff_ez}\t{diff_hd}\t{diff_in}\t{diff_at}\t{diff_legacy}\t"
                    f"{charter_ez}\t{charter_hd}\t{charter_in}\t{charter_at}\t{charter_legacy}\t"
                    f"{preview_start}\t{preview_end}\t{different_music}\t{different_cover}\t"
                    f"{music_bundle}\t{ill_bundle}\t{ill_blur_bundle}\t{ill_low_res_bundle}\t"
                    f"{ez_bundle}\t{hd_bundle}\t{in_bundle}\t{at_bundle}\t{legacy_bundle}\t"
                    f"{non_regular}\t{sp}\t{num}\n"
                )

            for song_id in songs_bundle:
                #print(f"    \033[34m[Debug]\033[0m   [song.build]:  正在为 \033[36m\"{song_id}\"\033[0m 建立索引")
                song_names = s.Fix(song_id).song_name()
                if song_names:
                    if song_id in songs_info:
                        template(song_id, song_name=song_names)
                        continue
                    elif f"{song_id[:-1]}0" in songs_info:
                        template(f"{song_id[:-1]}0", song_name=song_names)
                        continue
                    else:
                        print(song_id)
                        continue
                else:
                    if song_id in songs_info:
                        template(song_id)
                    else:
                        print(song_id)
                        continue
            print(f"    \033[32m[Save]\033[0m    [song.build]: 歌曲索引已保存至 \033[36m\"{os.path.join(self.output_dir, r".\info\song.tsv")}\"\033[0m")