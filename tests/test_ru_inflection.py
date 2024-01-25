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
<td bgcolor="#ffffff">ру́сской ру́сскою</td>
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
                    "tags": [
                        "единственное число",
                        "мужской род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сское",
                    "tags": [
                        "единственное число",
                        "средний род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сскую",
                    "tags": [
                        "единственное число",
                        "женский род",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сских",
                    "tags": [
                        "множественное число",
                        "винительный",
                        "одушевлённый",
                    ],
                },
                {
                    "form": "ру́сский",
                    "tags": [
                        "единственное число",
                        "мужской род",
                        "винительный",
                        "неодушевлённый",
                    ],
                },
                {
                    "form": "ру́сские",
                    "tags": [
                        "множественное число",
                        "винительный",
                        "неодушевлённый",
                    ],
                },
                {
                    "form": "ру́сской",
                    "tags": [
                        "единственное число",
                        "мужской род",
                        "творительный",
                    ],
                },
                {
                    "form": "ру́сскою",
                    "tags": [
                        "единственное число",
                        "мужской род",
                        "творительный",
                    ],
                },
            ],
        )
