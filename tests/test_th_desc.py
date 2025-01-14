import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThDesc(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def test_desc_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:desc",
            10,
            """<span class="desc-arr" title="borrowed">→</span> พม่า: <span class="Mymr" lang="{{{1}}}">[[{{{2}}}]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="my-Latn" class="tr Latn">{{{tr|}}}</span>, <span class="mention-gloss-double-quote">“</span><span class="mention-gloss">{{{t|}}}</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "สยาม",
            """== ภาษาไทย ==
=== คำคุณศัพท์ ===
# [[ของ]]ประเทศไทย (โบราณหรือปัจจุบัน)
===== คำสืบทอด =====
* {{desc|my|သျှမ်း|bor=1|t=Shan}}
* {{desc|pt|Sciam|bor=1}}
** {{desc|en|Siam|bor=1}}""",
        )
        self.assertEqual(
            page_data[0]["descendants"],
            [
                {
                    "lang": "พม่า",
                    "lang_code": "my",
                    "word": "သျှမ်း",
                    "sense": "Shan",
                },
                {
                    "lang": "โปรตุเกส",
                    "lang_code": "pt",
                    "word": "Sciam",
                    "descendants": [
                        {"lang": "อังกฤษ", "lang_code": "en", "word": "Siam"}
                    ],
                },
            ],
        )
