#!/usr/bin/env python3

import json
from pathlib import Path

import extract

if __name__ == '__main__':
    entries_dicts = []
    for i in range(1, 5):
        file = Path(f'./vocab_book_{i}.txt')
        for entry in map(extract.parse_entry, extract.normalized(file.read_text())):
            entry_dict = json.loads(entry.toJSON())
            entry_dict['book'] = i
            entries_dicts += [entry_dict]

    entries_dicts.sort(key=lambda entry: (entry['book'], entry['chapter'], entry['ru_entries'][0]['word']))
    print(json.dumps(entries_dicts, ensure_ascii=False, indent=2))
