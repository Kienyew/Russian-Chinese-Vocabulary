#!/usr/bin/env python3
import unittest
from extract import *

class Test(unittest.TestCase):
    def test_separate_ru_zh_chap(self):
        inputs = [
            'а而(1)',
            'а而（1）',
            'автомобиль汽车（18）',
            'алло喂！（打电话时招呼用语）（7）',
            'болеть[未]疼，痛（13）',
            'артист[阳]，артистка[阴]演员（13）',
            'аудитория（大学）教室（6）',
            'бегать[未，不定向]跑（18）',
            'наступать//наступить（某种时间）来临，到来（17）',
            'очередь (ж.) 次序；队列 （5）',
            'покойный (сущ.) 亡者，死者 （12）',
            'поехать[完]（乘车、船等）前往，出发（15）',
            'пятёрка数字5；（学校成绩）五分（12）'
        ]

        expects = [
            ('а', '而', '(1)'),
            ('а', '而', '（1）'),
            ('автомобиль', '汽车', '（18）'),
            ('алло', '喂！（打电话时招呼用语）', '（7）'),
            ('болеть[未]', '疼，痛', '（13）'),
            ('артист[阳]，артистка[阴]', '演员', '（13）'),
            ('аудитория', '（大学）教室', '（6）'),
            ('бегать[未，不定向]', '跑', '（18）'),
            ('наступать//наступить', '（某种时间）来临，到来', '（17）'),
            ('очередь (ж.)', '次序；队列', '（5）'),
            ('покойный (сущ.)', '亡者，死者', '（12）'),
            ('поехать[完]', '（乘车、船等）前往，出发', '（15）'),
            ('пятёрка', '数字5；（学校成绩）五分', '（12）'),
        ]

        for input, expect in zip(inputs, expects):
            self.assertEqual(separate_ru_zh_chap(input), expect)

    def test_parse_ru_entry(self):
        # RuEntry(word, annotations, gender, accent_index)
        inputs = [
            'а',
            'автомобиль',
            'алло',
            'болеть[未]',
            'артист[阳]',
            'бегать[未，不定向]',
            'очередь (ж.)',
            'покойный (сущ.)',
            'эмоциона´льно (нареч.)',
        ]

        expects = [
            RuEntry('а', [], None, None),
            RuEntry('автомобиль', [], None, None),
            RuEntry('алло', [], None, None),
            RuEntry('болеть', ['[未]'], None, None),
            RuEntry('артист', ['[阳]'], None, None),
            RuEntry('бегать', ['[未，不定向]'], None, None),
            RuEntry('очередь', [], FEMALE, None),
            RuEntry('покойный', ['(сущ.)'], None, None),
            RuEntry('эмоционально', ['(нареч.)'], None, 7),
        ]

        for input, expect in zip(inputs, expects):
            self.assertEqual(parse_ru_entry(input), expect)


if __name__ == '__main__':
    unittest.main()
