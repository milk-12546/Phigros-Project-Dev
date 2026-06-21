import re
import json


class Fix:
    def __init__(self, str_name: str):
        self.str_name = str_name
        with open("./utils/fix_str.json", "r", encoding="utf-8") as f:
            self.mapping = json.load(f)

    def file_name(self, name: str):
        mapping = self.mapping["fileError"]

        pattern = r':\s| \?\s|[\\/:*?"<>|]'
        def replace_func(match):
            matched_str = match.group(0)
            return mapping.get(matched_str, matched_str)

        return re.sub(pattern, replace_func, name)

    def song_name(self):
        mapping = self.mapping["songName"]
        if self.str_name in mapping:
            return mapping[self.str_name]
        else:
            return None

    def chart(self, level):
        mapping = self.mapping["charter"]
        if self.str_name in mapping:
            return mapping[self.str_name][level]
        else:
            return None