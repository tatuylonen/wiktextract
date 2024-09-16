from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_example(self):
        self.wxr.wtp.add_page("Szablon:język angielski", 10, "język angielski")
        page_data = parse_page(
            self.wxr,
            "dream",
            """== dream ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (2.1) [[sen]]
===przykłady===
: (2.1) ''[[passionately|Passionately]] [[enamor]]ed [[of]] [[this]] [[shadow]] [[of]] [[a]] [[dream]]''<ref>Washington Irving</ref> → [[gorąco|Gorąco]] [[zakochany]] [[w]] [[cień|cieniu]] [[ze]] '''[[sen|snów]]'''""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "Passionately enamored of this shadow of a dream",
                        "ref": "Washington Irving",
                        "translation": "Gorąco zakochany w cieniu ze snów",
                    }
                ],
                "glosses": ["sen"],
                "sense_index": "2.1",
            },
        )

    def test_examples_across_different_pos_sections(self):
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>',
        )
        self.wxr.wtp.add_page("Szablon:zool", 10, "zool.")
        page_data = parse_page(
            self.wxr,
            "dog",
            """== dog ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (1.1) {{zool}} [[pies]]
''czasownik przechodni''
: (3.1) [[ścigać]], [[śledzić]]
===przykłady===
: (1.1) ''[[it|It]] [[be|is]] [[say|said]] [[that]] [[a]] [[dog]] [[is]] [[a]] [[human]][['s]] [[good|best]] [[friend]].'' → [[mówić|Mówi]] [[się]], [[że]] '''[[pies]]''' [[być|jest]] [[dobry|najlepszym]] [[przyjaciel]]em [[człowiek]]a.
: (3.1) ''[[trouble|Trouble]] [[dog]]ged [[his]] [[every]] [[step]].'' → [[kłopot|Kłopoty]] '''[[dosięgać|dosięgały]]''' [[on|go]] [[na]] [[każdy]]m [[krok]]u.""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "It is said that a dog is a human's best friend.",
                        "translation": "Mówi się, że pies jest najlepszym przyjacielem człowieka.",
                    }
                ],
                "glosses": ["pies"],
                "topics": ["zoology"],
                "sense_index": "1.1",
            },
        )
        self.assertEqual(
            page_data[1]["senses"][0],
            {
                "examples": [
                    {
                        "text": "Trouble dogged his every step.",
                        "translation": "Kłopoty dosięgały go na każdym kroku.",
                    }
                ],
                "glosses": ["ścigać, śledzić"],
                "sense_index": "3.1",
            },
        )

    def test_no_italic(self):
        self.wxr.wtp.add_page(
            "Szablon:język chiński standardowy",
            10,
            '<span class="lang-code primary-lang-code lang-code-zh" id="zh">[[:Kategoria:Język chiński standardowy|język chiński standardowy]]</span>',
        )
        self.wxr.wtp.add_page("Szablon:zool", 10, "zool.")
        page_data = parse_page(
            self.wxr,
            "喜欢",
            """== {{zh|喜欢}} ({{język chiński standardowy}}) ==
===znaczenia===
''czasownik''
: (1.1) [[lubić]]
===przykłady===
: (1.1) [[我]][[喜欢]][[在]][[硬]][[地场]][[上]][[打球]]。(wǒ xǐhuān zài yìng dìchǎng shàng dǎqiú) → '''[[lubić|Lubię]]''' [[grać]] [[na]] [[twardy]]ch [[kort]]ach.""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "我喜欢在硬地场上打球。",
                        "roman": "wǒ xǐhuān zài yìng dìchǎng shàng dǎqiú",
                        "translation": "Lubię grać na twardych kortach.",
                    }
                ],
                "glosses": ["lubić"],
                "sense_index": "1.1",
            },
        )

    def test_not_roman(self):
        self.wxr.wtp.add_page(
            "Szablon:język czeski",
            10,
            '<span class="lang-code primary-lang-code lang-code-cs" id="cs">[[Słownik języka czeskiego|język czeski]]</span>',
        )
        self.wxr.wtp.add_page("Szablon:anat", 10, "anat.")
        page_data = parse_page(
            self.wxr,
            "oko",
            """== oko ({{język czeski}}) ==
===znaczenia===
''rzeczownik, rodzaj nijaki''
: (1.1) {{anat}} [[oko]]
===przykłady===
: (1.1) ''[[v|V]] [[jazyk|jazyce]] [[metafora|metafor]] [[být|je]] [[oko]] [[často|nejčastěji]] [[spojovat|spojováno]] [[s]] [[duše|duší]] ([[jakožto]] [[ona|její]] [[okno]]).''<ref>[http://www.souvislosti.cz/201/krato.html z Internetu]</ref> → [[w|W]] [[język]]u [[metafora|metafor]] '''[[oko]]''' [[częsty|najczęściej]] [[łączyć|łączone]] [[być|jest]] [[z]] [[dusza|duszą]] ([[jako]] [[ona|jej]] [[okno]]).""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "V jazyce metafor je oko nejčastěji spojováno s duší (jakožto její okno).",
                        "translation": "W języku metafor oko najczęściej łączone jest z duszą (jako jej okno).",
                        "ref": "z Internetu",
                    }
                ],
                "glosses": ["oko"],
                "topics": ["anatomy"],
                "sense_index": "1.1",
            },
        )

    def test_literal_meaning(self):
        self.wxr.wtp.add_page(
            "Szablon:język chiński standardowy",
            10,
            '<span class="lang-code primary-lang-code lang-code-zh" id="zh">[[:Kategoria:Język chiński standardowy|język chiński standardowy]]</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:dosł",
            10,
            '<span class="short-container">[[Aneks:Skróty używane w Wikisłowniku#D|<span class="short-wrapper" title="dosłownie" data-expanded="dosłownie"><span class="short-content">dosł.</span></span>]]</span>',
        )
        self.wxr.wtp.start_page("房子")
        page_data = parse_page(
            self.wxr,
            "房子",
            """== {{zh|房子}} ({{język chiński standardowy}}) ==
===znaczenia===
''czasownik''
: (1.2) [[miejsce]], [[miejscówka]]
===przykłady===
: (1.2) [[我]][[讨厌]][[这]][[房子]]，[[跟]][[坟墓]][[差不多]]！(wǒ tǎoyàn zhè fángzi gēn fénmù chàbùduō) → [[nienawidzić|Nienawidzę]] [[to|tego]] '''[[miejsce|miejsca]]''', [[tu]] [[być|jest]] [[jak]] [[w]] [[grobowiec|grobowcu]]! ({{dosł}} …[[być|jest]] [[prawie]] [[grobowiec|grobowcem]]!)""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "我讨厌这房子，跟坟墓差不多！",
                        "roman": "wǒ tǎoyàn zhè fángzi gēn fénmù chàbùduō",
                        "translation": "Nienawidzę tego miejsca, tu jest jak w grobowcu!",
                        "literal_meaning": "…jest prawie grobowcem!",
                    }
                ],
                "glosses": ["miejsce, miejscówka"],
                "sense_index": "1.2",
            },
        )
