from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.models import WordEntry
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
