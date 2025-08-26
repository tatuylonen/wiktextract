from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.models import WordEntry
from wiktextract.extractor.ja.page import parse_page
from wiktextract.extractor.ja.translation import extract_translation_section
from wiktextract.wxr_context import WiktextractContext


class TestJaTransaltion(TestCase):
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

    def test_common_layout(self):
        self.wxr.wtp.start_page("今日")
        self.wxr.wtp.add_page(
            "テンプレート:T",
            10,
            """{{#switch: {{{1}}}
| bg = ブルガリア語
| fa = ペルシア語
}}""",
        )
        data = WordEntry(word="今日", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("""{{trans-top|今過ごしているその日（副詞）}}
*{{T|bg}}: {{t|bg|днес|tr=dnés}}, [[днеска]]
*{{T|fa}}: {{t+|fa|امروز|alt=اِمروز|tr=emruz}}""")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "ブルガリア語",
                    "lang_code": "bg",
                    "word": "днес",
                    "roman": "dnés",
                    "sense": "今過ごしているその日（副詞）",
                },
                {
                    "lang": "ブルガリア語",
                    "lang_code": "bg",
                    "word": "днеска",
                    "sense": "今過ごしているその日（副詞）",
                },
                {
                    "lang": "ペルシア語",
                    "lang_code": "fa",
                    "word": "اِمروز",
                    "roman": "emruz",
                    "sense": "今過ごしているその日（副詞）",
                },
            ],
        )

    def test_lang_code_template(self):
        self.wxr.wtp.start_page("保護")
        self.wxr.wtp.add_page("テンプレート:de", 10, "ドイツ語")
        data = WordEntry(word="保護", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("*{{de}}: [[schützen]]")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [{"lang": "ドイツ語", "lang_code": "de", "word": "schützen"}],
        )

    def test_plain_text_lang_name(self):
        self.wxr.wtp.start_page("保護")
        data = WordEntry(word="保護", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("*イタリア語: [[proteggere]]")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [{"lang": "イタリア語", "lang_code": "it", "word": "proteggere"}],
        )

    def test_nested_list(self):
        self.wxr.wtp.start_page("いろ")
        self.wxr.wtp.add_page("テンプレート:zh", 10, "中国語")
        self.wxr.wtp.add_page("テンプレート:yue", 10, "広東語")
        data = WordEntry(word="いろ", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("""*[[{{zh}}]]: {{t+|cmn|色|tr=sè|sc=Hani}}
**[[{{yue}}]]: {{t|yue|色|tr=sik1|sc=Hani}}""")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "中国語",
                    "lang_code": "zh",
                    "word": "色",
                    "roman": "sè",
                },
                {
                    "lang": "広東語",
                    "lang_code": "yue",
                    "word": "色",
                    "roman": "sik1",
                },
            ],
        )

    def test_t_template_tag(self):
        self.wxr.wtp.start_page("いろ")
        self.wxr.wtp.add_page("テンプレート:an", 10, "アラゴン語")
        data = WordEntry(word="いろ", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("*[[{{an}}]]: {{t|an|color|f}}")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "アラゴン語",
                    "lang_code": "an",
                    "word": "color",
                    "tags": ["feminine"],
                }
            ],
        )

    def test_archar(self):
        self.wxr.wtp.start_page("いぬ")
        self.wxr.wtp.add_page("テンプレート:ar", 10, "アラビア語")
        self.wxr.wtp.add_page("テンプレート:ARchar", 10, "{{{1}}}")
        self.wxr.wtp.add_page("テンプレート:m", 10, "男性")
        data = WordEntry(word="いぬ", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse(
            "* [[{{ar}}]]: {{ARchar|[[ٌكلب|كَلْب]]}} (kalb) {{m}}"
        )
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "アラビア語",
                    "lang_code": "ar",
                    "word": "كَلْب",
                    "tags": ["masculine"],
                }
            ],
        )

    def test_t_template_number_tag(self):
        self.wxr.wtp.start_page("双魚宮")
        self.wxr.wtp.add_page("テンプレート:T", 10, "ロシア語")
        data = WordEntry(
            word="双魚宮", lang="日本語", lang_code="ja", pos="noun"
        )
        root = self.wxr.wtp.parse(
            "*{{T|ru}}: {{t-|ru|Рыбы|f|p|tr=Rýby|sc=Cyrl}}"
        )
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "ロシア語",
                    "lang_code": "ru",
                    "word": "Рыбы",
                    "roman": "Rýby",
                    "tags": ["feminine", "plural"],
                }
            ],
        )

    def test_tag_template(self):
        self.wxr.wtp.start_page("双魚宮")
        self.wxr.wtp.add_page("テンプレート:T", 10, "アイスランド語")
        self.wxr.wtp.add_page("テンプレート:npl", 10, "中性/複数")
        data = WordEntry(
            word="双魚宮", lang="日本語", lang_code="ja", pos="noun"
        )
        root = self.wxr.wtp.parse("*{{T|is}}: [[fiskarnir]] {{npl}}")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "アイスランド語",
                    "lang_code": "is",
                    "word": "fiskarnir",
                    "tags": ["neuter", "plural"],
                }
            ],
        )

    def test_fallback_to_parent_list_lang(self):
        self.wxr.wtp.start_page("双魚宮")
        self.wxr.wtp.add_page("テンプレート:T", 10, "セルビア・クロアチア語")
        data = WordEntry(
            word="双魚宮", lang="日本語", lang_code="ja", pos="noun"
        )
        root = self.wxr.wtp.parse("*{{T|sh}}:\n*:キリル文字: [[Рибе]]")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "セルビア・クロアチア語",
                    "lang_code": "sh",
                    "word": "Рибе",
                }
            ],
        )

    def test_zh_ts(self):
        self.wxr.wtp.start_page("豆乳")
        self.wxr.wtp.add_page("テンプレート:T", 10, "中国語")
        data = WordEntry(word="豆乳", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse("*{{T|zh}}: {{zh-ts|[[豆漿]]|[[豆浆]]}}")
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "中国語",
                    "lang_code": "zh",
                    "word": "豆漿",
                    "tags": ["Traditional-Chinese"],
                },
                {
                    "lang": "中国語",
                    "lang_code": "zh",
                    "word": "豆浆",
                    "tags": ["Simplified-Chinese"],
                },
            ],
        )

    def test_zh_l(self):
        self.wxr.wtp.start_page("音楽")
        self.wxr.wtp.add_page("テンプレート:T", 10, "広東語")
        self.wxr.wtp.add_page(
            "テンプレート:zh-l",
            10,
            '<span class="Hani" lang="zh">[[音樂#中国語|音樂]]</span>／<span class="Hani" lang="zh">[[音乐#中国語|音乐]]</span> (<i lang="zh-Latn" class="tr Latn">jam<sup>1</sup> ngok<sup>6</sup></i>)',
        )
        data = WordEntry(word="音楽", lang="日本語", lang_code="ja", pos="noun")
        root = self.wxr.wtp.parse(
            "*{{T|yue}}: {{t|yue|{{zh-l|音樂|tr=jam{{supra|1}} ngok{{supra|6}}}}}}"
        )
        extract_translation_section(self.wxr, data, root)
        self.assertEqual(
            [t.model_dump(exclude_defaults=True) for t in data.translations],
            [
                {
                    "lang": "広東語",
                    "lang_code": "yue",
                    "word": "音樂",
                    "tags": ["Traditional-Chinese"],
                    "roman": "jam¹ ngok⁶",
                },
                {
                    "lang": "広東語",
                    "lang_code": "yue",
                    "word": "音乐",
                    "tags": ["Simplified-Chinese"],
                    "roman": "jam¹ ngok⁶",
                },
            ],
        )

    def test_trans_see_id(self):
        self.wxr.wtp.add_page("テンプレート:T", 10, "英語")
        self.wxr.wtp.add_page(
            "バス",
            0,
            """==日本語==
===名詞:音楽===
# [[男声]]の[[低音域]][[パート]]。
====翻訳====
<span id="翻訳:バス(音楽)"></span>
* {{T|en}}: {{t+|en|bass}}""",
        )
        data = parse_page(
            self.wxr,
            "低音",
            """==日本語==
===名詞===
#[[ひくい|低い]]または[[よわい|弱い]][[音]]や声。
====翻訳====
{{trans-see2|語義2|バス#翻訳:バス(音楽)}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "英語",
                    "lang_code": "en",
                    "word": "bass",
                    "sense": "語義2",
                }
            ],
        )
