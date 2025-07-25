from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.header import extract_header_nodes
from wiktextract.extractor.ja.models import Form, WordEntry
from wiktextract.extractor.ja.page import parse_page
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

    def test_zhchar(self):
        self.wxr.wtp.start_page("民主")
        data = WordEntry(lang="中国語", lang_code="zh", word="民主")
        root = self.wxr.wtp.parse("{{zhchar|民|主}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(len(data.forms), 0)

    def test_three_bold_nodes(self):
        # no "canonical" tag
        self.wxr.wtp.start_page("みそ")
        data = WordEntry(lang="日本語", lang_code="ja", word="みそ")
        root = self.wxr.wtp.parse(
            "'''みそ'''【'''[[味]][[噌]]'''、'''[[未]][[醤]]'''】"
        )
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(data.forms, [Form(form="味噌"), Form(form="未醤")])

    def test_en_verb(self):
        self.wxr.wtp.start_page("debate")
        self.wxr.wtp.add_page(
            "テンプレート:en-verb",
            10,
            """<strong class="Latn headword" lang="en">debate</strong>
(<small>三単現: </small>''[[debates]]'')""",
        )
        data = WordEntry(lang="英語", lang_code="en", word="debate")
        root = self.wxr.wtp.parse("{{en-verb|debat|ing}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(
            data.forms,
            [
                Form(
                    form="debates", tags=["third-person", "singular", "present"]
                )
            ],
        )

    def test_ja_noun_small_tag(self):
        self.wxr.wtp.start_page("金玉")
        self.wxr.wtp.add_page(
            "テンプレート:ja-noun",
            10,
            """<strong class="Jpan headword" lang="ja">[[金#日本語|金]][[玉#日本語|玉]]</strong> (<span class="headword-tr manual-tr tr" dir="ltr">きんぎょく</span> <i><small><small>又は</small></small></i> <span class="headword-tr manual-tr tr" dir="ltr">きんたま</span> <i><small><small>又は</small></small></i> <span class="headword-tr manual-tr tr" dir="ltr">かねだま</span>)""",
        )
        data = WordEntry(lang="日本語", lang_code="ja", word="金玉")
        root = self.wxr.wtp.parse("{{ja-noun|きんぎょく|きんたま|かねだま}}")
        extract_header_nodes(self.wxr, data, root.children)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in data.forms],
            [
                {"form": "きんぎょく"},
                {"form": "きんたま"},
                {"form": "かねだま"},
            ],
        )

    def test_gender(self):
        self.wxr.wtp.add_page(
            "テンプレート:pl-noun",
            10,
            '<strong class="Latn headword" lang="pl">Portugalczyk</strong>&nbsp;<span class="gender">男性&nbsp;人称</span>[[カテゴリ:ポーランド語 |PORTUGALCZYK]][[カテゴリ:ポーランド語 名詞|PORTUGALCZYK]][[カテゴリ:ポーランド語 男性人間名詞|PORTUGALCZYK]]',
        )
        page_data = parse_page(
            self.wxr,
            "ryba",
            """==ポーランド語==
===名詞===
{{pl-noun|g=m-pr}}
# [[ポルトガル人]]。""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["ポーランド語", "ポーランド語 名詞", "ポーランド語 男性人間名詞"],
        )
        self.assertEqual(page_data[0]["tags"], ["masculine", "personal"])

    def test_ru_noun(self):
        self.wxr.wtp.add_page(
            "テンプレート:ru-noun+",
            10,
            """<strong class="Cyrl headword" lang="ru">ко́мната</strong> <b>[[Wiktionary:ロシア語の翻字|•]]</b> (<span lang="ru-Latn" class="headword-tr manual-tr tr Latn" dir="ltr">kómnata</span>)&nbsp;<span class="gender">女性&nbsp;非有生</span> (<i>生格</i> <b class="Cyrl" lang="ru">[[комнаты#ロシア語|ко́мнаты]]</b>, <i>複数主格</i> <b class="Cyrl" lang="ru">[[комнаты#ロシア語|ко́мнаты]]</b>, <i>複数生格</i> <b class="Cyrl" lang="ru">[[комнат#ロシア語|ко́мнат]]</b>, <i>形容詞</i> <b class="Cyrl" lang="ru">[[комнатный#ロシア語|ко́мнатный]]</b>, <i>指小形</i> <b class="Cyrl" lang="ru">[[комнатка#ロシア語|ко́мнатка]]</b> <i><small><small>又は</small></small></i> <b class="Cyrl" lang="ru">[[комнатушка#ロシア語|комнату́шка]]</b>)[[カテゴリ:ロシア語 |КОМНАТА]][[カテゴリ:ロシア語 名詞|КОМНАТА]]""",
        )
        page_data = parse_page(
            self.wxr,
            "комната",
            """==ロシア語==
===名詞===
{{ru-noun+|ко́мната|adj=ко́мнатный|dim=ко́мнатка|pej=комнатёнка|pej2=комнати́шка|dim2=комнату́шка}}
# 部屋。""",
        )
        self.assertEqual(
            page_data[0]["categories"], ["ロシア語", "ロシア語 名詞"]
        )
        self.assertEqual(page_data[0]["tags"], ["feminine", "inanimate"])
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "ко́мната", "tags": ["canonical"]},
                {"form": "kómnata", "tags": ["transliteration"]},
                {
                    "form": "ко́мнаты",
                    "tags": ["genitive", "nominative", "plural"],
                },
                {"form": "ко́мнат", "tags": ["genitive", "plural"]},
                {"form": "ко́мнатный", "tags": ["relational", "adjective"]},
                {"form": "ко́мнатка", "tags": ["diminutive"]},
                {"form": "комнату́шка"},
            ],
        )

    def test_de_noun_tag(self):
        self.wxr.wtp.add_page(
            "テンプレート:de-noun",
            10,
            """[[カテゴリ:ドイツ語]][[カテゴリ:ドイツ語 名詞]]<span lang="de" xml:lang="de">'''Silizium'''</span> <span class="gender n" title="neuter gender"><span>中性</span></span> (<span class="form-of genitive-form-of lang-de">属格'''<span lang="de" xml:lang="de">[[Siliziums]]</span>'''</span>, <span class="form-of plural-form-of lang-de">複数形無し</span>)""",
        )
        page_data = parse_page(
            self.wxr,
            "Silizium",
            """==ドイツ語==
===名詞===
{{de-noun|g=n|Siliziums|-}}
# [[珪素]]。""",
        )
        self.assertEqual(
            page_data[0]["forms"], [{"form": "Siliziums", "tags": ["genitive"]}]
        )
        self.assertEqual(page_data[0]["tags"], ["neuter", "no-plural"])

    def test_de_noun(self):
        self.wxr.wtp.add_page(
            "テンプレート:de-noun",
            10,
            """[[カテゴリ:ドイツ語]][[カテゴリ:ドイツ語 名詞]]<span lang="de" xml:lang="de">'''Montag'''</span> <span class="gender m" title="masculine gender"><span>男性</span></span> (<span class="form-of genitive-form-of lang-de">属格'''<span lang="de" xml:lang="de">[[Montages]]</span>'''<span class="form-of genitive-form-of lang-de"> 又は '''<span lang="de" xml:lang="de">[[Montags]]</span>'''</span></span>, <span class="form-of plural-form-of lang-de">複数形 '''<span lang="de" xml:lang="de">[[Montage]]</span>'''</span>)""",
        )
        page_data = parse_page(
            self.wxr,
            "Montag",
            """==ドイツ語==
===名詞===
{{de-noun|g=m|genitive=Montages|genitive2=Montags|plural=Montage}}
#[[月曜日]]。""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "Montages", "tags": ["genitive"]},
                {"form": "Montags", "tags": ["genitive"]},
                {"form": "Montage", "tags": ["plural"]},
            ],
        )
        self.assertEqual(page_data[0]["tags"], ["masculine"])
