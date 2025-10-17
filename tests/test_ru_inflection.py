from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.page import (
    extract_morphological_section,
    parse_page,
)
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
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

    def test_adj_forms_table(self):
        self.wxr.wtp.add_page(
            "Шаблон:прил ru 3aX~",
            10,
            """<table>
<tr>
<th colspan="2" rowspan="2">[[падеж]]</th>
<th colspan="3"> [[единственное число|ед. ч.]]</th>
<th rowspan="2"> [[множественное число|мн. ч.]]</th>
</tr>
<tr>
<th> [[мужской род|муж.&nbsp;р.]] </th>
<th> [[средний род|ср.&nbsp;р.]] </th>
<th> [[женский род|жен.&nbsp;р.]] </th>
</tr>
<tr>
<th rowspan="2">[[винительный|В.]]&nbsp;&nbsp;&nbsp;</th>
<th>[[одушевлённый|одуш.]]</th><td>ру́сского</td><td rowspan="2">ру́сское</td><td rowspan="2">ру́сскую</td><td>ру́сских</td>
</tr>
<tr>
<th>[[неодушевлённый|неод.]]</th>
<td>ру́сский</td>
<td>ру́сские</td>
</tr>
<tr>
<th colspan="2"> [[творительный|Тв.]]</th><td>ру́сской<br>ру́сскою</td>
</tr>
</table>""",
        )
        self.wxr.wtp.start_page("русский")
        root = self.wxr.wtp.parse("{{прил ru 3aX~}}")
        word_entry = WordEntry(
            word="русский", pos="adj", lang_code="ru", lang="Русский"
        )
        extract_morphological_section(self.wxr, [word_entry], root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {
                    "form": "ру́сского",
                    "tags": ["singular", "masculine", "accusative", "animate"],
                },
                {
                    "form": "ру́сское",
                    "tags": [
                        "singular",
                        "neuter",
                        "accusative",
                        "animate",
                        "inanimate",
                    ],
                },
                {
                    "form": "ру́сскую",
                    "tags": [
                        "singular",
                        "feminine",
                        "accusative",
                        "animate",
                        "inanimate",
                    ],
                },
                {
                    "form": "ру́сских",
                    "tags": ["plural", "accusative", "animate"],
                },
                {
                    "form": "ру́сский",
                    "tags": [
                        "singular",
                        "masculine",
                        "accusative",
                        "inanimate",
                    ],
                },
                {
                    "form": "ру́сские",
                    "tags": ["plural", "accusative", "inanimate"],
                },
                {
                    "form": "ру́сской",
                    "tags": ["singular", "masculine", "instrumental"],
                },
                {
                    "form": "ру́сскою",
                    "tags": ["singular", "masculine", "instrumental"],
                },
            ],
        )

    def test_noun_forms_table(self):
        self.wxr.wtp.add_page(
            "Шаблон:сущ bg 7",
            10,
            """{| class="morfotable ru" cellpadding="3" rules="all"
! bgcolor="#eef9ff" | [[форма]]
! bgcolor="#eef9ff" | [[единственное число|ед.&nbsp;ч.]]
! bgcolor="#eef9ff" | [[множественное число|мн.&nbsp;ч.]]
|-
|-
! bgcolor="#eef9ff" | [[неопределённый|общая]]
| bgcolor="#ffffff" | публицист
| bgcolor="#ffffff" | публицисти
|-
! bgcolor="#eef9ff" | [[определённый|опред.]]
| bgcolor="#ffffff" | публициста <br>публицистът
| bgcolor="#ffffff" | публицистите
|-
! bgcolor="#eef9ff" | [[счётная форма|счётн.]]</td>
| colspan="2" bgcolor="#ffffff"  | публициста
|-
| bgcolor="#eef9ff" | [[звательный|зват.]]
| colspan="2" bgcolor="#ffffff" align="center" | —
|}[[Категория:Болгарские существительные]]
<b>публицист</b>

Существительное, мужской род, склонение 7.[[Категория:Болгарские существительные, склонение 7]][[Категория:Мужской род/bg]]]""",  # noqa: E501
        )
        self.wxr.wtp.start_page("публицист")
        root = self.wxr.wtp.parse("{{сущ bg 7|публицист}}")
        word_entry = WordEntry(
            word="публицист", pos="noun", lang_code="bg", lang="Болгарский"
        )
        extract_morphological_section(self.wxr, [word_entry], root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {"form": "публицист", "tags": ["indefinite", "singular"]},
                {"form": "публицисти", "tags": ["indefinite", "plural"]},
                {"form": "публициста", "tags": ["definite", "singular"]},
                {"form": "публицистът", "tags": ["definite", "singular"]},
                {"form": "публицистите", "tags": ["definite", "plural"]},
                {"form": "публициста", "tags": ["count-form", "singular"]},
            ],
        )

    def test_verb_table(self):
        self.wxr.wtp.add_page(
            "Шаблон:гл ru 5a-т",
            10,
            """{| rules="all" class="morfotable ru"
! bgcolor="#EEF9FF" | &#160;
! bgcolor="#EEF9FF" | [[настоящее время|наст.]]
! bgcolor="#EEF9FF" | [[прошедшее время|прош.]]
! bgcolor="#EEF9FF" | [[повелительное наклонение|повелит.]]
|-
| bgcolor="#EEF9FF" align="right" | [[он|Он]]<br />[[она|Она]]<br />[[оно|Оно]]
| ви́дит
| ви́дел<br />ви́дела<br />ви́дело
| align="center" | —
|-
<tr>
<td bgcolor="#EEF9FF" align="right">[[деепричастие|Деепр.]] [[прошедшее время|прош.]]</td>
<td colspan="3" align="center">[[видев#ви́дев|ви́дев]], [[видевши#ви́девши|ви́девши]]</td>
</tr>
<tr>
<td bgcolor="#EEF9FF" align="right">[[будущее время|Будущее]]</td>
<td colspan="3" align="center">буду/будешь… ви́деть</td>
</tr>
|}""",  # noqa: E501
        )
        self.wxr.wtp.start_page("видеть")
        root = self.wxr.wtp.parse("{{гл ru 5a-т}}")
        word_entry = WordEntry(
            word="видеть", pos="verb", lang_code="ru", lang="Русский"
        )
        extract_morphological_section(self.wxr, [word_entry], root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {
                    "form": "ви́дит",
                    "tags": ["third-person", "singular", "present"],
                },
                {"form": "ви́дел", "tags": ["third-person", "singular", "past"]},
                {
                    "form": "ви́дела",
                    "tags": ["third-person", "singular", "past"],
                },
                {
                    "form": "ви́дело",
                    "tags": ["third-person", "singular", "past"],
                },
                {"form": "ви́дев", "tags": ["adverbial", "past"]},
                {"form": "ви́девши", "tags": ["adverbial", "past"]},
                {"form": "буду/будешь… ви́деть", "tags": ["future"]},
            ],
        )

    def test_падежи_cu(self):
        self.wxr.wtp.add_page(
            "Шаблон:сущ cu (-а)",
            10,
            """{|
! bgcolor="#EEF9FF" | [[падеж]]
! bgcolor="#EEF9FF" | [[единственное число|ед. ч.]]
! bgcolor="#EEF9FF" | [[двойственное число|дв. ч.]]
! bgcolor="#EEF9FF" | [[множественное число|мн. ч.]]
|-
! bgcolor="#EEF9FF" | [[местный|М.]]
| lang="cu" | водѣ
| lang="cu" | водѹ
| lang="cu" | водахъ
<tr>
<th bgcolor="#EEF9FF"> [[звательный|Зв.]]</th>
<td lang="cu"> водо
<td align="center"> — </td>
<td align="center"> — </td>
</tr>
|}""",
        )
        self.wxr.wtp.start_page("вода")
        root = self.wxr.wtp.parse("{{сущ cu (-а)}}")
        word_entry = WordEntry(
            word="вода", pos="noun", lang_code="cu", lang="Старославянский"
        )
        extract_morphological_section(self.wxr, [word_entry], root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {"form": "водѣ", "tags": ["locative", "singular"]},
                {"form": "водѹ", "tags": ["locative", "dual"]},
                {"form": "водахъ", "tags": ["locative", "plural"]},
                {"form": "водо", "tags": ["vocative", "singular"]},
            ],
        )

    def test_comparative_forms(self):
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.wxr.wtp.add_page(
            "Шаблон:прил ru 1*a",
            10,
            "[[прилагательное|Прилагательное]], [[качественное прилагательное|качественное]], тип склонения по [[Викисловарь:Использование словаря Зализняка|классификации А.&#160;Зализняка]]&#160;— 1*a. Сравнительная степень&nbsp;— ''[[опаснее#опа́снее|опа́снее]], [[опасней#опа́сней|опа́сней]].''",
        )
        data = parse_page(
            self.wxr,
            "опасный",
            """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{прил ru 1*a
|основа=опа́сн
|основа1=опа́сен
|тип=качественное
|слоги={{по слогам|о|.|па́с|ный}}
|степень=1
|краткая=
}}
=== Семантические свойства ===
==== Значение ====
# [[способный]] причинить [[вред]], угрожающий [[несчастье]]м {{пример|}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "опа́снее", "tags": ["comparative"]},
                {"form": "опа́сней", "tags": ["comparative"]},
            ],
        )

    def test_спряжения(self):
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.wxr.wtp.add_page(
            "Шаблон:гл ru 1a",
            10,
            """<table class="morfotable ru" cellpadding="2" rules="all">
<tr>
<th colspan="3">[[настоящее время|Настоящее время]]</th>
</tr><tr>
<th></th>
<th align="center">[[единственное число|ед. число]]</th>
<th align="center">[[множественное число|мн. число]]</th>
</tr>
<tr>
<th>[[первое лицо|1-е лицо]]</th>
<td>пры́гаю</td>
<td>пры́гаем</td>
</tr>
<tr>
<th colspan="3">[[деепричастие|Деепричастия]]</th>
</tr>
<tr><th align="right">[[настоящее время|наст. вр.]]</th>
<td colspan="2">[[прыгая#пры́гая|пры́гая]]</td>
</tr>
<tr>
<th align="right">[[прошедшее время|прош. вр.]]</th>
<td colspan="2">[[прыгав#пры́гав|пры́гав]], [[прыгавши#пры́гавши|пры́гавши]]</td>
</tr>
</table>""",
        )
        data = parse_page(
            self.wxr,
            "прыгать",
            """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{гл ru 1a
|основа=пры́га
|слоги={{по-слогам|пры́|гать}}
|НП=1
|соотв={{без ссылок|приставочные типа}} запры́гать, пропры́гать
|дореф=
}}
=== Семантические свойства ===
==== Значение ====
# совершать прыжок""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "пры́гаю",
                    "tags": ["present", "singular", "first-person"],
                },
                {
                    "form": "пры́гаем",
                    "tags": ["present", "plural", "first-person"],
                },
                {
                    "form": "пры́гая",
                    "tags": ["adverbial", "participle", "present"],
                },
                {"form": "пры́гав", "tags": ["adverbial", "participle", "past"]},
                {
                    "form": "пры́гавши",
                    "tags": ["adverbial", "participle", "past"],
                },
            ],
        )
