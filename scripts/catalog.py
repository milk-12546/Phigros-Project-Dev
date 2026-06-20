import base64
import json
from typing import Dict, List, Union


def parser(catalog_path: str) -> Dict[str, str]:
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    key_data = base64.b64decode(data["m_KeyDataString"])
    bucket_data = base64.b64decode(data["m_BucketDataString"])
    entry_data = base64.b64decode(data["m_EntryDataString"])

    def read_int(offset: int) -> int:
        return int.from_bytes(bucket_data[offset:offset + 4], 'little')

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

    result = {}
    for key, bundle in temp_table:
        if isinstance(key, int):
            continue
        if key.startswith("Assets/Tracks/"):
            key = key[14:]
            result[key] = bundle
        elif key.startswith("TrackFile/") or key.startswith("avatar."):
            result[key] = bundle

    return result