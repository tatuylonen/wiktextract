from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlTranslation(TestCase):
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

    def test_simple_list(self):
        self.wxr.wtp.add_page("Szablon:m", 10, "m")
        page_data = parse_page(
            self.wxr,
            "słownik",
            """== słownik ({{język polski}}) ==
===znaczenia===
''rzeczownik, rodzaj męskorzeczowy''
: (1.1) [[zbiór]]

===tłumaczenia===
* albański: (1.1) [[fjalor]] {{m}} (fyalór)
* chiński standardowy: (1.1) [[字典]] (zìdiǎn), [[词典]] (cídiǎn); (1.2) [[词典]] (cídiǎn)""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "albański",
                    "lang_code": "sq",
                    "word": "fjalor",
                    "sense_index": "1.1",
                    "tags": ["masculine"],
                    "roman": "fyalór",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "zh",
                    "word": "字典",
                    "sense_index": "1.1",
                    "roman": "zìdiǎn",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "zh",
                    "word": "词典",
                    "sense_index": "1.1",
                    "roman": "cídiǎn",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "zh",
                    "word": "词典",
                    "sense_index": "1.2",
                    "roman": "cídiǎn",
                },
            ],
        )

    def test_close_links(self):
        self.wxr.wtp.add_page(
            "Szablon:furi",
            10,
            '<span class="furigana-wrapper" lang="ja" xml:lang="ja">[[語]]<span class="furigana-caption">(ご)</span></span>',
        )
        self.wxr.wtp.start_page("polski")
        page_data = parse_page(
            self.wxr,
            "polski",
            """== polski ({{język polski}}) ==
===znaczenia===
''przymiotnik relacyjny''
: (1.1) gloss 1

''rzeczownik, rodzaj męskorzeczowy''
: (2.1) gloss 2

===tłumaczenia===
* japoński: (1.1) [[ポーランド]][[の]]; (2.1) [[ポーランド]]{{furi|語|ご}}""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "japoński",
                    "lang_code": "ja",
                    "word": "ポーランドの",
                    "sense_index": "1.1",
                }
            ],
        )
        self.assertEqual(
            page_data[1]["translations"],
            [
                {
                    "lang": "japoński",
                    "lang_code": "ja",
                    "word": "ポーランド語",
                    "sense_index": "2.1",
                    "ruby": [("語", "ご")],
                },
            ],
        )

    def test_furi(self):
        self.wxr.wtp.add_page(
            "Szablon:przest",
            10,
            '<span class="short-container">[[Wikisłownik:Użycie szablonów daw, hist, przest, stpol|<span class="short-wrapper" title="przestarzałe, przestarzały" data-expanded="przestarzałe, przestarzały"><span class="short-content">przest.</span></span>]]</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:furi",
            10,
            '<span class="furigana-wrapper" lang="ja" xml:lang="ja">[[{{{1}}}]]<span class="furigana-caption">({{{2}}})</span></span>',
        )
        self.wxr.wtp.start_page("umierać")
        page_data = parse_page(
            self.wxr,
            "umierać",
            """== polski ({{język polski}}) ==
===znaczenia===
''czasownik''
: (1.1) gloss 1

===tłumaczenia===
* japoński: (1.1) {{furi|死亡する|[[しぼうする]]}} (shibō suru), {{przest}} {{furi|死する|[[しする]]}} (shi suru)""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "japoński",
                    "lang_code": "ja",
                    "word": "死亡する",
                    "ruby": [("死亡する", "しぼうする")],
                    "sense_index": "1.1",
                    "roman": "shibō suru",
                },
                {
                    "lang": "japoński",
                    "lang_code": "ja",
                    "word": "死する",
                    "ruby": [("死する", "しする")],
                    "sense_index": "1.1",
                    "roman": "shi suru",
                    "tags": ["obsolete"],
                },
            ],
        )
