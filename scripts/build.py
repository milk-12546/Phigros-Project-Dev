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
        avatars_bundle = self.bundle_map["avatars"]
        with open(os.path.join(self.temp_dir, "key_avatar_name.json"), "r", encoding="utf-8") as f:
            avatar_dict = json.load(f)
        with open(os.path.join(self.output_dir, "./info/avatar.tsv"), "w", newline="", encoding="utf-8") as tsv:
            tsv.write("key\tname\tbundle\n")
            for avatar in avatars_bundle:
                if avatar in avatar_dict:
                    avatar_name = avatar_dict[avatar]
                else:
                    print(f"\033[33m[头像资源索引] Warning:\033[0m \"{avatar}\" 未实装 或 信息缺失，将使用默认文件名")
                    avatar_name = avatar
                tsv.write(f"{avatar}\t{avatar_name}\t{avatars_bundle[avatar]}\n")

    def cover(self):
        covers_bundle = self.bundle_map["covers"]
        with open(os.path.join(self.temp_dir, "chapters_name.json"), "r", encoding="utf-8") as f:
            cover_dict = json.load(f)
        with open(os.path.join(self.output_dir, "./info/cover.tsv"), "w", newline="", encoding="utf-8") as tsv:
            tsv.write("key\tname\tbundle\n")
            for cover in covers_bundle:
                cover_name = None
                for cover_id in cover_dict:
                    if cover_id in cover:
                        cover_name = f"{cover.replace(cover_id, f"{cover_dict[cover_id]} (")})".replace(" ()", "")
                        break
                if not cover_name:
                    print(f"\033[33m[章节封面索引] Warning:\033[0m \"{cover}\" 无章节名字，将使用默认文件名")
                    cover_name = cover
                tsv.write(f"{cover}\t{cover_name}\t{covers_bundle[cover]}\n")

    def song(self):
        songs_bundle = self.bundle_map["songs"]
        with open(os.path.join(self.temp_dir, "song_info.json"), "r", encoding="utf-8") as f:
            songs_info = json.load(f)
        with open(os.path.join(self.temp_dir, "chapters.json"), "r", encoding="utf-8") as f:
            chapters = json.load(f)
        with open(os.path.join(self.temp_dir, "diff_mapping.json"), "r", encoding="utf-8") as f:
            difficulties = json.load(f)
        with open(os.path.join(self.output_dir, "./info/song.tsv"), "w", newline="", encoding="utf-8") as tsv:
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

                if non_regular == "":
                    if key in difficulties["nonRegular"]:
                        non_regular = difficulties["nonRegular"][key]
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

                if song_id in difficulties["AT"] or key in difficulties["AT"]:
                    if at_bundle == "": at_bundle = song_bundle["Chart_AT"]
                    if "AT" in song_info["levelInfo"]:
                        if diff_at == "": diff_at = song_info["levelInfo"]["AT"][0]
                        if charter_at == "": charter_at = song_info["levelInfo"]["AT"][1]

                if song_id in difficulties["Legacy"] or key in difficulties["Legacy"]:
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