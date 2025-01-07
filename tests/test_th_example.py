from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def test_ux(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ko-usex",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko">^파리는 ^프랑스의 '''서울'''이다.</i><dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn">Pari-neun Peurangseu-ui '''seour'''-ida.</i></dd><dd><span class="e-translation">ปารีสคือเมืองหลวงของฝรั่งเศส</span></dd></dl></div>[[Category:ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้|서울]]""",
        )
        page_data = parse_page(
            self.wxr,
            "서울",
            """== ภาษาเกาหลี ==
=== คำนาม ===
{{ko-noun}}

# [[เมืองหลวง]]; [[เมือง]][[ใหญ่]]
#: {{ko-usex|^파리-는 ^프랑스-의 '''서울'''-이다.|ปารีสคือเมืองหลวงของฝรั่งเศส}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้"],
                "glosses": ["เมืองหลวง; เมืองใหญ่"],
                "examples": [
                    {
                        "text": "^파리는 ^프랑스의 서울이다.",
                        "roman": "Pari-neun Peurangseu-ui seour-ida.",
                        "translation": "ปารีสคือเมืองหลวงของฝรั่งเศส",
                    }
                ],
            },
        )
