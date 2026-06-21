import json
import hashlib

from utils import dxf


def txt(path, level, mus, ill, chart, data):
    return (
        f"#\n"
        f"Path: 125460{str(path)[:16]}\n"
        f"Name: {data["songName"]}\n"
        f"Song: {mus}\n"
        f"Picture: {ill}\n"
        f"Chart: {chart}\n"
        f"Level: {level} Lv.{int(dxf.f2d(data["levelInfo"][level][0], 0))}\n"
        f"Composer: {data["composer"]}\n"
        f"Illustrator: {data["illustrator"]}\n"
        f"Charter: {data["levelInfo"][level][1]}"
    )

def yml(level, data):
    return (
        f"name: \"{data["songName"]}\",\n"
        f"composer: \"{data["composer"]}\",\n"
        f"illustrator: \"{data["illustrator"]}\",\n"
        f"level: \"{level} Lv.{int(dxf.f2d(data["levelInfo"][level][0], 0))}\",\n"
        f"difficulty: {dxf.f2d(data["levelInfo"][level][0], 1)},\n"
        f"charter: \"{data["levelInfo"][level][1]}\",\n"
        "tip: \"Tips: 打包来至milk_12546\""
    )

def info(song_id, level, mus, ill, chart):
    with open(r"C:\Users\ml354\OneDrive\文档\Phigros-Project-Dev\temp\song_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)[song_id]
    return txt(int.from_bytes(hashlib.sha256(song_id.encode("utf-8")).digest()[:8], byteorder="big"), level, mus, ill, chart, data), yml(level, data)