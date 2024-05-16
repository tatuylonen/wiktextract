from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.inflection import extract_inflection
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"), WiktionaryConfig(dump_file_lang_code="ru")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_adj_forms_table(self):
        self.maxDiff = None
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
<td rowspan="2" bgcolor="#EEF9FF">[[винительный|В.]]&nbsp;&nbsp;&nbsp;</td>
<td bgcolor="#EEF9FF">[[одушевлённый|одуш.]]</td>
<td bgcolor="#ffffff">ру́сского</td>
<td rowspan="2" bgcolor="#ffffff">ру́сское</td>
<td rowspan="2" bgcolor="#ffffff">ру́сскую</td>
<td bgcolor="#ffffff">ру́сских</td>
</tr>
<tr>
<td bgcolor="#EEF9FF">[[неодушевлённый|неод.]]</td>
<td bgcolor="#ffffff">ру́сский</td>
<td bgcolor="#ffffff">ру́сские</td>
</tr>
<tr>
<td colspan="2" bgcolor="#EEF9FF"> [[творительный|Т.]]</td>
<td>ру́сской ру́сскою</td>
</tr>
</table>""",
        )
        self.wxr.wtp.start_page("русский")
        root = self.wxr.wtp.parse("{{прил ru 3aX~}}")
        word_entry = WordEntry(
            word="русский", pos="adj", lang_code="ru", lang="Русский"
        )
        extract_inflection(self.wxr, word_entry, root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {
                    "form": "ру́сского",
                    "raw_tags": [
                        "единственное число",
                        "мужской род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сское",
                    "raw_tags": [
                        "единственное число",
                        "средний род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сскую",
                    "raw_tags": [
                        "единственное число",
                        "женский род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сских",
                    "raw_tags": [
                        "множественное число",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сский",
                    "raw_tags": [
                        "единственное число",
                        "мужской род",
                        "винительный",
                        "неодушевлённый",
                    ],
                },
                {
                    "form": "ру́сские",
                    "raw_tags": [
                        "множественное число",
                        "винительный",
                        "неодушевлённый",
                    ],
                },
                {
                    "form": "ру́сской",
                    "raw_tags": [
                        "единственное число",
                        "мужской род",
                        "творительный",
                    ],
                },
                {
                    "form": "ру́сскою",
                    "raw_tags": [
                        "единственное число",
                        "мужской род",
                        "творительный",
                    ],
                },
            ],
        )

    def test_noun_forms_table(self):
        self.maxDiff = None
        self.wxr.wtp.add_page(
            "Шаблон:сущ bg 7",
            10,
            """{| class="morfotable ru" cellpadding="3" rules="all"
! bgcolor="#eef9ff" | [[форма]]
! bgcolor="#eef9ff" | [[единственное число|ед.&nbsp;ч.]]
! bgcolor="#eef9ff" | [[множественное число|мн.&nbsp;ч.]]
|-
|-
| bgcolor="#eef9ff" | [[неопределённый|общая]]
| bgcolor="#ffffff" | публицист
| bgcolor="#ffffff" | публицисти
|-
| bgcolor="#eef9ff" | [[определённый|опред.]]
| bgcolor="#ffffff" | публициста <br>публицистът
| bgcolor="#ffffff" | публицистите
|-
| bgcolor="#eef9ff" | [[счётная форма|счётн.]]</td>
| colspan="2" bgcolor="#ffffff"  | публициста
|-
| bgcolor="#eef9ff" | [[звательный|зват.]]
| colspan="2" bgcolor="#ffffff" align="center" | —
|}[[Категория:Болгарские существительные]]
<b>публицист</b>

Существительное, мужской род, склонение 7.[[Категория:Болгарские существительные, склонение 7]][[Категория:Мужской род/bg]]]""",
        )
        self.wxr.wtp.start_page("публицист")
        root = self.wxr.wtp.parse("{{сущ bg 7|публицист}}")
        word_entry = WordEntry(
            word="публицист", pos="noun", lang_code="bg", lang="Болгарский"
        )
        extract_inflection(self.wxr, word_entry, root)
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
