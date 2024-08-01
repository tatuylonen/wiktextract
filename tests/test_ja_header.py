from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.header import extract_header_nodes
from wiktextract.extractor.ja.models import Form, WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestJaHeader(TestCase):
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

    def test_en_noun(self):
        self.wxr.wtp.start_page("puppy")
        self.wxr.wtp.add_page(
            "テンプレート:en-noun",
            10,
            """[[カテゴリ:英語]][[カテゴリ:英語 名詞]]
<span class="infl-inline">'''puppy''' (<small>複数</small>&nbsp;<span class="form-of plural-form-of lang-en">'''[[puppies]]'''</span>)</span>""",
        )
        data = WordEntry(lang="英語", lang_code="en", word="puppy")
        root = self.wxr.wtp.parse("{{en-noun|pl=puppies}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(data.categories, ["英語", "英語 名詞"])
        self.assertEqual(data.forms, [Form(form="puppies", tags=["plural"])])

    def test_ja_noun(self):
        self.wxr.wtp.start_page("なきむし")
        self.wxr.wtp.add_page(
            "テンプレート:ja-noun",
            10,
            """<strong class="Jpan headword" lang="ja">なきむし</strong><span class="headword-kanji">【<b class="Jpan" lang="ja">[[泣き虫#日本語|泣き虫]]</b>】</span>[[カテゴリ:日本語 |なきむし]][[カテゴリ:日本語 名詞|なきむし]]""",
        )
        data = WordEntry(lang="日本語", lang_code="ja", word="なきむし")
        root = self.wxr.wtp.parse("{{ja-noun|泣き虫}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(data.categories, ["日本語", "日本語 名詞"])
        self.assertEqual(data.forms, [Form(form="泣き虫", tags=["kanji"])])

    def test_ja_verb(self):
        self.wxr.wtp.start_page("うつる")
        self.wxr.wtp.add_page(
            "テンプレート:ja-verb",
            10,
            """<strong class="Jpan headword" lang="ja">うつる</strong><span class="headword-kanji">【<b class="Jpan" lang="ja">[[移る#日本語|移る]]</b>・<b class="Jpan" lang="ja">[[遷る#日本語|遷る]]</b>】</span>""",
        )
        data = WordEntry(lang="日本語", lang_code="ja", word="うつる")
        root = self.wxr.wtp.parse("{{ja-verb|移る|遷る}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(
            data.forms,
            [
                Form(form="移る", tags=["kanji"]),
                Form(form="遷る", tags=["kanji"]),
            ],
        )

    def test_ja_verb_suru(self):
        self.wxr.wtp.start_page("料理")
        self.wxr.wtp.add_page(
            "テンプレート:ja-verb-suru",
            10,
            """<strong class="Jpan headword" lang="ja">[[料#日本語|料]][[理#日本語|理]][[する#日本語|する]]</strong> (<span class="headword-tr manual-tr tr" dir="ltr">りょうりする</span>)""",
        )
        data = WordEntry(lang="日本語", lang_code="ja", word="料理")
        root = self.wxr.wtp.parse("{{ja-verb-suru|りょうり}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(
            data.forms,
            [
                Form(form="料理する", tags=["canonical"]),
                Form(form="りょうりする"),
            ],
        )

    def test_plain_text_form(self):
        self.wxr.wtp.start_page("民主")
        data = WordEntry(lang="日本語", lang_code="ja", word="民主")
        root = self.wxr.wtp.parse("'''[[民]] [[主]]'''（みんしゅ）")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(data.forms, [Form(form="みんしゅ")])

    def test_plain_text_forms(self):
        self.wxr.wtp.start_page("うつる")
        data = WordEntry(lang="日本語", lang_code="ja", word="うつる")
        root = self.wxr.wtp.parse("'''うつる'''【[[写]]る、[[映]]る】")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(data.forms, [Form(form="写る"), Form(form="映る")])

    def test_zhchar(self):
        self.wxr.wtp.start_page("民主")
        data = WordEntry(lang="中国語", lang_code="zh", word="民主")
        root = self.wxr.wtp.parse("{{zhchar|民|主}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(len(data.forms), 0)
