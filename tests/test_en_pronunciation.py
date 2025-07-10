from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.pronunciation import parse_pronunciation
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"), WiktionaryConfig(dump_file_lang_code="en")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test1(self):
        self.wxr.wtp.start_page("foo")
        self.wxr.wtp.add_page(
            "Template:enPR",
            10,
            """{{#switch:{{{1}}}
| föö = (Received Pronunciation) enPR: föö
| bär = enPR: bär
| vöö = (US) enPR: vöö
}}""",
        )
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            """{{#switch:{{{2}}}
| /foo/ = IPA⁽ᵏᵉʸ⁾: /foo/
| /bar/ = (Received Pronunciation) IPA⁽ᵏᵉʸ⁾: /bar/
| /baz/ = (Northern England, Scotland) IPA⁽ᵏᵉʸ⁾: /baz/
| /voo/ = IPA⁽ᵏᵉʸ⁾: /voo/
| foobar = (Received Pronunciation, ergative) IPA⁽ᵏᵉʸ⁾: (Caribbean, note-fodder causes everything to be a note) /foobar/ (singular), (note-text) foobaz (ipa accepts parens) (Cajun, dual), barbar, barbaz; baz, bazfoo (singular) (US, paucal)
}}""",
        )
        self.wxr.wtp.add_page("Template:homophones", 10, "Homophone: feu")
        self.wxr.wtp.add_page("Template:rhymes", 10, "Rhymes: -oo, -öö")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{enPR|föö|a=RP}}, {{IPA|en|/foo/}}
* {{IPA|en|/bar/|a=RP}}, {{enPR|bär}},
* {{IPA|en|/baz/|a=Northern England,Scotland}}
* {{audio|en|LL-Q1860 (eng)-Back ache-past.wav|a=UK}}
* Verb:
* {{enPR|vöö|a=US}}, {{IPA|en|/voo/}}
* {{audio|en|en-us-past.ogg|a=US}}
* {{homophones|en|feu}}
* {{rhymes|en|oo|öö|s=1}}
* {{IPA|en|foobar|foobaz (ipa accepts parens)|barbar|barbaz|;|baz|bazfoo|a=RP|aa=US|q=ergative|qq=paucal|q1=note-fodder causes everything to be a note|qq1=singular|a1=Caribbean|aa2=Cajun|q2=note-text|qq2=dual|qq6=singular}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "tags": ["Received-Pronunciation"],
                        "enpr": "föö",
                        "pos": "noun",
                    },
                    {
                        "ipa": "/foo/",
                        "tags": ["Received-Pronunciation"],
                        "pos": "noun",
                    },
                    {
                        "tags": ["Received-Pronunciation"],
                        "ipa": "/bar/",
                        "pos": "noun",
                    },
                    {
                        "enpr": "bär",
                        "tags": ["Received-Pronunciation"],
                        "pos": "noun",
                    },
                    {
                        "tags": ["Northern-England", "Scotland"],
                        "ipa": "/baz/",
                        "pos": "noun",
                    },
                    {
                        "audio": "LL-Q1860 (eng)-Back ache-past.wav",
                        "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/7/7a/LL-Q1860_%28eng%29-Back_ache-past.wav/LL-Q1860_%28eng%29-Back_ache-past.wav.ogg",
                        "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/7/7a/LL-Q1860_%28eng%29-Back_ache-past.wav/LL-Q1860_%28eng%29-Back_ache-past.wav.mp3",
                        "pos": "noun",
                    },
                    {"tags": ["US"], "enpr": "vöö", "pos": "verb"},
                    {"ipa": "/voo/", "tags": ["US"], "pos": "verb"},
                    {
                        "audio": "en-us-past.ogg",
                        "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/En-us-past.ogg",
                        "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/b0/En-us-past.ogg/En-us-past.ogg.mp3",
                        "pos": "verb",
                    },
                    {"homophone": "feu", "pos": "verb"},
                    {"rhymes": "-oo", "pos": "verb"},
                    {"rhymes": "-öö", "pos": "verb"},
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                            "singular",
                        ],
                        "note": "Caribbean, note-fodder causes everything to be a note",
                        "ipa": "/foobar/",
                        "pos": "verb",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "note": "Cajun, dual",
                        "ipa": "foobaz(ipa accepts parens)",
                        "pos": "verb",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbar",
                        "pos": "verb",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbaz",
                        "pos": "verb",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "baz",
                        "pos": "verb",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                            "singular",
                        ],
                        "ipa": "bazfoo",
                        "pos": "verb",
                    },
                ]
            },
        )

    def test2(self):
        self.wxr.wtp.start_page("baz")
        self.wxr.wtp.add_page(
            "Template:enPR", 10, "(Received Pronunciation) enPR: föö"
        )
        self.wxr.wtp.add_page("Template:IPA", 10, "IPA⁽ᵏᵉʸ⁾: /foo/")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{enPR|föö|a=RP}}, {{IPA|en|/foo/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "tags": ["Received-Pronunciation"],
                        "enpr": "föö",
                        "pos": "noun",
                    },
                    {
                        "tags": ["Received-Pronunciation"],
                        "ipa": "/foo/",
                        "pos": "noun",
                    },
                ]
            },
        )

    def test_no_templates1(self):
        self.wxr.wtp.start_page("baz")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* (Received-Pronunciation) IPA: /foo/
* Homophone: feu
* Rhymes: -oo
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "tags": ["Received-Pronunciation"],
                        "ipa": "/foo/",
                        "pos": "noun",
                    },
                    {"homophone": "feu", "pos": "noun"},
                    {"rhymes": "-oo", "pos": "noun"},
                ]
            },
        )

    def test_split_args(self):
        self.wxr.wtp.start_page("foo")
        self.wxr.wtp.add_page(
            "IPA",
            10,
            "(Received Pronunciation, ergative) IPA⁽ᵏᵉʸ⁾: (Caribbean, note-fodder causes everything to be a note) /foobar/ (singular), (note-text) foobaz (ipa accepts parens) (Cajun, dual), barbar, barbaz; baz, bazfoo (singular) (US, paucal)",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|foobar|foobaz (ipa accepts parens)|barbar|barbaz|;|baz|bazfoo|a=RP|aa=US|q=ergative|qq=paucal|q1=note-fodder causes everything to be a note|qq1=singular|a1=Caribbean|aa2=Cajun|q2=note-text|qq2=dual|qq6=singular}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                            "singular",
                        ],
                        "note": "Caribbean, note-fodder causes everything to be a note",
                        "ipa": "/foobar/",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "note": "Cajun, dual",
                        "ipa": "foobaz(ipa accepts parens)",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbar",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbaz",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "baz",
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                            "singular",
                        ],
                        "ipa": "bazfoo",
                    },
                ]
            },
        )

    def test_hyphenation_1(self):
        self.wxr.wtp.start_page("baz")
        self.wxr.wtp.add_page(
            "Template:enPR", 10, "(Received Pronunciation) enPR: föö"
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{hyphenation|en|foo|bar}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "hyphenations": [
                    {
                        "parts": ["foo", "bar"],
                        "tags": [],
                    },
                ]
            },
        )

    def test_hyphenation_2(self):
        self.wxr.wtp.start_page("baz")
        self.wxr.wtp.add_page(
            "Template:enPR", 10, "(Received Pronunciation) enPR: föö"
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{hyphenation|en|foo|bar||fo|obar}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "hyphenations": [
                    {
                        "parts": ["foo", "bar"],
                        "tags": [],
                    },
                    {
                        "parts": ["fo", "obar"],
                        "tags": [],
                    },
                ]
            },
        )

    def test_hyphenation_3(self):
        self.wxr.wtp.start_page("baz")
        self.wxr.wtp.add_page(
            "Template:enPR", 10, "(Received Pronunciation) enPR: föö"
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{hyphenation|en|foo|bar|caption=US}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "hyphenations": [
                    {
                        "parts": ["foo", "bar"],
                        "tags": ["US"],
                    },
                ]
            },
        )

    def test_hyphenation_4(self):
        self.wxr.wtp.start_page("baz")
        self.wxr.wtp.add_page(
            "Template:enPR", 10, "(Received Pronunciation) enPR: föö"
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun:
* {{hyphenation|en|foo|bar||fo|obar||f|oobar|caption=US}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                "hyphenations": [
                    {
                        "parts": ["foo", "bar"],
                        "tags": ["US"],
                    },
                    {
                        "parts": ["fo", "obar"],
                        "tags": ["US"],
                    },
                    {
                        "parts": ["f", "oobar"],
                        "tags": ["US"],
                    },
                ]
            },
        )

    def test_hyphenation_regex(self):
        self.wxr.wtp.start_page("quieto")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Hyphenation: quiè‧to, qui‧è‧to, quié‧to, qui‧é‧to
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        # import pprint
        # pprint.pp(out)

        self.assertEqual(
            out,
            {
                # Remove `hyphenation` field if deprecated succesfully
                  "hyphenation": [
                    "quiè‧to, qui‧è‧to, quié‧to, qui‧é‧to"
                  ],
                "hyphenations": [
                    {"parts": ["quiè", "to"]},
                    {"parts": ["qui", "è", "to"]},
                    {"parts": ["quié", "to"]},
                    {"parts": ["qui", "é", "to"]},
                ],
            },
        )
