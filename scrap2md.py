import json
import os
import argparse
import datetime
import dataclasses
from enum import Enum

"""
ScrapboxからエクスポートしたJSONファイルを複数のマークダウンファイルに変換します。
"""

class JsonPathNotFoundException(Exception):
    def __init__(self, jsonpath=None):
        if jsonpath==None:
            super().__init__("Invalid JSON")
        else:
            super().__init__(f"The element '{jsonpath}' is not found in the JSON file")

class LinePartType(Enum):
    PLAIN = 1,
    BRACKET = 2,

@dataclasses.dataclass
class LinePart:
    ty: LinePartType
    # 内容。ty==LinePartType.BRACKETの場合、'[' ']'を含まない。
    # 例えば"[aaa]"ならtext=="aaa"、"[* bbb]"ならtext=="* bbb"
    text: str


JST = datetime.timezone(datetime.timedelta(hours=9))
UTC = datetime.timezone.utc

def split_lines_into_parts(line: str) -> list[LinePart]:
    in_bracket: bool = False
    index: int = 0
    length: int = len(line)
    parts: list[LinePart] = []
    part_begin: int = 0

    while index < length:
        # ブラケットの中に入ったとき
        if line[index] == '[' and not in_bracket:
            # ブラケット外の内容をpartsに追加
            part_str = line[part_begin:index]
            parts.append(LinePart(ty=LinePartType.PLAIN, text=part_str))
            # ブラケット内を読み取る準備
            in_bracket = True
            part_begin = index+1
        # ブラケットの外に出たとき
        elif line[index] == ']' and in_bracket:
            # ブラケット内の内容をpartsに追加
            part_str = line[part_begin:index]
            parts.append(LinePart(ty=LinePartType.BRACKET, text=part_str))
            # ブラケット外を読み取る準備
            in_bracket = False
            part_begin = index+1
        index += 1

    # 残りをpartsに追加
    part_str = line[part_begin:length]
    parts.append(LinePart(ty=LinePartType.PLAIN, text=part_str))

    return parts


def process_single_page(page):
    title = page.get('title')
    id = page.get('id')
    created = page.get('created')
    updated = page.get('updated')
    lines = page.get('lines')

    print(f'converting {title} ({id})')

    if title == None:
        print(f'Title not found. Defaulting to the id')
        title = str(id)
    if id == None:
        print(f'Page ID not found. Aborting...')
        return

    if created == None:
        print(f'Created-timestamp not found. Defaulting to current datetime')
        created_utc = datetime.datetime.now(UTC)
    else:
        created_utc = datetime.datetime.fromtimestamp(int(created), UTC)
    if updated == None:
        print(f'Updated-timestamp not found. Defaulting to current datetime')
        updated_utc = datetime.datetime.now(UTC)
    else:
        updated_utc = datetime.datetime.fromtimestamp(int(updated), UTC)

    if lines == None:
        print(f'Page lines not found. Defaulting to empty list')
        lines = []

    for line in lines:
        parts = split_lines_into_parts(line)
        print(parts)


def main():
    scrapbox_file = "yumaprivate.json"
    output_dir = "."
    with open(scrapbox_file, mode='r', encoding='UTF-8') as f:
        s = f.read()
    j = json.loads(s)
    pages = j.get('pages')
    if pages == None:
        raise JsonPathNotFoundException('.pages')
    for page in pages:
        process_single_page(page)

if __name__ == '__main__':
    print(split_lines_into_parts("[aaaa]]hoge"))
    #main()
