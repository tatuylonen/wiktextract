from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestFrDescendant(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"),
            WiktionaryConfig(
                dump_file_lang_code="fr",
                capture_language_codes=None,
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_derives_autres_langues_section_link(self):
        # https://fr.wiktionary.org/wiki/caligineux#Dérivés_dans_d’autres_langues
        self.wxr.wtp.add_page("Modèle:L", 10, "Anglais")
        data = parse_page(
            self.wxr,
            "eau",
            """== {{langue|frm}} ==
=== {{S|adjectif|frm}} ===
# Qui décrit une
==== {{S|dérivés autres langues}} ====
* {{L|en}} : [[caliginous#en|caliginous]]""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [{"word": "caliginous", "lang_code": "en", "lang": "Anglais"}],
        )

    def test_desc_ruby(self):
        self.wxr.wtp.add_page("Modèle:L", 10, "Japonais")
        self.wxr.wtp.add_page(
            "Modèle:ruby",
            10,
            """<ruby>櫛<rp> (</rp><rt>くし</rt><rp>) </rp></ruby>""",
        )
        data = parse_page(
            self.wxr,
            "髪梳",
            """== {{langue|ojp}} ==
=== {{S|nom|ojp}} ===
# [[peigne|Peigne]].
==== {{S|dérivés autres langues}} ====
* {{L|ja}} : {{lien|{{ruby|櫛|くし}}|ja|tr=kushi}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "Japonais",
                    "lang_code": "ja",
                    "roman": "kushi",
                    "ruby": [("櫛", "くし")],
                    "word": "櫛",
                }
            ],
        )

    def test_nested_desc_list(self):
        self.wxr.wtp.add_page(
            "Modèle:L",
            10,
            """{{#switch:{{{1}}}
| ota = Turc ottoman
| fr = Français
}}""",
        )
        data = parse_page(
            self.wxr,
            "گبر",
            """== {{langue|fa}} ==
=== {{S|nom|fa|num=1}} ===
# [[zoroastrien|Zoroastrien]].
==== {{S|dérivés autres langues}} ====
* {{L|ota}} : {{lien|كاور|ota|tr=gâvur}}
** {{L|fr}} : {{lien|gaure|fr}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "descendants": [
                        {"lang": "Français", "lang_code": "fr", "word": "gaure"}
                    ],
                    "lang": "Turc ottoman",
                    "lang_code": "ota",
                    "roman": "gâvur",
                    "word": "كاور",
                }
            ],
        )
