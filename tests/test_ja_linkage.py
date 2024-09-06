from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.linkage import extract_linkage_section
from wiktextract.extractor.ja.models import WordEntry
from wiktextract.extractor.ja.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestJaLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ja"),
            WiktionaryConfig(
                dump_file_lang_code="ja",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_ruby(self):
        self.wxr.wtp.start_page("全然")
        self.wxr.wtp.add_page(
            "テンプレート:おくりがな2",
            10,
            "<ruby>[[全]]<rp>（</rp><rt>[[まったく|まった]]</rt><rp>）</rp></ruby>く",
        )
        data = WordEntry(word="全然", lang="日本語", lang_code="ja", pos="adv")
        root = self.wxr.wtp.parse("* {{おくりがな2|全|まった|く|まったく}}")
        extract_linkage_section(self.wxr, data, root, "synonyms")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.synonyms],
            [{"word": "全く", "ruby": [("全", "まった")]}],
        )

    def test_sense(self):
        self.wxr.wtp.start_page("日本")
        self.wxr.wtp.add_page(
            "テンプレート:xlink",
            10,
            "<ruby>[[w:ニホンアカガエル|日本赤蛙]]<rp>（</rp><rt>[[日本赤蛙|→作成]]</rt><rp>）</rp></ruby>",
        )
        data = WordEntry(word="日本", lang="日本語", lang_code="ja", pos="name")
        root = self.wxr.wtp.parse("""{{rel-top5|生物名}}
* {{xlink|日本赤蛙|ニホンアカガエル}}""")
        extract_linkage_section(self.wxr, data, root, "proverbs")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.proverbs],
            [{"word": "日本赤蛙", "sense": "生物名"}],
        )

    def test_phrase(self):
        # "成句" could also be POS title
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:noun", 10, "名詞")
        self.wxr.wtp.add_page("テンプレート:idiom", 10, "成句")
        self.assertEqual(
            parse_page(
                self.wxr,
                "青",
                """=={{L|ja}}==
==={{noun}}===
# gloss
==={{idiom}}===
*[[青天の霹靂]]""",
            ),
            [
                {
                    "word": "青",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "lang_code": "ja",
                    "lang": "日本語",
                    "senses": [{"glosses": ["gloss"]}],
                    "phrases": [{"word": "青天の霹靂"}],
                }
            ],
        )

    def test_linkage_type_in_list_item(self):
        self.wxr.wtp.start_page("豆乳")
        self.wxr.wtp.add_page("テンプレート:prov", 10, "熟語")
        data = WordEntry(word="豆乳", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("""* [[うのはな|卯の花]]
* {{prov}}: [[調製豆乳]]""")
        extract_linkage_section(self.wxr, data, root, "related")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.related],
            [{"word": "卯の花"}],
        )
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.proverbs],
            [{"word": "調製豆乳"}],
        )

    def test_linkage_under_gloss_list(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:noun", 10, "名詞")
        self.wxr.wtp.add_page("テンプレート:idiom", 10, "成句")
        data = parse_page(
            self.wxr,
            "みそ",
            """== {{ja}} ==
=== {{noun}} ===
# [[失敗]]。
#*{{idiom}}:[[みそをつける]]""",
        )
        self.assertEqual(
            data[0]["phrases"], [{"word": "みそをつける", "sense": "失敗。"}]
        )

    # set to None to force using ja edition ns prefixes
    @patch("wiktextract.clean.IMAGE_LINK_RE", return_value=None)
    def test_bagua_image(self, mock_re):
        # no image link
        self.wxr.wtp.start_page("太陽")
        data = WordEntry(word="太陽", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("* [[画像:Shaoyin.png]][[少陰]]")
        extract_linkage_section(self.wxr, data, root, "related")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.related],
            [{"word": "少陰"}],
        )

    def test_nested_list_change_linkage_type(self):
        self.wxr.wtp.start_page("太陽")
        self.wxr.wtp.add_page("テンプレート:syn", 10, "類義語")
        data = WordEntry(word="太陽", lang="日本語", lang_code="ja", pos="name")
        root = self.wxr.wtp.parse("* {{syn}}:\n*: [[天日]]")
        extract_linkage_section(self.wxr, data, root, "related")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.synonyms],
            [{"word": "天日"}],
        )

    def test_sense_template(self):
        self.wxr.wtp.start_page("大切")
        self.wxr.wtp.add_page(
            "テンプレート:sense",
            10,
            '<span class="ib-brac"><span class="qualifier-brac"> (</span></span><span class="ib-content"><span class="qualifier-content">重要だ</span></span><span class="ib-brac"><span class="qualifier-brac">)</span></span><span class="ib-colon"><span class="sense-qualifier-colon">:</span></span>',
        )
        data = WordEntry(
            word="大切", lang="日本語", lang_code="ja", pos="adj_noun"
        )
        root = self.wxr.wtp.parse("* {{sense|重要だ}} [[些細]]")
        extract_linkage_section(self.wxr, data, root, "antonyms")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.antonyms],
            [{"word": "些細", "sense": "重要だ"}],
        )
