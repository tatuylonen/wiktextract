from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.models import Sound, WordEntry
from wiktextract.extractor.ja.page import parse_page
from wiktextract.extractor.ja.sound import extract_sound_section
from wiktextract.wxr_context import WiktextractContext


class TestJaSound(TestCase):
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

    def test_en_sounds(self):
        self.wxr.wtp.start_page("puppy")
        self.wxr.wtp.add_page(
            "テンプレート:IPA",
            10,
            '[[w:国際音声記号|IPA]]: <span class="IPA">/ˈpə.pi/</span>, <span class="IPA">/ˈpʌp.i/</span>[[カテゴリ: 国際音声記号あり]]',
        )
        self.wxr.wtp.add_page(
            "テンプレート:X-SAMPA",
            10,
            '[[w:X-SAMPA|X-SAMPA]]:&nbsp;<span title="X-SAMPA pronunciation">/<span class="SAMPA">"p@.pi</span>/, /<span class="SAMPA">"pVp.i</span>/</span>',
        )
        self.wxr.wtp.add_page(
            "テンプレート:X-SAMPA",
            10,
            '<table class="audiotable"><tr><td class="unicode audiolink" style="padding-right:5px; padding-left: 0;">音声 (米)<td class="audiofile">[[File:en-us-puppy.ogg|noicon|175px]]</td><td class="audiometa" style="font-size: 80%;">([[:File:en-us-puppy.ogg|ファイル]])</td></tr></table>[[カテゴリ:英語 音声リンクがある語句|PUPPY]]',
        )
        data = WordEntry(lang="英語", lang_code="en", word="puppy")
        root = self.wxr.wtp.parse("""===発音===
* {{IPA|ˈpə.pi|ˈpʌp.i}}
* {{X-SAMPA|"p@.pi|"pVp.i}}
* {{音声|en|en-us-puppy.ogg|音声 (米)}}""")
        extract_sound_section(self.wxr, [], data, root.children[0])
        self.assertEqual(
            data.categories, ["国際音声記号あり", "英語 音声リンクがある語句"]
        )
        self.assertEqual(
            data.sounds[:4],
            [
                Sound(ipa="ˈpə.pi"),
                Sound(ipa="ˈpʌp.i"),
                Sound(ipa='"p@.pi', tags=["X-SAMPA"]),
                Sound(ipa='"pVp.i', tags=["X-SAMPA"]),
            ],
        )
        self.assertEqual(data.sounds[4].audio, "en-us-puppy.ogg")
        self.assertEqual(data.sounds[4].raw_tags, ["音声 (米)"])

    def test_ja_pron(self):
        self.wxr.wtp.start_page("日本語")
        self.wxr.wtp.add_page(
            "テンプレート:ja-pron",
            10,
            """*<span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">[[w:東京式アクセント|東京式]]</span><span class="ib-brac qualifier-brac">)</span> <span lang="ja" class="Jpan">に<span style="border-top:1px solid black">ほんご</span></span> <span class="Latn"><samp>[nìhóńgó]</samp></span> ([[平板型]] – [0])
*[[w:国際音声記号|IPA]]<sup>([[付録:日本語の発音表記|?]])</sup>:&#32;<span class="IPA">[ɲ̟ihõ̞ŋɡo̞]</span>[[カテゴリ:日本語 国際音声記号あり|にほんこ にほんご]]
* <table class="audiotable"><tr><td class="unicode audiolink">音声</td><td class="audiofile">[[Image:Ja-nihongo.ogg|noicon|175px]]</td><td class="audiometa" style="font-size: 80%;">([[:Image:Ja-nihongo.ogg|file]])</td></tr></table>[[Category:日本語 音声リンクがある語句|にほんこ にほんご]]""",
        )
        data = WordEntry(lang="日本語", lang_code="ja", word="日本語")
        root = self.wxr.wtp.parse("""===発音===
{{ja-pron|にほんご|acc=0|a=Ja-nihongo.ogg}}""")
        extract_sound_section(self.wxr, [], data, root.children[0])
        self.assertEqual(
            data.sounds[:2],
            [
                Sound(
                    roman="[nìhóńgó]",
                    form="にほんご",
                    raw_tags=["東京式"],
                    tags=["Heiban"],
                ),
                Sound(ipa="[ɲ̟ihõ̞ŋɡo̞]"),
            ],
        )
        self.assertEqual(data.sounds[2].audio, "Ja-nihongo.ogg")

    def test_sound_under_pos(self):
        self.wxr.wtp.add_page(
            "テンプレート:ja-pron",
            10,
            '*[[w:国際音声記号|IPA]]<sup>([[付録:日本語の発音表記|?]])</sup>:&#32;<span class="IPA">[iɾo̞]</span>',
        )
        data = parse_page(
            self.wxr,
            "いろ",
            """==日本語==
===名詞===
# gloss 1
====発音====
{{ja-pron|acc=2}}

===動詞===
# gloss 2""",
        )
        self.assertEqual(data[0]["senses"], [{"glosses": ["gloss 1"]}])
        self.assertEqual(data[0]["sounds"], [{"ipa": "[iɾo̞]"}])
        self.assertEqual(data[1]["senses"], [{"glosses": ["gloss 2"]}])
        self.assertTrue("sounds" not in data[1])

    def test_wiki_link_homophones(self):
        self.wxr.wtp.start_page("lice")
        root = self.wxr.wtp.parse("""===発音===
* {{homophones|lang=fr|[[lis]]/[[lys]]}}""")
        base_data = WordEntry(word="lice", lang_code="fr", lang="フランス語")
        page_data = [base_data.model_copy(deep=True)]
        extract_sound_section(self.wxr, page_data, base_data, root.children[0])
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(data["sounds"], [{"homophones": ["lis/lys"]}])

    def test_ja_accent_common_template(self):
        self.wxr.wtp.start_page("豆乳")
        self.wxr.wtp.add_page(
            "テンプレート:ja-accent-common",
            10,
            """*([[w:京阪式アクセント|京阪式]])&nbsp;<span lang="ja" xml:lang="ja"><span>とーにゅー</span></span>""",
        )
        root = self.wxr.wtp.parse("""===発音===
{{ja-accent-common|region=京阪|h||とーにゅー}}""")
        base_data = WordEntry(word="豆乳", lang_code="ja", lang="日本語")
        page_data = [base_data.model_copy(deep=True)]
        extract_sound_section(self.wxr, page_data, base_data, root.children[0])
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"], [{"form": "とーにゅー", "raw_tags": ["京阪式"]}]
        )

    def test_ja_accent_common_template_two_span_tags(self):
        self.wxr.wtp.start_page("まぜる")
        self.wxr.wtp.add_page(
            "テンプレート:ja-accent-common",
            10,
            """*([[w:京阪式アクセント|京阪式]])&nbsp;<span lang="ja" xml:lang="ja">まぜ<span>る</span></span>""",
        )
        root = self.wxr.wtp.parse("""===発音===
{{ja-accent-common|region=京阪|h|まぜ|る}}""")
        base_data = WordEntry(word="まぜる", lang_code="ja", lang="日本語")
        page_data = [base_data.model_copy(deep=True)]
        extract_sound_section(self.wxr, page_data, base_data, root.children[0])
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"], [{"form": "まぜる", "raw_tags": ["京阪式"]}]
        )

    def test_magic_word_in_template_param(self):
        self.wxr.wtp.start_page("Aluminium")
        root = self.wxr.wtp.parse("""===発音===
* {{音声|de|De-{{PAGENAME}}.ogg|音声（ドイツ）}}""")
        base_data = WordEntry(word="Aluminium", lang_code="de", lang="ドイツ語")
        page_data = [base_data.model_copy(deep=True)]
        extract_sound_section(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(base_data.sounds[0].audio, "De-Aluminium.ogg")

    def test_zh_sounds(self):
        self.wxr.wtp.start_page("議論")
        self.wxr.wtp.add_page("テンプレート:nan", 10, "閩南語")
        root = self.wxr.wtp.parse("""===発音===
*注音符号: ㄧˋ　ㄌㄨㄣˋ
*{{nan}}: gī-lūn""")
        base_data = WordEntry(word="議論", lang_code="zh", lang="中国語")
        page_data = [base_data.model_copy(deep=True)]
        extract_sound_section(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in base_data.sounds],
            [
                {"zh_pron": "ㄧˋ　ㄌㄨㄣˋ", "tags": ["Bopomofo"]},
                {"zh_pron": "gī-lūn", "tags": ["Min-Nan"]},
            ],
        )
