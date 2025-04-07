from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

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

    test1_templates = [
        ("enPR", "(Received Pronunciation) enPR: föö"),
        ("IPA", "IPA⁽ᵏᵉʸ⁾: /foo/"),
        ("IPA", "(Received Pronunciation) IPA⁽ᵏᵉʸ⁾: /bar/"),
        ("enPR", "enPR: bär"),
        ("IPA", "(Northern England, Scotland) IPA⁽ᵏᵉʸ⁾: /baz/"),
        # The Template:audio calls have no calls to get_page() because
        # parse_pronunciation_template_fn skips them; clean_value()
        # is called on argument 3, but that doesn't contain templates here
        # ("audio", "Audio (UK):	"),
        ("enPR", "(US) enPR: vöö"),
        ("IPA", "IPA⁽ᵏᵉʸ⁾: /voo/"),
        # ("audio", "Audio (US):	"),
        ("homophones", "Homophone: feu"),
        ("rhymes", "Rhymes: -oo, -öö"),
        (
            "IPA",
            "(Received Pronunciation, ergative) IPA⁽ᵏᵉʸ⁾: (Caribbean, note-fodder causes everything to be a note) /foobar/ (singular), (note-text) foobaz (ipa accepts parens) (Cajun, dual), barbar, barbaz; baz, bazfoo (singular) (US, paucal)",
        ),
    ]
    test1_pages = [
        Page(title=title, namespace_id=10, body=body)
        for (title, body) in test1_templates
    ]

    # for page in test1_pages:
    #     print(f"== {page}")

    @patch(
        "wikitextprocessor.Wtp.get_page",
        side_effect=test1_pages,
    )
    def test1(self, mock_get_page):
        self.wxr.wtp.start_page("foo")
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

    test2_templates = [
        ("enPR", "(Received Pronunciation) enPR: föö"),
    ]
    test1_pages = [
        Page(title=title, namespace_id=10, body=body)
        for (title, body) in test1_templates
    ]

    @patch(
        "wikitextprocessor.Wtp.get_page",
        side_effect=test1_pages,
    )
    def test2(self, mock_get_page):
        self.wxr.wtp.start_page("baz")
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

    test1_templates = [
        (
            "IPA",
            "(Received Pronunciation, ergative) IPA⁽ᵏᵉʸ⁾: (Caribbean, note-fodder causes everything to be a note) /foobar/ (singular), (note-text) foobaz (ipa accepts parens) (Cajun, dual), barbar, barbaz; baz, bazfoo (singular) (US, paucal)",
        ),
    ]
    test1_pages = [
        Page(title=title, namespace_id=10, body=body)
        for (title, body) in test1_templates
    ]

    # for page in test1_pages:
    #     print(f"== {page}")

    @patch(
        "wikitextprocessor.Wtp.get_page",
        side_effect=test1_pages,
    )
    def test_split_args(self, mock_get_page):
        self.wxr.wtp.start_page("foo")
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
