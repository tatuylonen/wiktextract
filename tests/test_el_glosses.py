from typing import Any
from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


def raw_trim(raw: str) -> str:
    return "\n".join(line.strip() for line in raw.strip().split("\n"))


class TestElGlosses(TestCase):
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

    def mktest_bl_linkage(self, raw: str, expected: list[Any]) -> None:
        """Test βλ-linkage parsing in glosses.

        Reference:
        https://el.wiktionary.org/wiki/Πρότυπο:βλ

        Test suite:
        * linkage in a not (":" or "*")-ending LIST_ITEM
        * linkage in a list with a single ":"
        * linkage together with another template
        * linkage inside synonym
        * linkage without gloss
        * linkage without gloss, but one quote
        * linkage without gloss, with βλ-prefixed linkage
        * linkage basic
        * linkage multiple
        * linkage useless (delete)

        Notes:
        * Is this another template or equivalent?
        https://el.wiktionary.org/wiki/Πρότυπο:ΒΠ
        * Same for βλέπε, δείτε etc.
        """
        self.wxr.wtp.start_page("start_filler")
        data = WordEntry(lang="Greek", lang_code="el", word="word_filler")
        # * Prefixing the header allows us to not have it everywhere in the tests.
        # * Adding the head just silences a warning.
        raw = "==={{ουσιαστικό|el}}===\n'''head'''\n" + raw_trim(raw)
        root = self.wxr.wtp.parse(raw)
        pos_node = root.children[0]
        process_pos(self.wxr, pos_node, data, None, "", "", pos_tags=[])  # type: ignore
        # from wiktextract.extractor.el.logger import dbg
        # dbg(data)
        dumped = data.model_dump(exclude_defaults=True)
        # print(f"{dumped=}")
        senses = dumped["senses"]
        # print("-----------------------------------")
        # print(f"{senses=}")
        self.assertEqual(senses, expected)

    def test_bl_linkage_irregular_list_item(self) -> None:
        # https://el.wiktionary.org/wiki/Καραγκιόζης
        # * The βλ template appears in an not (":" or "*")-ending ITEM
        raw = """
            # [[ήρωας]] του [[θέατρο σκιών|θεάτρου σκιών]]
            # (μεταφορικά) {{βλ|καραγκιόζης}}
        """
        expected = [
            {"glosses": ["ήρωας του θεάτρου σκιών"]},
            {
                "related": [{"word": "καραγκιόζης"}],
                "raw_tags": ["μεταφορικά"],
                "tags": ["no-gloss", "figuratively"],
            },
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_list_with_single_colon_item(self) -> None:
        # https://el.wiktionary.org/wiki/αναμαλλιασμένος
        raw = """: {{βλ|αναμαλλιάζω}}"""
        expected = [
            {"related": [{"word": "αναμαλλιάζω"}], "tags": ["no-gloss"]}
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_with_another_template(self) -> None:
        # https://el.wiktionary.org/wiki/επωτίδες
        raw = """* {{πτώσειςΟΑΚπλ|επωτίδα}} {{βλ|όρος=το αρχαίο|ἐπωτίδες}}"""
        expected = [
            {
                "glosses": [":Πρότυπο:πτώσειςΟΑΚπλ"],
                "tags": ["accusative", "nominative", "plural", "vocative"],
                "form_of": [{"word": "επωτίδα"}],
                "related": [{"word": "ἐπωτίδες"}],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_inside_synonym(self) -> None:
        # https://el.wiktionary.org/wiki/αφόδευμα
        raw = """
            * [[ό,τι]] [[αφοδεύω|αφοδεύει]] κάποιος
            *: {{συνων}} {{βλ|περίττωμα}}
        """
        expected = [
            {
                "glosses": ["ό,τι αφοδεύει κάποιος"],
                "synonyms": [{"word": "περίττωμα"}],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_no_gloss(self) -> None:
        # https://el.wiktionary.org/wiki/αγριόσκυλος
        raw = """* {{βλ|αγριόσκυλο}}"""
        expected = [{"tags": ["no-gloss"], "related": [{"word": "αγριόσκυλο"}]}]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_no_gloss_with_bl_starting_linkage(self) -> None:
        # Handmade: to test prefix selection.
        raw = """* {{βλ|βλέπε}}"""
        expected = [
            {
                "related": [{"word": "βλέπε"}],
                "tags": ["no-gloss"],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_no_gloss_one_quote(self) -> None:
        # https://el.wiktionary.org/wiki/αιματόχροος
        raw = """
            * {{βλ|αιματόχρους}}
            *: {{παράθεμα}} ''Στα πρώτα...''
        """
        expected = [
            {
                "examples": [{"text": ":Πρότυπο:παράθεμα Στα πρώτα..."}],
                "related": [{"word": "αιματόχρους"}],
                "tags": ["no-gloss"],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage(self) -> None:
        # https://el.wiktionary.org/wiki/μετροταινία
        raw = """
            * οποιοδήποτε είδος ταινίας...
            *: {{βλ|και=2|μεζούρα}}
        """
        expected = [
            {
                "glosses": ["οποιοδήποτε είδος ταινίας..."],
                "related": [{"word": "μεζούρα"}],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_multiple(self) -> None:
        # https://el.wiktionary.org/wiki/ισοβαρής
        raw = """
            # που ενώνει σημεία με ίδια [[βαρομετρικός|βαρομετρική]] [[πίεση]]
            #: {{βλ|όρος=1|ισοβαρής γραμμή|ισοβαρής καμπύλη}}
            #: {{βλ|και=2|ισαλλοβαρής}}
        """
        expected = [
            {
                "glosses": ["που ενώνει σημεία με ίδια βαρομετρική πίεση"],
                "related": [
                    {"word": "ισοβαρής γραμμή"},
                    {"word": "ισοβαρής καμπύλη"},
                    {"word": "ισαλλοβαρής"},
                ],
            },
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_bl_linkage_inline_useless(self) -> None:
        # https://el.wiktionary.org/wiki/επί
        # Should delete the βλ template
        raw = """# δηλώνει [[αιτία]] {{βλ|όρος=τις εκφράσεις}}"""
        expected = [{"glosses": ["δηλώνει αιτία"]}]
        self.mktest_bl_linkage(raw, expected)

    def test_el_glosses1(self) -> None:
        self.wxr.wtp.start_page("brain")
        data = WordEntry(lang="English", lang_code="en", word="brain")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|en}}===
'''φώσφορος'''
# foo
#: ''An operation was done to remove a tumor from the patient’s '''brain'''.''
#:: Έγινε επέμβαση για αφαίρεση όγκου από τον '''εγκέφαλο''' του ασθενή.
# (''πληθυντικός'') τα [[μυαλό|μυαλά]], το μυαλό ζώων που χρησιμοποιείται από τους ανθρώπους ως τροφή
#: ''lamb '''brains''''' - αρνίσια '''μυαλά'''
# το [[μυαλό]], η ικανότητα να μαθαίνω γρήγορα και να σκέφτομαι τα πράγματα με λογικό και έξυπνο τρόπο
#: ''Use your '''brain'''!''
#:: Βάλε το '''μυαλό''' σου να δουλέψει!
#: ''If you had any '''brains''', you wouldn’t be in this mess.''
#:: Αν είχες '''μυαλά''' δε θα βρισκόσουν σ΄ αυτά τα χάλια.
# ανεπίσημο το [[μυαλό]], έξυπνος άνθρωπος
#: ''He’s a big '''brain'''.''
#:: Είναι κάποιος μεγάλο '''μυαλό'''.
# ('''''the brains''', ενικός'') ο [[εγκέφαλος]], το [[μυαλό]], το πιο έξυπνο άτομο σε μια συγκεκριμένη ομάδα· το άτομο που είναι υπεύθυνο να σκεφτεί και να οργανώσει κάτι
#: ''He is '''the brains''' of the company.''
#:: Είναι '''ο εγκέφαλος''' της εταιρείας.
#: ''He was '''the brains''' behind the plot.''
#:: Ήταν '''το μυαλό''' της συνωμοσίας.
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr,
            pos_node,  # type: ignore[arg-type]
            data,
            None,
            "noun",
            "ουσιαστικό",
            pos_tags=[],
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")
        test = {
            "word": "brain",
            "forms": [{"form": "φώσφορος", "source": "header"}],
            "lang_code": "en",
            "lang": "English",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["foo"],
                    "examples": [
                        {
                            "text": "An operation was done to remove a tumor from the patient’s brain.",
                            "translation": "Έγινε επέμβαση για αφαίρεση όγκου από τον εγκέφαλο του ασθενή.",
                        }
                    ],
                },
                {
                    "glosses": [
                        "τα μυαλά, το μυαλό ζώων που χρησιμοποιείται από τους ανθρώπους ως τροφή"
                    ],
                    "raw_tags": ["πληθυντικός"],
                    "tags": ["plural"],
                    "examples": [{"text": "lamb brains - αρνίσια μυαλά"}],
                },
                {
                    "glosses": [
                        "το μυαλό, η ικανότητα να μαθαίνω γρήγορα και να σκέφτομαι τα πράγματα με λογικό και έξυπνο τρόπο"
                    ],
                    "examples": [
                        {
                            "text": "Use your brain!",
                            "translation": "Βάλε το μυαλό σου να δουλέψει!",
                        },
                        {
                            "text": "If you had any brains, you wouldn’t be in this mess.",
                            "translation": "Αν είχες μυαλά δε θα βρισκόσουν σ΄ αυτά τα χάλια.",
                        },
                    ],
                },
                {
                    "glosses": ["ανεπίσημο το μυαλό, έξυπνος άνθρωπος"],
                    "examples": [
                        {
                            "text": "He’s a big brain.",
                            "translation": "Είναι κάποιος μεγάλο μυαλό.",
                        }
                    ],
                },
                {
                    "glosses": [
                        "(the brains, ενικός) ο εγκέφαλος, το μυαλό, το πιο έξυπνο άτομο σε μια συγκεκριμένη ομάδα· το άτομο που είναι υπεύθυνο να σκεφτεί και να οργανώσει κάτι"
                    ],
                    "examples": [
                        {
                            "text": "He is the brains of the company.",
                            "translation": "Είναι ο εγκέφαλος της εταιρείας.",
                        },
                        {
                            "text": "He was the brains behind the plot.",
                            "translation": "Ήταν το μυαλό της συνωμοσίας.",
                        },
                    ],
                },
            ],
        }
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped, test)

    def test_synonyms_antonyms(self) -> None:
        # https://el.wiktionary.org/wiki/ευχαριστώ
        raw = """
            # [[δείχνω]] σε κάποιον ότι τον [[ευγνωμονώ]] για κάτι που μου έκανε ή που μου έδωσε
            #: {{πχ}}  ''Μπορείς να τον '''ευχαριστήσεις''' για όλο τον κόπο που έκανε!''
            #: {{αντων}} [[δυσαρεστώ]], [[πικραίνω]], [[στενοχωρώ]]
            # κάνω κάποιον να νιώσει όμορφα, [[ικανοποιώ]] κάποιον
            #: {{συνων}} [[ικανοποιώ]], [[χαροποιώ]]
            #: {{αντων}} [[δυσαρεστώ]], [[στενοχωρώ]]
        """
        expected = [
            {
                "glosses": [
                    "δείχνω σε κάποιον ότι τον ευγνωμονώ για κάτι που μου έκανε ή που μου έδωσε"
                ],
                "examples": [
                    {
                        "text": ":Πρότυπο:πχ Μπορείς να τον ευχαριστήσεις για όλο τον κόπο που έκανε!"
                    }
                ],
                "antonyms": [
                    {"word": "δυσαρεστώ"},
                    {"word": "πικραίνω"},
                    {"word": "στενοχωρώ"},
                ],
            },
            {
                "glosses": ["κάνω κάποιον να νιώσει όμορφα, ικανοποιώ κάποιον"],
                "synonyms": [{"word": "ικανοποιώ"}, {"word": "χαροποιώ"}],
                "antonyms": [{"word": "δυσαρεστώ"}, {"word": "στενοχωρώ"}],
            },
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_synonyms_antonyms_alt_templates(self) -> None:
        # https://el.wiktionary.org/wiki/αναβιβασμός
        raw = """
            # [[ανέβασμα]]
            #: {{συνών}} [[αναβίβαση]], [[ανέβασμα]]
            #: {{αντών}} [[καταβιβασμός]], [[καταβίβαση]], [[κατέβασμα]]
        """
        expected = [
            {
                "glosses": ["ανέβασμα"],
                "synonyms": [{"word": "αναβίβαση"}, {"word": "ανέβασμα"}],
                "antonyms": [
                    {"word": "καταβιβασμός"},
                    {"word": "καταβίβαση"},
                    {"word": "κατέβασμα"},
                ],
            }
        ]
        self.mktest_bl_linkage(raw, expected)

    def test_el_subglosses1(self) -> None:
        self.wxr.wtp.start_page("brain")
        data = WordEntry(lang="English", lang_code="en", word="brain")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|en}}===
'''brain'''
# bar
## baz
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr,
            pos_node,  # type: ignore[arg-type]
            data,
            None,
            "noun",
            "ουσιαστικό",
            pos_tags=[],
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")
        test = {
            "word": "brain",
            "forms": [{"form": "brain", "source": "header"}],
            "lang_code": "en",
            "lang": "English",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["bar", "baz"],
                },
            ],
        }
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped, test)
