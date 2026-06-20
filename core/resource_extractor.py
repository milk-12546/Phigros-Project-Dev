import json

from zipfile import ZipFile
from scripts import catalog
from core import get_game_info


class APK:
    def __init__(self, apk_path):
        self.apk_src = ZipFile(apk_path)

    def catalog(self):
        with self.apk_src.open("assets/aa/catalog.json") as c:
            catalog.parser(json.load(c))

    def info(self):
        with self.apk_src.open("assets/bin/Data/globalgamemanagers.assets") as g:
            with self.apk_src.open("assets/bin/Data/level0") as l:
                with open("./scripts/typetree.json") as t:
                    get_game_info.parser(g.read(), l.read(), json.load(t))

    def bundle(self, value):
        file = self.apk_src.open("assets/aa/Android/%s" % value)
        try:
            return file
        finally:
            file.close()

    def close(self):
        self.apk_src.close()