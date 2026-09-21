from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlEtymology(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_dog(self):
        # etymology texts should be added to both sense data
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>',
        )
        page_data = parse_page(
            self.wxr,
            "dog",
            """== dog ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (1.1) {{zool}} [[pies]]
''rzeczownik niepoliczalny''
: (2.1) {{kulin}} [[psi]]e [[mięso]]

===etymologia===
: Od średnioang. dogge
: por. szkoc. dug → pies""",
        )
        self.assertEqual(len(page_data), 2)
        self.assertEqual(
            page_data[0]["etymology_texts"], page_data[1]["etymology_texts"]
        )
        self.assertEqual(
            page_data[0]["etymology_texts"],
            ["Od średnioang. dogge", "por. szkoc. dug → pies"],
        )

    def test_sense_index(self):
        self.wxr.wtp.add_page(
            "Szablon:forma rzeczownika",
            10,
            "<i>rzeczownik, forma fleksyjna</i>[[Kategoria:Formy rzeczowników polskich]]",
        )
        data = parse_page(
            self.wxr,
            "jam",
            """== jam ({{język polski}}) ==
===znaczenia===
''zaimek''
: (1.1) ''…''[[ja]]'' z końcówką czasownikową''
''rzeczownik, rodzaj męskorzeczowy''
: (2.1) {{przest}} {{zob|dżem}}
''{{forma rzeczownika|pl}}''
: (3.1) {{D}} {{lm}} ''od'' [[jama]]
===etymologia===
: (1.1) pol. ja + -m
: (2.1) ang. jam → dżem""",
        )
        self.assertEqual(data[0]["etymology_texts"], ["pol. ja + -m"])
        self.assertEqual(data[1]["etymology_texts"], ["ang. jam → dżem"])
        self.assertTrue("etymology_texts" not in data[2])

    def test_links_follow_sense_indices_and_language(self):
        self.wxr.wtp.add_page(
            "Szablon:język polski", 10, '<span id="pl">język polski</span>'
        )
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span id="en">język angielski</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:pochodzenie-test",
            10,
            "[[ja#polski|ja]][[Kategoria:Pochodzenie polskie]]",
        )
        data = parse_page(
            self.wxr,
            "jam",
            """== jam ({{język polski}}) ==
===znaczenia===
''zaimek''
: (1.1) Zaimek.
''rzeczownik''
: (2.1) Dżem.
''rzeczownik''
: (3.1) Forma fleksyjna.
===etymologia===
: (1.1) Od {{pochodzenie-test}} i [[ja#polski|ja]].
: (2.1) Od [[jam#angielski|jam]].
== jam ({{język angielski}}) ==
===znaczenia===
''rzeczownik''
: (1.1) Inne znaczenie.""",
        )
        self.assertEqual(
            data[0]["etymology_links"],
            [("ja", "ja#polski"), ("ja", "ja#polski")],
        )
        self.assertEqual(data[1]["etymology_links"], [("jam", "jam#angielski")])
        self.assertNotIn("etymology_links", data[2])
        self.assertNotIn("etymology_links", data[3])

    def test_unlisted_links_inherited_from_base(self):
        data = parse_page(
            self.wxr,
            "dog",
            """== dog ({{język angielski}}) ==
===etymologia===
Od [[dogge#średnioangielski|dogge]], por. [[dug]].
===znaczenia===
''rzeczownik policzalny''
: (1.1) Pies.
''rzeczownik niepoliczalny''
: (2.1) Mięso.""",
        )
        self.assertEqual(len(data), 2)
        for entry in data:
            self.assertEqual(
                entry["etymology_links"],
                [("dogge", "dogge#średnioangielski"), ("dug", "dug")],
            )
