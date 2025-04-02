from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_t_template(self):
        self.wxr.wtp.add_page(
            "Templat:ter-atas",
            10,
            "{{{1}}}[[Kategori:Entries with translation boxes|ABADI]]",
        )
        self.wxr.wtp.add_page(
            "Templat:t+",
            10,
            '<span class="Hani" lang="cmn">[[永远#Mandarin|永远]]</span><span class="tpos">&nbsp;[[:zh&#x3A;永远|(zh)]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="cmn-Latn" class="tr Latn">yǒngyuǎn</span><span class="mention-gloss-paren annotation-paren">)</span>[[Kategori:Kata bahasa Mandarin dengan kod skrip lewah|ABADI]][[Kategori:Kata dengan terjemahan bahasa Mandarin|ABADI]]',
        )
        self.wxr.wtp.add_page(
            "Templat:t",
            10,
            '<span class="Deva" lang="hi">[[सनातन#Hindi|सनातन]]</span>&nbsp;<span class="gender"><abbr title="jantina maskulin">m</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="hi-Latn" class="tr Latn">sanaatan</span><span class="mention-gloss-paren annotation-paren">)</span>[[Kategori:Kata bahasa Hindi dengan kod skrip lewah|ABADI]][[Kategori:Kata bahasa Hindi dengan transliterasi manual tidak lewah|ABADI]][[Kategori:Kata dengan terjemahan bahasa Hindi|ABADI]]',
        )
        page_data = parse_page(
            self.wxr,
            "abadi",
            """== Bahasa Melayu ==
=== Takrifan ===
# [[kekal]] untuk selamanya.
=== Terjemahan ===
{{ter-atas|kekal selamanya}}
* Cina:
*: Mandarin: {{t+|cmn|永远|tr=yǒngyuǎn|sc=Hani}}
* Hindi: {{t|hi|सनातन|m|tr=sanaatan|sc=Deva}}""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "Mandarin",
                    "lang_code": "cmn",
                    "word": "永远",
                    "roman": "yǒngyuǎn",
                    "sense": "kekal selamanya",
                },
                {
                    "lang": "Hindi",
                    "lang_code": "hi",
                    "word": "सनातन",
                    "roman": "sanaatan",
                    "sense": "kekal selamanya",
                    "tags": ["masculine"],
                },
            ],
        )
        self.assertEqual(
            page_data[0]["categories"],
            [
                "Entries with translation boxes",
                "Kata bahasa Mandarin dengan kod skrip lewah",
                "Kata dengan terjemahan bahasa Mandarin",
                "Kata bahasa Hindi dengan kod skrip lewah",
                "Kata bahasa Hindi dengan transliterasi manual tidak lewah",
                "Kata dengan terjemahan bahasa Hindi",
            ],
        )
