from unittest import TestCase

from wikitextprocessor import WikiNode, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.page import parse_page
from wiktextract.extractor.el.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


class TestElHeader(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="el"),
            WiktionaryConfig(
                dump_file_lang_code="el",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_el_head1(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        data = WordEntry(lang="Greek", lang_code="el", word="φώσφορος")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' ''ή'' '''[[φωσφόρος]]''' (''αρσενικό'') ''και'' '''[[φώσφορο]]''' (''ουδέτερο'')
* foo
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "φώσφορος", "raw_tags": ["αρσενικό"]},
            {"form": "φωσφόρος", "raw_tags": ["αρσενικό"]},
            {"form": "φώσφορο", "raw_tags": ["ουδέτερο"]},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_el_head_dash_before_template(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        data = WordEntry(lang="Greek", lang_code="el", word="φώσφορος")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|el}}===
-'''{{PAGENAME}}'''
* foo
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "-φώσφορος"},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_el_with_colon_list(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        data = WordEntry(lang="Greek", lang_code="el", word="φώσφορος")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|el}}===
: '''{{PAGENAME}}'''
* foo
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "φώσφορος"},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_en_head1(self) -> None:
        self.wxr.wtp.start_page("free")
        data = WordEntry(lang="Greek", lang_code="en", word="free")
        root = self.wxr.wtp.parse(
            """==={{επίθετο|en}}===
'''{{PAGENAME}}''' (en)
# foo"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "free"},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_el_interrupted_punctuation(self) -> None:
        # For example https://el.wiktionary.org/wiki/%CE%BE%CE%B5%CF%87%CE%B1%CF%81%CE%B2%CE%B1%CE%BB%CF%8E%CE%BD%CF%89
        self.wxr.wtp.start_page("ξεχαρβαλώνω")
        data = WordEntry(lang="Greek", lang_code="el", word="ξεχαρβαλώνω")
        root = self.wxr.wtp.parse(
            """===Ρήμα===
'''ξεχαρβαλώνω''', ''[[foo]].'': '''ξεχαρβάλωσα''', ''[[foo.bar]]:'' '''[[ξεχαρβαλώνομαι]]''', ''[[f.bar]].:'' '''[[ξεχαρβαλώθηκα]]''', ''[[foo.b.b]].:'' '''[[ξεχαρβαλωμένος]]'''
* foo
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "ξεχαρβαλώνω"},
            {"form": "ξεχαρβάλωσα", "raw_tags": ["foo"]},
            {"form": "ξεχαρβαλώνομαι", "raw_tags": ["foo.bar"]},
            {"form": "ξεχαρβαλώθηκα", "raw_tags": ["f.bar"]},
            {"form": "ξεχαρβαλωμένος", "raw_tags": ["foo.b.b"]},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_form_parsing_verbs(self) -> None:
        # Test that particles (θα) are properly merged to verb forms.
        # Note: seems that only θα can appear (no να etc.).
        # https://el.wiktionary.org/wiki/Πρότυπο:el-ρήμα
        word = "ψάχνω"
        self.wxr.wtp.start_page(word)
        data = WordEntry(lang="Greek", lang_code="el", word=word)
        # '''{{PAGENAME}}'''{{el-ρήμα|έψαχνα|ψάξω|έψαξα|ψάχνομαι|ψαγμένος|π-αορ=ψάχτηκα}}
        # Expanded via 'wxr.wtp.node_to_text(node)' at the start of 'process_pos'
        root = self.wxr.wtp.parse(
            """===Ρήμα===
'''ψάχνω''', ''πρτ.'': '''έψαχνα''', ''στ.μέλλ.'': θα '''ψάξω''', ''αόρ.'': '''έψαξα''', ''παθ.φωνή:'' '''[[ψάχνομαι]]''', ''π.αόρ.:'' '''ψάχτηκα''', ''μτχ.π.π.:'' '''[[ψαγμένος]]'''
* foo
"""
        )
        pos_node = root.children[0]
        assert isinstance(pos_node, WikiNode)
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        dumped = data.model_dump(exclude_defaults=True)

        expected = [
            {"form": "ψάχνω"},
            {"form": "έψαχνα", "raw_tags": ["πρτ."]},
            # Should not have "tha"
            {"form": "ψάξω", "raw_tags": ["στ.μέλλ."]},
            {
                "form": "έψαξα",
                "raw_tags": ["αόρ.", "μτχ.π.π.:", "π.αόρ.:", "παθ.φωνή:"],
            },
            {
                "form": "ψάχνομαι",
                "raw_tags": ["αόρ.", "μτχ.π.π.:", "π.αόρ.:", "παθ.φωνή:"],
            },
            {
                "form": "ψάχτηκα",
                "raw_tags": ["αόρ.", "μτχ.π.π.:", "π.αόρ.:", "παθ.φωνή:"],
            },
            {
                "form": "ψαγμένος",
                "raw_tags": ["αόρ.", "μτχ.π.π.:", "π.αόρ.:", "παθ.φωνή:"],
            },
        ]
        self.assertEqual(dumped.get("forms"), expected)

    def test_parsing_logio(self) -> None:
        # https://el.wiktionary.org/wiki/αιδώς
        # Test that logio (literary) is correctly parsed
        self.wxr.wtp.add_page("Πρότυπο:-el-", 10, "Greek")
        self.wxr.wtp.add_page("Πρότυπο:ουσιαστικό", 10, "Ουσιαστικό")
        self.wxr.wtp.add_page(
            "Πρότυπο:ετ",
            10,
            """([[:Κατηγορία:Λόγιοι όροι (νέα ελληνικά)|<i>λόγιο</i>]])[[Κατηγορία:Λόγιοι όροι  (νέα ελληνικά)]]""",
        )
        self.wxr.wtp.add_page(
            "Πρότυπο:θεν",
            10,
            """<span style="background:#ffffff; color:#002000;">''θηλυκό, μόνο στον ενικό''</span>""",
        )
        self.wxr.wtp.add_page(
            "Πρότυπο:κλείδα-ελλ",
            10,
            """[[Κατηγορία:Αντίστροφο λεξικό (ελληνικά)|σωδια]]""",
        )

        raw = """=={{-el-}}==
==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' {{θεν}} {{ετ|λόγιο}}
"""
        word = "αιδώς"
        page_datas = parse_page(self.wxr, word, raw)
        received = page_datas[0]["forms"]

        expected = [
            {
                "form": "αιδώς",
                "raw_tags": ["θηλυκό", "λόγιο", "μόνο στον ενικό"],
            },
        ]

        self.assertEqual(received, expected)
