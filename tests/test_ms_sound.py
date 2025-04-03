from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsSound(TestCase):
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

    def test_abadi(self):
        self.wxr.wtp.add_page(
            "Templat:dewan",
            10,
            "[[w:Kamus Dewan|Kamus Dewan]]: <span>a</span>'''·'''<span>ba</span>'''·'''<span>di</span>",
        )
        self.wxr.wtp.add_page(
            "Templat:AFA",
            10,
            '[[Wikikamus:Abjad Fonetik Antarabangsa|AFA]]<sup>([[Lampiran:Sebutan bahasa Melayu|kekunci]])</sup>:&#32;<span class="IPA">/abadi/</span>[[Kategori:Perkataan bahasa Melayu dengan sebutan AFA|ABADI]]',
        )
        self.wxr.wtp.add_page(
            "Templat:rhymes",
            10,
            'Rima: [[Rima:Bahasa Melayu/di|<span class="IPA">-di</span>]], [[Rima:Bahasa Melayu/i|<span class="IPA">-i</span>]][[Kategori:Rima:Bahasa Melayu/di|ABADI]][[Kategori:Rima:Bahasa Melayu/i|ABADI]]',
        )
        self.wxr.wtp.add_page(
            "Templat:penyempangan",
            10,
            'Penyempangan: <span class="Latn" lang="ms">a‧ba‧di</span>',
        )
        page_data = parse_page(
            self.wxr,
            "abadi",
            """== Bahasa Melayu ==
=== Takrifan ===
# [[kekal]] untuk selamanya.
=== Sebutan ===
* {{dewan|a|ba|di}}
* {{AFA|ms|/abadi/}}
* {{rhymes|ms|di|i}}
* {{penyempangan|ms|a|ba|di}}""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            [
                "Perkataan bahasa Melayu dengan sebutan AFA",
                "Rima:Bahasa Melayu/di",
                "Rima:Bahasa Melayu/i",
            ],
        )
        self.assertEqual(
            page_data[0]["sounds"],
            [
                {"other": "a·ba·di", "raw_tags": ["Kamus Dewan"]},
                {"ipa": "/abadi/"},
                {"rhymes": "-di"},
                {"rhymes": "-i"},
            ],
        )
        self.assertEqual(page_data[0]["hyphenation"], "a‧ba‧di")

    def test_bendera(self):
        self.wxr.wtp.add_page(
            "Templat:a",
            10,
            '<span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">Bahasa Baku</span><span class="ib-brac qualifier-brac">)</span>',
        )
        self.wxr.wtp.add_page(
            "Templat:IPA",
            10,
            '[[Wikikamus:Abjad Fonetik Antarabangsa|AFA]]<sup>([[Lampiran:Sebutan bahasa Melayu|kekunci]])</sup>:&#32;<span class="IPA">/bəndeɾa/</span>[[Kategori:Perkataan bahasa Melayu dengan sebutan AFA|ABADI]]',
        )
        self.wxr.wtp.add_page(
            "Templat:rhymes",
            10,
            'Rima: [[Rima:Bahasa Melayu/di|<span class="IPA">-di</span>]], [[Rima:Bahasa Melayu/i|<span class="IPA">-i</span>]][[Kategori:Rima:Bahasa Melayu/di|ABADI]][[Kategori:Rima:Bahasa Melayu/i|ABADI]]',
        )
        page_data = parse_page(
            self.wxr,
            "bendera",
            """== Bahasa Melayu ==
=== Takrifan ===
# sepotong [[kain]]
=== Sebutan ===
* {{a|Bahasa Baku}} {{IPA|ms|/bəndeɾa/}}
* {{audio|ms|Ms-MY-bendera.ogg|Audio (MY, Johor-Riau)}}""",
        )
        self.assertEqual(
            page_data[0]["sounds"][0],
            {"ipa": "/bəndeɾa/", "raw_tags": ["Bahasa Baku"]},
        )
        self.assertEqual(
            page_data[0]["sounds"][1]["audio"], "Ms-MY-bendera.ogg"
        )
