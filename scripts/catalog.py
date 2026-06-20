import base64
import json
import os

from typing import List, Union


def parser(data) -> str:
    key_data = base64.b64decode(data["m_KeyDataString"])
    bucket_data = base64.b64decode(data["m_BucketDataString"])
    entry_data = base64.b64decode(data["m_EntryDataString"])

    def read_int(offset: int) -> int:
        return int.from_bytes(bucket_data[offset: offset + 4], 'little')

    temp_table: List[List[Union[int, str, None]]] = []
    pos = 0
    num_keys = read_int(pos)
    pos += 4

    for _ in range(num_keys):
        key_pos = read_int(pos)
        pos += 4
        key_type = key_data[key_pos]
        key_pos += 1

        if key_type == 0:
            length = key_data[key_pos]
            key_pos += 4
            key_value = key_data[key_pos:key_pos + length].decode('ascii')
        elif key_type == 1:
            length = key_data[key_pos]
            key_pos += 4
            key_value = key_data[key_pos:key_pos + length].decode('utf-16')
        elif key_type == 4:
            key_value = key_data[key_pos]
        else:
            raise ValueError(f"未知的 key 类型: {key_type}")

        num_entries = read_int(pos)
        pos += 4
        last_entry_idx = None
        for _ in range(num_entries):
            entry_idx = read_int(pos)
            pos += 4
            entry_start = 4 + 28 * entry_idx
            entry_block = entry_data[entry_start:entry_start + 28]
            ref_value = int.from_bytes(entry_block[8:10], 'little')
            last_entry_idx = ref_value

        temp_table.append([key_value, last_entry_idx])

    for i in range(len(temp_table)):
        ref = temp_table[i][1]
        if isinstance(ref, int) and ref != 65535:
            temp_table[i][1] = temp_table[ref][0]

    temp = {}
    for key, bundle in temp_table:
        if isinstance(key, int):
            continue
        if key.startswith("Assets/Tracks/"):
            key = key[14:]
            temp[key] = bundle
        elif key.startswith("TrackFile/") or key.startswith("avatar."):
            temp[key] = bundle

    result = {}
    for key in temp:
        if key.startswith("avatar.") or key.startswith("#ChapterCover"):
            continue
        bundle = temp[key]
        song_id, file = os.path.split(key)
        if song_id not in result:
            result[song_id] = {}
        file_name = os.path.splitext(file)[0]
        result[song_id][file_name] = bundle

    mapping = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=4)

    with open("./temp/bundle_mapping.json", "w", encoding="utf-8") as f:
        f.write(mapping)
    return mapping