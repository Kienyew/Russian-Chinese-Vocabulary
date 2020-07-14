#!/usr/bin/env python3
# 2020年07月12日 星期日 19时55分44秒

import re
import json
import unicodedata
from typing import Iterator, List, Tuple, Union

MALE = 'м'
FEMALE = 'ж'


class RuEntry:
    def __init__(self, word: str, annotations: Union[List[str]], gender: Union[str, None], stress_index: Union[int, None]):
        self.word = word
        self.annotations = annotations
        self.gender = gender
        self.stress_index = stress_index

    def __str__(self) -> str:
        return f'RuEntry("{self.word}", annots={self.annotations}, gender={self.gender}), accent={self.stress_index})'

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class ZhEntry:
    def __init__(self, word):
        self.word = word

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __str__(self) -> str:
        return f'ZhEntry("{self.word}")'

    def __repr__(self) -> str:
        return str(self)

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class Entry:
    def __init__(self, ru: List[RuEntry], zh: List[ZhEntry], chap: int):
        self.ru = list(ru)
        self.zh = list(zh)
        self.chap = chap

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __str__(self) -> str:
        return f'Entry(\n\t{self.ru},\n\t{self.zh}, \n\tchap={self.chap}\n)'

    def as_dict(self) -> dict:
        return {
            'ru_entries': [*map(RuEntry.as_dict, self.ru)],
            'zh_entries': [*map(ZhEntry.as_dict, self.zh)],
            'chapter': self.chap
        }


def normalized(contents: str) -> Iterator:
    lines = list(map(str.strip, contents.splitlines()))
    line = 0
    good_pattern = re.compile(r'.*(\(|（)\d+(\)|）)$')
    while line < len(lines):
        current_line = lines[line]
        while not good_pattern.match(current_line):
            line += 1
            current_line += lines[line]

        yield current_line
        line += 1


def is_chinese_char(s: str):
    assert len(s) == 1
    return 'CJK' in unicodedata.name(s)


def separate_ru_zh_chap(entry_line: str) -> Tuple[str, str]:
    def first_cn_part_char(s: str) -> Union[None, int]:
        cn_char_index = None
        for i, c in enumerate(s):
            if c == '（' and is_chinese_char(s[i + 1]):
                cn_char_index = i
                break

            if is_chinese_char(c):
                cn_char_index = i
                break

        return cn_char_index

    cn_char_index = first_cn_part_char(entry_line)
    ru_part_str = None
    not_ru_part_str = None
    while True:
        bracket_start = None
        bracket_end = None
        for i, c in reversed(list(enumerate(entry_line[0:cn_char_index]))):
            if c == ']':
                break

            if c == '[':
                bracket_start = i
                break

        for i, c in enumerate(reversed(entry_line[cn_char_index + 1:])):
            if c == ']':
                bracket_end = cn_char_index + 1 + i
                break

        if bracket_start is None and bracket_end is None:
            ru_part_str = entry_line[:cn_char_index]
            not_ru_part_str = entry_line[cn_char_index:]
            break

        elif bracket_start is not None and bracket_end is not None:
            cn_char_index += first_cn_part_char(entry_line[cn_char_index + 1:]) + 1
            continue

        else:
            raise ValueError("Invalid bracket '[' and ']'")

    start_paren_pos = max(not_ru_part_str.rfind('（'), not_ru_part_str.rfind('('))
    if start_paren_pos == -1:
        raise ValueError('chapter part string not found')

    cn_part_str = not_ru_part_str[:start_paren_pos].strip()
    chap_part_str = not_ru_part_str[start_paren_pos:].strip()
    ru_part_str = ru_part_str.strip()
    return (ru_part_str, cn_part_str, chap_part_str)


def parse_ru_entry(s: str) -> Tuple[RuEntry, str]:
    annotations = []
    annotation_pattern = r'\(..+?\.\)|\[.+?\]'
    includes_indices = [0]
    for annotation_match in re.finditer(annotation_pattern, s):
        annotations.append(annotation_match.group())
        includes_indices.extend(annotation_match.span())

    includes_indices.append(len(s))

    s_annotations_removed = ''
    for i in range(0, len(includes_indices), 2):
        range_start = includes_indices[i]
        range_end = includes_indices[i + 1]
        s_annotations_removed += s[range_start:range_end]

    gender = None
    gender_pattern = r'\([мж]\.\)'
    if (match := re.search(gender_pattern, s)):
        match_str = match.group()
        gender = MALE if 'м' in match_str else FEMALE
        s_annotations_removed = s_annotations_removed.replace(match_str, '')

    s_annotations_removed = s_annotations_removed.strip()
    if (stress_index := s_annotations_removed.find('´')) >= 0:
        stress_index -= 1
        s_annotations_removed = s_annotations_removed.replace('´', '')
    else:
        stress_index = None

    return RuEntry(s_annotations_removed, annotations, gender, stress_index)


def parse_zh_entry(s: str) -> Tuple[ZhEntry, str]:
    return ZhEntry(s)


def parse_entry(entry_line: str):
    ru_str, zh_str, chap = separate_ru_zh_chap(entry_line)
    ru_entries = []
    ru_field_seps = r'[;；,]|//'
    for ru_entry_str in re.split(ru_field_seps, ru_str):
        ru_entries.append(parse_ru_entry(ru_entry_str))

    zh_entries = []
    zh_field_seps = r'[;；,，]|//'
    for zh_entry_str in re.split(zh_field_seps, zh_str):
        zh_entries.append(parse_zh_entry(zh_entry_str))

    chap = int(chap[1:-1])
    return Entry(ru_entries, zh_entries, chap)
