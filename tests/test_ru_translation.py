import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.page import parse_page
from wiktextract.extractor.ru.translation import extract_translations
from wiktextract.wxr_context import WiktextractContext


class TestRUTranslation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_translation_list(self):
        # https://ru.wiktionary.org/wiki/русский
        self.wxr.wtp.start_page("русский")
        self.wxr.wtp.add_page(
            "Шаблон:перев-блок",
            10,
            """{|
| относящийся к России, россиянам
|-
|
* [[Английский]]<sub>en</sub>: <span lang="en">[[Russian]]; ''относящийся к Киевской Руси'' [[Ruthenian]]</span>
* [[Итальянский]]<sub>it</sub>: <span lang="it">[[russo]]&nbsp;<sup>[[(it)]]</sup>&nbsp;<span title="форма (формы) мужского рода">''м.''</span></span>
* [[Китайский]]<sub>zh</sub> (традиц.): <span lang="">''письменный'' [[俄文]] (Éwén), ''устный'' [[俄語]] (Éyǔ)</span>
* [[Эсперанто]]<sup title='искусственный язык'>и</sup><sub>eo</sub>: <span lang="eo">[[rusa]]</span>
* [[Латинский]]<sub>la</sub>: <span lang="la">[[lingua Ruthenica]] <i title="форма женского рода">ж.</i>, [[lingua Russica]] <i title="форма женского рода">ж.</i></span>
|}""",  # noqa: E501
        )
        root = self.wxr.wtp.parse(
            """{{перев-блок|относящийся к России, россиянам
|en=[[Russian]]; ''относящийся к Киевской Руси'' [[Ruthenian]]
|it=[[ruso]]
|zh-tw=''письменный'' [[俄文]] (Éwén), ''устный'' [[俄語]] (Éyǔ)
|eo=[[rusa]]
|la=[[lingua Ruthenica]] {{f}}, [[lingua Russica]] {{f}}
}}"""
        )
        word_entry = WordEntry(word="русский", lang_code="ru", lang="Русский")
        extract_translations(self.wxr, word_entry, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in word_entry.translations
            ],
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "sense": "относящийся к России, россиянам",
                    "word": "Russian",
                },
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "sense": "относящийся к России, россиянам",
                    "raw_tags": ["относящийся к Киевской Руси"],
                    "word": "Ruthenian",
                },
                {
                    "lang": "Итальянский",
                    "lang_code": "it",
                    "sense": "относящийся к России, россиянам",
                    "tags": ["masculine"],
                    "word": "russo",
                },
                {
                    "lang": "Китайский",
                    "lang_code": "zh",
                    "sense": "относящийся к России, россиянам",
                    "tags": ["traditional", "Written-Form"],
                    "word": "俄文",
                    "roman": "Éwén",
                },
                {
                    "lang": "Китайский",
                    "lang_code": "zh",
                    "sense": "относящийся к России, россиянам",
                    "tags": ["colloquial"],
                    "word": "俄語",
                    "roman": "Éyǔ",
                },
                {
                    "lang": "Эсперанто",
                    "lang_code": "eo",
                    "sense": "относящийся к России, россиянам",
                    "raw_tags": ["искусственный язык"],
                    "word": "rusa",
                },
                {
                    "lang": "Латинский",
                    "lang_code": "la",
                    "sense": "относящийся к России, россиянам",
                    "tags": ["feminine"],
                    "word": "lingua Ruthenica",
                },
                {
                    "lang": "Латинский",
                    "lang_code": "la",
                    "sense": "относящийся к России, россиянам",
                    "tags": ["feminine"],
                    "word": "lingua Russica",
                },
            ],
        )

    def test_ja(self):
        self.wxr.wtp.add_page(
            "Шаблон:перев-блок",
            10,
            """{|
| влага, прозрачная бесцветная жидкость
|-
|
* [[ассамский#Русский|Ассамский]]<sub style='color:#33C066'>asm</sub>: <span lang="asm">[[জল#Ассамский|জল]]&nbsp;&#32;(jôl); [[পানী]] (pānī)</span>
* [[японский#Русский|Японский]]<sub style='color:#33C066'>ja</sub>: <span lang="ja">[[水#Японский|水]]&nbsp;<sup>[[:ja:水|(ja)]]</sup>&#32;([[みず]], mizú)</span>
</div>
|}""",
        )
        data = parse_page(
            self.wxr,
            "вода",
            """= {{-ru-}} =
== {{з|ударение=вода́}} ==
=== Морфологические и синтаксические свойства ===
==== Значение ====
# [[влага]]
=== Перевод ===
{{перев-блок|влага, прозрачная бесцветная жидкость
|asm={{t|asm|জল|tr=jôl}}; [[পানী]] (pānī)
|ja={{t|ja|水|tr=[[みず]], mizú}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "Ассамский",
                    "lang_code": "asm",
                    "roman": "jôl",
                    "sense": "влага, прозрачная бесцветная жидкость",
                    "word": "জল",
                },
                {
                    "lang": "Ассамский",
                    "lang_code": "asm",
                    "roman": "pānī",
                    "sense": "влага, прозрачная бесцветная жидкость",
                    "word": "পানী",
                },
                {
                    "lang": "Японский",
                    "lang_code": "ja",
                    "other": "みず",
                    "roman": "mizú",
                    "sense": "влага, прозрачная бесцветная жидкость",
                    "word": "水",
                },
            ],
        )
