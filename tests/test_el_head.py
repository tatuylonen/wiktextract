from unittest import TestCase

from wikitextprocessor import WikiNode, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import Form, WordEntry
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

    def mktest_form(self, received, expected):
        # Similar to test_el_inflection::mktest_form
        def normalize_forms(lst):
            for form in lst:
                if "raw_tags" in form:
                    form["raw_tags"].sort()
                if "source" in form:
                    del form["source"]
                if "tags" in form:
                    del form["tags"]

        normalize_forms(received)
        normalize_forms(expected)

        self.assertEqual(received, expected)

    def get_forms(
        self,
        raw: str,
        *,
        # These should not be important for testing
        word: str = "word_filler",
        lang: str = "Greek",
        lang_code: str = "el",
    ) -> list[Form]:
        # Similar to test_el_inflection::xinfl
        data = WordEntry(lang=lang, lang_code=lang_code, word=word)
        tree = self.wxr.wtp.parse(raw)
        pos_node = tree.children[0]
        assert isinstance(pos_node, WikiNode)
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        dumped = data.model_dump(exclude_defaults=True)
        forms = dumped["forms"]
        return forms

    def test_el_head1(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        raw = """==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' ''ή'' '''[[φωσφόρος]]''' (''αρσενικό'') ''και'' '''[[φώσφορο]]''' (''ουδέτερο'')
* foo
"""
        received = self.get_forms(raw)
        expected = [
            {"form": "φώσφορος", "raw_tags": ["αρσενικό"]},
            {"form": "φωσφόρος", "raw_tags": ["αρσενικό"]},
            {"form": "φώσφορο", "raw_tags": ["ουδέτερο"]},
        ]
        self.mktest_form(received, expected)

    def test_el_head_dash_before_template(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        raw = """==={{ουσιαστικό|el}}===
-'''{{PAGENAME}}'''
* foo
"""
        received = self.get_forms(raw)
        expected = [
            {"form": "-φώσφορος"},
        ]
        self.mktest_form(received, expected)

    def test_el_with_colon_list(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        raw = """==={{ουσιαστικό|el}}===
: '''{{PAGENAME}}'''
* foo
"""
        received = self.get_forms(raw)
        expected = [
            {"form": "φώσφορος"},
        ]
        self.mktest_form(received, expected)

    def test_en_head1(self) -> None:
        self.wxr.wtp.start_page("free")
        raw = """==={{επίθετο|en}}===
'''{{PAGENAME}}''' (en)
# foo"""
        received = self.get_forms(raw, lang_code="en")
        expected = [
            {"form": "free"},
        ]
        self.mktest_form(received, expected)

    def test_el_interrupted_punctuation(self) -> None:
        # https://el.wiktionary.org/wiki/ξεχαρβαλώνω
        self.wxr.wtp.start_page("ξεχαρβαλώνω")
        raw = """===Ρήμα===
'''ξεχαρβαλώνω''', ''[[foo]].'': '''ξεχαρβάλωσα''', ''[[foo.bar]]:'' '''[[ξεχαρβαλώνομαι]]''', ''[[f.bar]].:'' '''[[ξεχαρβαλώθηκα]]''', ''[[foo.b.b]].:'' '''[[ξεχαρβαλωμένος]]'''
* foo
"""
        received = self.get_forms(raw)
        expected = [
            {"form": "ξεχαρβαλώνω"},
            {"form": "ξεχαρβάλωσα", "raw_tags": ["foo"]},
            {"form": "ξεχαρβαλώνομαι", "raw_tags": ["foo.bar"]},
            {"form": "ξεχαρβαλώθηκα", "raw_tags": ["f.bar"]},
            {"form": "ξεχαρβαλωμένος", "raw_tags": ["foo.b.b"]},
        ]
        self.mktest_form(received, expected)

    def test_form_parsing_verbs(self) -> None:
        # Test that particles (θα) are properly merged to verb forms.
        # Note: seems that only θα can appear (no να etc.).
        # https://el.wiktionary.org/wiki/Πρότυπο:el-ρήμα
        #
        # '''{{PAGENAME}}'''{{el-ρήμα|έψαχνα|ψάξω|έψαξα|ψάχνομαι|ψαγμένος|π-αορ=ψάχτηκα}}
        # Expanded via 'wxr.wtp.node_to_text(node)' at the start of 'process_pos'
        self.wxr.wtp.start_page("ψάχνω")
        raw = """===Ρήμα===
'''ψάχνω''', ''πρτ.'': '''έψαχνα''', ''στ.μέλλ.'': θα '''ψάξω''', ''αόρ.'': '''έψαξα''', ''παθ.φωνή:'' '''[[ψάχνομαι]]''', ''π.αόρ.:'' '''ψάχτηκα''', ''μτχ.π.π.:'' '''[[ψαγμένος]]'''
* foo
"""
        received = self.get_forms(raw)
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
        self.mktest_form(received, expected)

    def test_parsing_logio(self) -> None:
        # https://el.wiktionary.org/wiki/αιδώς
        # Test that logio (literary) is correctly parsed
        self.wxr.wtp.add_page("Πρότυπο:-el-", 10, "Νέα ελληνικά (el)")
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

        raw = """=={{-el-}}==
==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' {{θεν}} {{ετ|λόγιο}}
* foo
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

        self.mktest_form(received, expected)

    def test_parsing_forms_and_tags(self) -> None:
        # https://el.wiktionary.org/wiki/γάιδαρος
        self.wxr.wtp.add_page("Πρότυπο:-el-", 10, "Νέα ελληνικά (el)")
        self.wxr.wtp.add_page("Πρότυπο:ουσιαστικό", 10, "Ουσιαστικό")
        self.wxr.wtp.add_page(
            "Πρότυπο:α",
            10,
            """<span style="background:#ffffff; color:#002000;">''αρσενικό''</span>""",
        )
        self.wxr.wtp.add_page(
            "Πρότυπο:θ",
            10,
            """(<span style="background:#ffffff; color:#002000;">''θηλυκό''</span> '''[[γαϊδάρα]]'''&nbsp;''ή''  '''[[γαϊδούρα]]''')""",
        )

        raw = """=={{-el-}}==
==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' {{α}} {{θ|γαϊδάρα|ή=γαϊδούρα}}
* foo
"""
        word = "γάιδαρος"
        page_datas = parse_page(self.wxr, word, raw)
        received = page_datas[0]["forms"]

        expected = [
            {"form": "γάιδαρος", "raw_tags": ["αρσενικό"]},
            {"form": "γαϊδάρα", "raw_tags": ["θηλυκό"]},
            {"form": "γαϊδούρα", "raw_tags": ["θηλυκό"]},
        ]

        self.mktest_form(received, expected)
