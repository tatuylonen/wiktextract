from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.headword_line import extract_headword_line
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestHeadword(TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(lang_code="zh"), Mock())

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_english_headword(self) -> None:
        # https://zh.wiktionary.org/wiki/manga#字源1
        # wikitext: {{en-noun|~|manga|s}}
        # expanded text: manga (可數 & 不可數，複數 manga 或 mangas)
        self.wxr.wtp.start_page("manga")
        self.wxr.wtp.add_page(
            "Template:en-noun",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="en">-{manga}-</strong> ([[可數|可數]] <small>和</small> [[不可數|不可數]]-{}-，複數-{ <b lang="en"><strong class="selflink">manga</strong></b> <small>或</small> <b>[[mangas#英語|-{mangas}-]]</b>}-)</span>',
        )
        root = self.wxr.wtp.parse("{{en-noun|~|manga|s}}")
        page_data = [
            WordEntry(word="manga", lang_code="en", lang="英語", pos="noun")
        ]
        self.wxr.wtp.title = "manga"
        extract_headword_line(self.wxr, page_data, root.children[0], "en")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "manga",
                    "lang_code": "en",
                    "lang": "英語",
                    "forms": [
                        {"form": "manga", "tags": ["plural"]},
                        {"form": "mangas", "tags": ["plural"]},
                    ],
                    "tags": ["countable", "uncountable"],
                    "pos": "noun",
                }
            ],
        )

    def test_headword_gender(self) -> None:
        # https://zh.wiktionary.org/wiki/manga#字源1_2
        # wikitext: {{nl-noun|m|-'s|mangaatje}}
        # expanded text: manga m (複數 manga's，指小詞 mangaatje n)
        self.wxr.wtp.start_page("manga")
        self.wxr.wtp.add_page(
            "Template:nl-noun",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="nl">-{manga}-</strong>&nbsp;<span class="gender"><abbr title="陽性名詞">m</abbr></span> (複數-{ <b>[[manga\'s#荷蘭語|-{manga\'s}-]]</b>}-，指小詞-{ <b>[[mangaatje#荷蘭語|-{mangaatje}-]]</b>&nbsp;<span class="gender"><abbr title="中性名詞">n</abbr></span>}-)</span>',
        )
        root = self.wxr.wtp.parse("{{nl-noun|m|-'s|mangaatje}}")
        page_data = [
            WordEntry(word="manga", lang_code="en", lang="英語", pos="noun")
        ]
        self.wxr.wtp.title = "manga"
        extract_headword_line(self.wxr, page_data, root.children[0], "nl")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "manga",
                    "lang_code": "en",
                    "lang": "英語",
                    "forms": [
                        {"form": "manga's", "tags": ["plural"]},
                        {
                            "form": "mangaatje",
                            "tags": ["neuter", "diminutive"],
                        },
                    ],
                    "tags": ["masculine"],
                    "pos": "noun",
                }
            ],
        )

    def test_headword_roman(self) -> None:
        # https://zh.wiktionary.org/wiki/-κρατίας
        # wikitext: {{head|grc|後綴變格形|g=f|head=-κρατίᾱς}}
        # expanded text: -κρατίᾱς (-kratíās) f
        self.wxr.wtp.start_page("-κρατίας")
        self.wxr.wtp.add_page(
            "Template:head",
            10,
            '<span class="headword-line"><strong class="Polyt headword" lang="grc">-{-κρατίᾱς}-</strong> (<span lang="grc-Latn" class="headword-tr tr Latn" dir="ltr">-kratíās</span>)&nbsp;<span class="gender"><abbr title="陰性名詞">f</abbr></span></span>',
        )
        root = self.wxr.wtp.parse("{{head|grc|後綴變格形|g=f|head=-κρατίᾱς}}")
        page_data = [
            WordEntry(
                word="-κρατίας", lang_code="grc", lang="古希臘語", pos="suffix"
            )
        ]
        self.wxr.wtp.title = "-κρατίας"
        extract_headword_line(self.wxr, page_data, root.children[0], "grc")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "-κρατίας",
                    "lang_code": "grc",
                    "lang": "古希臘語",
                    "forms": [
                        {"form": "-kratíās", "tags": ["romanization"]},
                    ],
                    "tags": ["feminine"],
                    "pos": "suffix",
                }
            ],
        )
