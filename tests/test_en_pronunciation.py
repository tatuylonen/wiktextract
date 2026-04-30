from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.extractor.en.pronunciation import (
    parse_pronunciation,
    pronunciation_pos_from_part,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def add_pos_pronunciation_templates(self) -> None:
        self.wxr.wtp.add_page(
            "Template:IPA", 10, "IPA⁽ᵏᵉʸ⁾: {{{2}}}"
        )
        self.wxr.wtp.add_page(
            "Template:q",
            10,
            "({{{1}}}{{#if:{{{2|}}}|, {{{2}}}}}{{#if:{{{3|}}}|, {{{3}}}}})",
        )
        self.wxr.wtp.add_page(
            "Template:sense",
            10,
            "({{{1}}}{{#if:{{{2|}}}|, {{{2}}}}}):",
        )
        self.wxr.wtp.add_page("Template:i", 10, "({{{1}}})")
        self.wxr.wtp.add_page(
            "Template:a",
            10,
            "({{{2}}}{{#if:{{{3|}}}|, {{{3}}}}})",
        )

    def test_pronunciation_pos_from_part(self):
        self.assertEqual(
            pronunciation_pos_from_part("attributive adjective"),
            ("adj", "attributive"),
        )
        self.assertEqual(
            pronunciation_pos_from_part("attributive proper noun"),
            ("name", "attributive"),
        )
        self.assertEqual(
            pronunciation_pos_from_part("proper noun"),
            ("name", ""),
        )
        self.assertEqual(
            pronunciation_pos_from_part(
                "rare, with or without the horse-hoarse merger"
            ),
            (None, "rare, with or without the horse-hoarse merger"),
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
                        "pos": ("noun",),
                    },
                    {
                        "ipa": "/foo/",
                        "tags": ["Received-Pronunciation"],
                        "pos": ("noun",),
                    },
                    {
                        "tags": ["Received-Pronunciation"],
                        "ipa": "/bar/",
                        "pos": ("noun",),
                    },
                    {
                        "enpr": "bär",
                        "tags": ["Received-Pronunciation"],
                        "pos": ("noun",),
                    },
                    {
                        "tags": ["Northern-England", "Scotland"],
                        "ipa": "/baz/",
                        "pos": ("noun",),
                    },
                    {
                        "audio": "LL-Q1860 (eng)-Back ache-past.wav",
                        "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/7/7a/LL-Q1860_%28eng%29-Back_ache-past.wav/LL-Q1860_%28eng%29-Back_ache-past.wav.ogg",
                        "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/7/7a/LL-Q1860_%28eng%29-Back_ache-past.wav/LL-Q1860_%28eng%29-Back_ache-past.wav.mp3",
                        "pos": ("noun",),
                        "tags": ["UK"],
                    },
                    {"tags": ["US"], "enpr": "vöö", "pos": ("verb",)},
                    {"ipa": "/voo/", "tags": ["US"], "pos": ("verb",)},
                    {
                        "audio": "en-us-past.ogg",
                        "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/En-us-past.ogg",
                        "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/b0/En-us-past.ogg/En-us-past.ogg.mp3",
                        "pos": ("verb",),
                        "tags": ["US"],
                    },
                    {"homophone": "feu", "pos": ("verb",)},
                    {"rhymes": "-oo", "pos": ("verb",)},
                    {"rhymes": "-öö", "pos": ("verb",)},
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
                        "pos": ("verb",),
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "note": "note-text; Cajun, dual",
                        "ipa": "foobaz(ipa accepts parens)",
                        "pos": ("verb",),
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbar",
                        "pos": ("verb",),
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "barbaz",
                        "pos": ("verb",),
                    },
                    {
                        "tags": [
                            "Received-Pronunciation",
                            "ergative",
                            "US",
                            "paucal",
                        ],
                        "ipa": "baz",
                        "pos": ("verb",),
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
                        "pos": ("verb",),
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
                        "pos": ("noun",),
                    },
                    {
                        "tags": ["Received-Pronunciation"],
                        "ipa": "/foo/",
                        "pos": ("noun",),
                    },
                ]
            },
        )

    def test_multi_pos_plain_text_label(self):
        self.wxr.wtp.start_page("offset")
        self.wxr.wtp.add_page("Template:IPA", 10, "IPA⁽ᵏᵉʸ⁾: /ˈɔfsɛt/")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* Noun and verb:
* {{IPA|en|/ˈɔfsɛt/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {"sounds": [{"ipa": "/ˈɔfsɛt/", "pos": ("noun", "verb")}]},
        )

    def test_bold_pos_plain_text_label(self):
        self.wxr.wtp.start_page("use")
        self.wxr.wtp.add_page("Template:IPA", 10, "IPA⁽ᵏᵉʸ⁾: /juːs/")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
'''Noun'''
* {{IPA|en|/juːs/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(out, {"sounds": [{"ipa": "/juːs/", "pos": ("noun",)}]})

    def test_non_pos_qualifier_not_converted_to_pos(self):
        self.wxr.wtp.start_page("foo")
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* (US) IPA⁽ᵏᵉʸ⁾: /fu/
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(out, {"sounds": [{"tags": ["US"], "ipa": "/fu/"}]})

    def test_determinate_parenthesized_pos_prefixes(self):
        self.wxr.wtp.start_page("determinate")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "({{{a}}}) IPA⁽ᵏᵉʸ⁾: {{{2}}}",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* (adjective, noun) {{IPA|en|/dɪˈtɜːmɪnət/|a=UK}}
* (verb) {{IPA|en|/dɪˈtɜːmɪneɪt/|a=UK}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "ipa": "/dɪˈtɜːmɪnət/",
                        "tags": ["UK"],
                        "pos": ("adj", "noun"),
                    },
                    {
                        "ipa": "/dɪˈtɜːmɪneɪt/",
                        "tags": ["UK"],
                        "pos": ("verb",),
                    },
                ]
            },
        )

    def test_pos_template_line_labels_following_sublist(self):
        self.wxr.wtp.start_page("increase")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{q|verb}}
** {{IPA|en|/ɪnˈkɹiːs/}}
* {{q|noun}}
** {{IPA|en|/ˈɪnkɹiːs/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {"ipa": "/ɪnˈkɹiːs/", "pos": ("verb",)},
                    {"ipa": "/ˈɪnkɹiːs/", "pos": ("noun",)},
                ]
            },
        )

    def test_pos_template_root_level_label(self):
        self.wxr.wtp.start_page("dotcom")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
{{i|noun}}
* {{IPA|en|/dɒtˈkɒm/}}
{{i|verb}}
* {{IPA|en|/ˈdɒtkɒm/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {"ipa": "/dɒtˈkɒm/", "pos": ("noun",)},
                    {"ipa": "/ˈdɒtkɒm/", "pos": ("verb",)},
                ]
            },
        )

    def test_pos_template_prefix_and_postfix_labels(self):
        self.wxr.wtp.start_page("reboot")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{q|verb}} {{IPA|en|/ɹiːˈbuːt/}}
* {{IPA|en|/ˈɹiːbuːt/}} {{q|noun|verb}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {"ipa": "/ɹiːˈbuːt/", "pos": ("verb",)},
                    {"ipa": "/ˈɹiːbuːt/", "pos": ("noun", "verb")},
                ]
            },
        )

    def test_pos_template_multi_pos_and_parenthetical_label(self):
        self.wxr.wtp.start_page("deserts")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{a|en|noun (barren areas)|verb}} {{IPA|en|/ˈdɛzɚts/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {"sounds": [{"ipa": "/ˈdɛzɚts/", "pos": ("noun", "verb")}]},
        )

    def test_pos_template_multiple_groups_on_one_line(self):
        # Norwegian Bokmål section
        self.wxr.wtp.start_page("abandoner")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{sense|noun}} {{IPA|nb|/abaŋˈdɔŋər/}}, {{sense|verb}} {{IPA|nb|/abandɔˈneːr/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "nb")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {"ipa": "/abaŋˈdɔŋər/", "pos": ("noun",)},
                    {"ipa": "/abandɔˈneːr/", "pos": ("verb",)},
                ]
            },
        )

    def test_accent_template_non_pos_label_remains_tag(self):
        self.wxr.wtp.start_page("conduct")
        self.add_pos_pronunciation_templates()
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{a|en|RP}} {{IPA|en|/ˈkɒndʌkt/}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {"sounds": [{"ipa": "/ˈkɒndʌkt/", "tags": ["Received-Pronunciation"]}]},
        )

    def test_ipa_qq_note_with_link_template(self):
        self.wxr.wtp.start_page("jewellery")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "({{{a}}}) IPA⁽ᵏᵉʸ⁾: {{{2}}} ({{{qq}}})",
        )
        self.wxr.wtp.add_page(
            "Template:l",
            10,
            "[[:{{{2}}}#English|{{{2}}}]]",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/ˈd͡ʒuː(ə)ləɹi/|a=nonstandard|qq=this pronunciation gives rise to the Cockney rhyming slang ''{{l|en|tomfoolery}}''}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out["sounds"][0]["note"],
            "this pronunciation gives rise to the Cockney rhyming slang tomfoolery",
        )

    def test_ipa_text_in_qualifier_template_not_extracted(self):
        self.wxr.wtp.start_page("Kokos")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "IPA⁽ᵏᵉʸ⁾: {{{2}}}",
        )
        self.wxr.wtp.add_page(
            "Template:q",
            10,
            "({{{1}}})",
        )
        self.wxr.wtp.add_page(
            "Template:IPAchar",
            10,
            '<span class="IPA nowrap">{{{1}}}</span>',
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|de|/ˈkoːkɔs/}} {{q|entirely uncommon in northern and central Germany, perhaps used by southern speakers whose {{IPAchar|/ɔ/}} is {{IPAchar|[o]}}}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "de")
        self.assertEqual(out, {"sounds": [{"ipa": "/ˈkoːkɔs/"}]})

    def test_inline_ipa_q_pos_qualifier(self):
        self.wxr.wtp.start_page("disuse")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "IPA⁽ᵏᵉʸ⁾: (noun) /dɪsˈjuːs/, (verb) /dɪsˈjuːz/",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/dɪsˈjuːs/<q:noun>|/dɪsˈjuːz/<q:verb>}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {"ipa": "/dɪsˈjuːs/", "pos": ("noun",)},
                    {"ipa": "/dɪsˈjuːz/", "pos": ("verb",)},
                ]
            },
        )

    def test_ipa_nonindexed_named_param_pos(self):
        self.wxr.wtp.start_page("advocate")
        self.wxr.wtp.add_page(
            "Template:IPA", 10, "({{{q}}}) IPA⁽ᵏᵉʸ⁾: {{{2}}}"
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/ˈæd.və.kət/|q=noun}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {"sounds": [{"ipa": "/ˈæd.və.kət/", "pos": ("noun",)}]},
        )

    def test_ipa_indexed_param_pos(self):
        self.wxr.wtp.start_page("rebound")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "({{{a}}}) IPA⁽ᵏᵉʸ⁾: ({{{q1}}}) {{{2}}}, ({{{q2}}}) {{{3}}}",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/ˈɹi.baʊnd/|q1=noun|/ɹiˈbaʊnd/|q2=verb|a=GA}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "ipa": "/ˈɹi.baʊnd/",
                        "pos": ("noun",),
                        "tags": ["General-American"],
                    },
                    {
                        "ipa": "/ɹiˈbaʊnd/",
                        "pos": ("verb",),
                        "tags": ["General-American"],
                    },
                ]
            },
        )

    def test_ipa_note_keeps_prose_conjunctions(self):
        self.wxr.wtp.start_page("mourn")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "IPA⁽ᵏᵉʸ⁾: {{{2}}} (rare, rhotic, with or without the horse-hoarse merger)",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/mɔːn/|a=rare,rhotic,with or without the horse-hoarse merger}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "ipa": "/mɔːn/",
                        "note": "rare, rhotic, with or without the horse-hoarse merger",
                    }
                ]
            },
        )

    def test_compound_pos_qualifier_keeps_modifier_as_tag(self):
        self.wxr.wtp.start_page("inbred")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            "({{{a}}}) IPA⁽ᵏᵉʸ⁾: {{{2}}}{{#if:{{{3|}}}|, {{{3}}}}}",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{IPA|en|/ˈɪnˌbɹɛd/|a=[[attributive]] adjective,noun}}
* {{IPA|en|/ˈɪnˌbɹɛd/|/ˌɪnˈbɹɛd/|a=[[predicative]] adjective,verb}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        self.assertEqual(
            out,
            {
                "sounds": [
                    {
                        "ipa": "/ˈɪnˌbɹɛd/",
                        "pos": ("adj", "noun"),
                        "tags": ["attributive"],
                    },
                    {
                        "ipa": "/ˈɪnˌbɹɛd/",
                        "pos": ("adj", "verb"),
                        "tags": ["predicative"],
                    },
                    {
                        "ipa": "/ˌɪnˈbɹɛd/",
                        "pos": ("adj", "verb"),
                        "tags": ["predicative"],
                    },
                ]
            },
        )

    def test_pos_filtered_pronunciation_audio_stays_with_matching_pos(self):
        self.wxr.wtp.start_page("discharge")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            """{{#ifeq:{{{2}}}|/dɪsˈtʃɑːdʒ/<q:verb>|IPA⁽ᵏᵉʸ⁾: (verb) /dɪsˈtʃɑːdʒ/|{{#ifeq:{{{2}}}|/ˈdɪstʃɑːdʒ/<q:noun>|IPA⁽ᵏᵉʸ⁾: (noun) /ˈdɪstʃɑːdʒ/|IPA⁽ᵏᵉʸ⁾: {{{2}}}}}}}""",
        )
        self.wxr.wtp.add_page("Template:a", 10, "({{{2}}})")
        self.wxr.wtp.add_page("Template:qualifier", 10, "({{{1}}})")
        self.wxr.wtp.add_page("Template:enPR", 10, "enPR: {{{1}}}")
        tree = self.wxr.wtp.parse("""===Pronunciation===
* {{a|en|RP}}
** {{IPA|en|/dɪsˈtʃɑːdʒ/<q:verb>}}
*** {{audio|en|LL-Q1860 (eng)-Vealhurl-discharge (verb).wav|a=Southern England}}
** {{IPA|en|/ˈdɪstʃɑːdʒ/<q:noun>}}
*** {{audio|en|LL-Q1860 (eng)-Vealhurl-discharge (noun).wav|a=Southern England}}
* {{a|en|US}}
** {{qualifier|verb}} {{enPR|dĭschärj'}}, {{IPA|en|/dɪsˈtʃɑɹdʒ/}}
** {{qualifier|noun}} {{enPR|dĭs'chärj}}, {{IPA|en|/ˈdɪstʃɑɹdʒ/}}
*** {{audio|en|En-us-discharge.ogg|a=US}}
* {{rhymes|en|ɑː(ɹ)dʒ|ɪstʃɑː(ɹ)dʒ|s=2}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        sounds = out["sounds"]
        verb_sounds = [s for s in sounds if s.get("pos") == ("verb",)]
        noun_sounds = [s for s in sounds if s.get("pos") == ("noun",)]
        self.assertEqual(
            [s["ipa"] for s in verb_sounds if "ipa" in s],
            ["/dɪsˈtʃɑːdʒ/", "/dɪsˈtʃɑɹdʒ/"],
        )
        self.assertIn(
            "LL-Q1860 (eng)-Vealhurl-discharge (verb).wav",
            [s["audio"] for s in verb_sounds if "audio" in s],
        )
        self.assertNotIn(
            "LL-Q1860 (eng)-Vealhurl-discharge (noun).wav",
            [s["audio"] for s in verb_sounds if "audio" in s],
        )
        self.assertEqual(
            [s["ipa"] for s in noun_sounds if "ipa" in s],
            ["/ˈdɪstʃɑːdʒ/", "/ˈdɪstʃɑɹdʒ/"],
        )
        self.assertIn(
            "LL-Q1860 (eng)-Vealhurl-discharge (noun).wav",
            [s["audio"] for s in noun_sounds if "audio" in s],
        )
        self.assertNotIn(
            "LL-Q1860 (eng)-Vealhurl-discharge (verb).wav",
            [s["audio"] for s in noun_sounds if "audio" in s],
        )

    def test_audio_pos_inherits_only_from_parent_list_item(self):
        self.wxr.wtp.start_page("abstract")
        self.wxr.wtp.add_page("Template:a", 10, "({{{2}}})")
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            """{{#switch:{{{a}}}
| noun = (noun) IPA⁽ᵏᵉʸ⁾: {{{2}}}
| adjective = (adjective) IPA⁽ᵏᵉʸ⁾: {{{2}}}{{#if:{{{3|}}}|, {{{3}}}}}{{#if:{{{4|}}}|, {{{4}}}}}
| verb = (verb) IPA⁽ᵏᵉʸ⁾: {{{2}}}{{#if:{{{3|}}}|, {{{3}}}}}
}}""",
        )
        tree = self.wxr.wtp.parse("""=== Pronunciation ===
* {{a|en|RP}}
** {{IPA|en|/ˈæbˌstɹækt/|a=noun}}
** {{IPA|en|/ˈæbˌstɹækt/|a=adjective}}
** {{IPA|en|/ˌæbˈstɹækt/|/əbˈstɹækt/|a=verb}}
** {{audio|en|LL-Q1860 (eng)-Vealhurl-abstract (noun).wav|a=Southern England}}
** {{audio|en|LL-Q1860 (eng)-Vealhurl-abstract (noun).wav|a=Southern England}}
** {{audio|en|LL-Q1860 (eng)-Vealhurl-abstract (verb).wav|a=Southern England}}
* {{a|en|GA}}
** {{IPA|en|/ˈæbˌstɹækt/|a=noun}}
** {{IPA|en|/ˌæbˈstɹækt/|/əbˈstɹækt/|/ˈæbˌstɹækt/|a=adjective}}
** {{IPA|en|/ˌæbˈstɹækt/|/əbˈstɹækt/|a=verb}}
* {{rhymes|en|ækt|s=2}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        sounds = out["sounds"]
        self.assertIn(
            ("/ˈæbˌstɹækt/", ("noun",)),
            [(s.get("ipa"), s.get("pos")) for s in sounds],
        )
        self.assertIn(
            ("/ˈæbˌstɹækt/", ("adj",)),
            [(s.get("ipa"), s.get("pos")) for s in sounds],
        )
        self.assertIn(
            ("/ˌæbˈstɹækt/", ("verb",)),
            [(s.get("ipa"), s.get("pos")) for s in sounds],
        )
        audio_sounds = [s for s in sounds if "audio" in s]
        self.assertEqual(
            [s["audio"] for s in audio_sounds],
            [
                "LL-Q1860 (eng)-Vealhurl-abstract (noun).wav",
                "LL-Q1860 (eng)-Vealhurl-abstract (verb).wav",
            ],
        )
        self.assertTrue(all("pos" not in s for s in audio_sounds))

    def test_audio_pos_inherits_from_suffix_pos_marker(self):
        self.wxr.wtp.start_page("maculate")
        self.wxr.wtp.add_page("Template:IPA", 10, "IPA⁽ᵏᵉʸ⁾: {{{2}}}")
        self.wxr.wtp.add_page("Template:sense", 10, "({{{1}}}):")
        tree = self.wxr.wtp.parse("""===Pronunciation===
* {{IPA|en|/ˈmækjʊleɪt/}} {{sense|verb}}
** {{audio|en|LL-Q1860 (eng)-Vealhurl-maculate.wav|a=Southern England}}
* {{IPA|en|/ˈmækjʊlət/}} {{sense|adjective}}
""")
        out = {}
        parse_pronunciation(self.wxr, tree.children[0], out, {}, {}, {}, "en")
        sounds = out["sounds"]
        verb_audio = next(
            s
            for s in sounds
            if s.get("audio")
            == "LL-Q1860 (eng)-Vealhurl-maculate.wav"
        )
        self.assertEqual(
            [(s.get("ipa") or s.get("audio"), s.get("pos")) for s in sounds],
            [
                ("/ˈmækjʊleɪt/", ("verb",)),
                ("LL-Q1860 (eng)-Vealhurl-maculate.wav", ("verb",)),
                ("/ˈmækjʊlət/", ("adj",)),
            ],
        )
        self.assertEqual(verb_audio["tags"], ["Southern-England"])

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
                        "pos": ("noun",),
                    },
                    {"homophone": "feu", "pos": ("noun",)},
                    {"rhymes": "-oo", "pos": ("noun",)},
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
                        "note": "note-text; Cajun, dual",
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
                "hyphenation": ["quiè‧to, qui‧è‧to, quié‧to, qui‧é‧to"],
                "hyphenations": [
                    {"parts": ["quiè", "to"]},
                    {"parts": ["qui", "è", "to"]},
                    {"parts": ["quié", "to"]},
                    {"parts": ["qui", "é", "to"]},
                ],
            },
        )

    def test_th_pron(self):
        self.wxr.wtp.add_page(
            "Template:th-pron",
            10,
            """<table>
<tr><th>''[[w:Thai alphabet|Orthographic]]''</th><td colspan="2"><span lang="th" class="Thai th-reading">ฝรั่ง</span><br><small>f&thinsp;r&thinsp;ạ&thinsp;ˋ&thinsp;ŋ</small></td></tr>
<tr><th colspan="2">''[[w:Thai alphabet|Phonemic]]''</th><td><div class="th-reading"><span lang="th" class="Thai ">ฝะ-หฺรั่ง</span><br><small>f&thinsp;a&thinsp;&ndash;&thinsp;h&thinsp;̥&thinsp;r&thinsp;ạ&thinsp;ˋ&thinsp;ŋ</small></div></td><td><div class="th-reading"><span><small>[colloquial]</small></span><br><span lang="th" class="Thai ">ฟะ-หฺรั่ง</span><br><small>v&thinsp;a&thinsp;&ndash;&thinsp;h&thinsp;̥&thinsp;r&thinsp;ạ&thinsp;ˋ&thinsp;ŋ</small></div></td></tr>
<tr><th rowspan="2">''[[Wiktionary:Thai romanization|Romanization]]''</th><th colspan="1">''[[Wiktionary:Thai romanization|Paiboon]]''</th><td><span class="tr">fà-ràng</span></td><td style="border-right:0px"><span class="tr">fá-ràng</span></td></tr><tr><th colspan="1">''[[Wiktionary:Thai romanization|Royal Institute]]''</th><td><span class="tr">fa-rang</span></td><td style="border-right:0px"><span class="tr">fa-rang</span></td></tr>
<tr><th colspan="2">(''[[w:Standard Thai|standard]]'') [[Wiktionary:International Phonetic Alphabet|IPA]]<sup>([[Appendix:Thai pronunciation|key]])</sup></th><td><span class="IPA">/fa˨˩.raŋ˨˩/</span><sup>([[:Category:Rhymes:Thai/aŋ|R]])</sup>[[Category:Rhymes:Thai/aŋ]]</td><td style="border-right:0px"><span class="IPA">/fa˦˥.raŋ˨˩/</span><sup>([[:Category:Rhymes:Thai/aŋ|R]])</sup>[[Category:Rhymes:Thai/aŋ]]</td></tr>
<tr><th colspan="2">''Audio''</th><td>[[File:Th-farang.ogg|100px|center]]</td><td></td></tr>
</table>[[Category:Thai terms with IPA pronunciation]][[Category:Thai 2-syllable words]][[Category:Thai 2-syllable words]][[Category:Thai terms with audio pronunciation]]""",
        )
        data = parse_page(
            self.wxr,
            "ฝรั่ง",
            """==Thai==
===Pronunciation===
{{th-pron|ฝะ-หฺรั่ง|ฟะ-หฺรั่ง:colloquial}}
===Noun===
# [[farang]]; [[Westerner]].""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "other": "ฝรั่ง",
                    "raw_tags": ["Orthographic"],
                    "roman": "f r ạ ˋ ŋ",
                },
                {
                    "other": "ฝะ-หฺรั่ง",
                    "raw_tags": ["Phonemic"],
                    "roman": "f a – h ̥ r ạ ˋ ŋ",
                },
                {
                    "other": "ฟะ-หฺรั่ง",
                    "raw_tags": ["Phonemic"],
                    "tags": ["colloquial"],
                    "roman": "v a – h ̥ r ạ ˋ ŋ",
                },
                {
                    "roman": "fà-ràng",
                    "raw_tags": ["Paiboon"],
                    "tags": ["romanization"],
                },
                {
                    "roman": "fá-ràng",
                    "raw_tags": ["Paiboon"],
                    "tags": ["romanization"],
                },
                {
                    "roman": "fa-rang",
                    "raw_tags": ["Royal Institute"],
                    "tags": ["romanization"],
                },
                {
                    "roman": "fa-rang",
                    "raw_tags": ["Royal Institute"],
                    "tags": ["romanization"],
                },
                {"ipa": "/fa˨˩.raŋ˨˩/"},
                {"ipa": "/fa˦˥.raŋ˨˩/"},
                {
                    "audio": "Th-farang.ogg",
                    "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/6/6b/Th-farang.ogg/Th-farang.ogg.mp3",
                    "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Th-farang.ogg",
                },
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "Rhymes:Thai/aŋ",
                "Thai terms with IPA pronunciation",
                "Thai 2-syllable words",
                "Thai terms with audio pronunciation",
            ],
        )

    def test_zh_pron_erhua(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div><div class="vsSwitcher" data-toggle-category="pronunciations">
<div class="vsHide" style="clear:right;">
<hr>
* [[w:Mandarin Chinese|Mandarin]]
** <small>(''[[w:Standard Chinese|Standard Chinese]], [[w:erhua|erhua]]-ed'') (<span class="Hant" lang="cmn">[[:旋兒#Mandarin|旋兒]]</span><span class="Zsym mention" style="font-size:100%;">&nbsp;/ </span><span class="Hans" lang="cmn">[[:旋儿#Mandarin|旋儿]]</span>)</small><sup><small><abbr title="Add Mandarin homophones"><span class="plainlinks">[//en.wiktionary.org/w/index.php?title=Module%3Azh%2Fdata%2Fcmn-hom%2F4&action=edit +]</span></abbr></small></sup>
*** <small>''[[w:Pinyin|Hanyu Pinyin]]''</small>: <span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace"><span class="Latn" lang="cmn">[[:xuánr#Mandarin|xuánr]]</span></span>
</div></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "旋",
            """==Chinese==
===Pronunciation 1===
{{zh-pron
|m=xuán,er=y
|cat=v,n,adv
}}
====Definitions====
# to [[revolve]]; to [[turn]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "raw_tags": ["旋兒 /旋儿"],
                    "tags": ["Mandarin", "Standard-Chinese", "Erhua", "Pinyin"],
                    "zh_pron": "xuánr",
                }
            ],
        )

    def test_zh_pron_section(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """{{#switch:{{{cat}}}
| pron = <div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="pronunciations">
* [[w:Mandarin Chinese|Mandarin]]
*:<small>(''[[w:Pinyin|Pinyin]]'')</small>: <span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace">[[dàjiā#Mandarin|dàjiā]], [[dà'ā#Mandarin|dà'ā]]</span>
</div></div>
| n = <div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="pronunciations">
* [[w:Mandarin Chinese|Mandarin]]
*:<small>(''[[w:Pinyin|Pinyin]]'')</small>: <span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace">[[dàgū#Mandarin|dàgū]]</span>
</div></div>
}}""",
        )
        data = parse_page(
            self.wxr,
            "大家",
            """==Chinese==
===Pronunciation 1===
{{zh-pron
|m=dàjiā,dà'ā,2nb=colloquial
|cat=pron
}}
====Pronoun====
# [[everyone]]

===Pronunciation 3===
{{zh-pron
|m=dàgū
|cat=n
}}
====Noun====
# 大姑""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"tags": ["Mandarin", "Pinyin"], "zh_pron": "dàjiā"},
                {"tags": ["Mandarin", "Pinyin"], "zh_pron": "dà'ā"},
            ],
        )
        self.assertEqual(
            data[1]["sounds"],
            [{"tags": ["Mandarin", "Pinyin"], "zh_pron": "dàgū"}],
        )

    def test_zh_pron_under_glyph_origin_and_etymology(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """{{#switch:{{{cat}}}
| v,n = <div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="pronunciations">
* [[w:Mandarin Chinese|Mandarin]]
*:<small>(''[[w:Pinyin|Pinyin]]'')</small>: <span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace">[[zuò#Mandarin|zuò]], [[zuó#Mandarin|zuó]] ([[zuo4|zuo<sup>4</sup>]], [[zuo2|zuo<sup>2</sup>]])</span>
</div></div>
| n,a = <div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="pronunciations">
* [[w:Mandarin Chinese|Mandarin]]
*:<small>(''[[w:Pinyin|Pinyin]]'')</small>: <span class="form-of pinyin-ts-form-of" lang="cmn" class="zhpron-monospace">[[zuō#Mandarin|zuō]] ([[zuo1|zuo<sup>1</sup>]])</span>
</div></div>
}}""",
        )
        data = parse_page(
            self.wxr,
            "作",
            """==Chinese==
===Glyph origin===
Phono-semantic compound
===Etymology===
Derivative: 做
===Pronunciation 1===
{{zh-pron
|m=zuò,zuó,2nb=variant
|cat=v,n
}}
====Definitions====
# to [[get up]]

===Pronunciation 2===
{{zh-pron
|m=zuō
|cat=n,a
}}
====Definitions====
# [[workshop]]""",
        )
        self.assertEqual(
            data[0]["etymology_text"],
            "Phono-semantic compound\nDerivative: 做",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"tags": ["Mandarin", "Pinyin"], "zh_pron": "zuò"},
                {"tags": ["Mandarin", "Pinyin"], "zh_pron": "zuó (zuo⁴, zuo²)"},
            ],
        )
        self.assertEqual(
            data[1]["etymology_text"],
            "Phono-semantic compound\nDerivative: 做",
        )
        self.assertEqual(
            data[1]["sounds"],
            [{"tags": ["Mandarin", "Pinyin"], "zh_pron": "zuō (zuo¹)"}],
        )

    def test_sound_before_etymology(self):
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            """[[Wiktionary:International Phonetic Alphabet|IPA]]<sup>([[Appendix:English pronunciation|key]])</sup>:&#32;<span class="IPA">/ˈtiː/</span>[[Category:English 1-syllable words|TEE]][[Category:English terms with IPA pronunciation|TEE]]""",
        )
        data = parse_page(
            self.wxr,
            "tee",
            """==English==
===Pronunciation===
* {{IPA|en|/ˈtiː/}}

===Etymology 1===
Etymology 1
====Noun====
# The name of the Latin-script letter T/t.
====Verb====
# To redirect output to multiple destinations.

===Etymology 2===
Etymology 2
====Noun====
# A flat area of ground""",
        )
        self.assertEqual(data[0]["etymology_text"], "Etymology 1")
        self.assertEqual(data[0]["etymology_text"], data[1]["etymology_text"])
        self.assertEqual(data[2]["etymology_text"], "Etymology 2")
        self.assertEqual(data[0]["sounds"], [{"ipa": "/ˈtiː/"}])
        self.assertEqual(data[0]["sounds"], data[1]["sounds"])
        self.assertEqual(data[0]["sounds"], data[2]["sounds"])

    def test_sound_inside_etymology(self):
        self.wxr.wtp.add_page(
            "Template:IPA",
            10,
            """[[Wiktionary:International Phonetic Alphabet|IPA]]<sup>([[Appendix:English pronunciation|key]])</sup>:&#32;<span class="IPA">{{{2}}}</span>[[Category:English 1-syllable words|TEE]][[Category:English terms with IPA pronunciation|TEE]]""",
        )
        data = parse_page(
            self.wxr,
            "tee",
            """==English==

===Etymology 1===
Etymology 1
====Pronunciation====
* {{IPA|en|/ˈtiː/}}
====Noun====
# The name of the Latin-script letter T/t.
====Verb====
# To redirect output to multiple destinations.

===Etymology 2===
Etymology 2
====Pronunciation====
* {{IPA|en|/ˈtaː/}}
====Noun====
# A flat area of ground""",
        )
        print(data)
        self.assertEqual(data[0]["etymology_text"], "Etymology 1")
        self.assertEqual(data[0]["etymology_text"], data[1]["etymology_text"])
        self.assertEqual(data[2]["etymology_text"], "Etymology 2")
        self.assertEqual(data[0]["sounds"], [{"ipa": "/ˈtiː/"}])
        self.assertEqual(data[2]["sounds"], [{"ipa": "/ˈtaː/"}])
        self.assertEqual(data[0]["sounds"], data[1]["sounds"])
        self.assertNotEqual(data[0]["sounds"], data[2]["sounds"])

    def test_zh_pron_nested_parentheses(self):
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """<div class="standard-box zhpron"><div class="vsSwitcher" data-toggle-category="pronunciations">
<div class="vsHide" style="clear:right;">
<hr>
* [[w:Mandarin Chinese|Mandarin]]
** <small>(''[[w:Standard Chinese|Standard Chinese]], standard in mainland China (with [[w:erhua|erhua]])'')</small><sup><small><abbr title="Add Mandarin homophones"><span class="plainlinks">[//en.wiktionary.org/w/index.php?title=Module%3Azh%2Fdata%2Fcmn-hom%2F1&action=edit +]</span></abbr></small></sup>
*** <small>''[[w:Pinyin|Hanyu Pinyin]]''</small>: <span class="form-of pinyin-t-form-of transliteration-断片" lang="cmn" class="zhpron-monospace"><span class="Latn" lang="cmn">[[:duànpiān#Mandarin|duànpiān]]</span></span>
</div></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "斷片",
            """==Chinese==
===Pronunciation 2===
{{zh-pron
|m=duànpiān,duànpiàn,er=y,2er=y,1nb=standard in mainland China (with erhua),2nb=standard in Taiwan
|c=tyun5 pin3-2
|cat=v
}}
====Verb====
# to [[break]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "tags": [
                        "Mandarin",
                        "Standard-Chinese",
                        "Mainland-China",
                        "standard",
                        "Erhua",
                        "Pinyin",
                    ],
                    "zh_pron": "duànpiān",
                }
            ],
        )

    def test_th_pron_th_tags(self):
        self.wxr.wtp.add_page(
            "Template:th-pron",
            10,
            """<table cellpadding=10>
<tr><th colspan="2">''[[w:Thai alphabet|Phonemic]]''<br><small>{<span title="This phonetic respelling violates Thai alphabet rules to indicate an irregular pronunciation.">Unorthographical</span>; <span title="The vowel in this word is pronounced irregularly short.">Short</span>}</small></th><td><div class="th-reading"><span lang="th" class="Thai ">เล็่น-เพื่อน</span><br><small><span title="Vowel sign appearing in front of the initial consonant.">e</span>&thinsp;l&thinsp;˘&thinsp;ˋ&thinsp;n&thinsp;&ndash;&thinsp;<span title="Vowel sign appearing in front of the initial consonant.">e</span>&thinsp;b&thinsp;ụ̄&thinsp;ˋ&thinsp;ɒ&thinsp;n</small></div></td></tr>
</table>""",
        )
        data = parse_page(
            self.wxr,
            "เล่นเพื่อน",
            """==Thai==
===Pronunciation===
{{th-pron|เล็่น-เพื่อน}}
===Verb===
# gloss""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "other": "เล็่น-เพื่อน",
                    "raw_tags": ["Phonemic", "Unorthographical", "Short"],
                    "roman": "e l ˘ ˋ n – e b ụ̄ ˋ ɒ n",
                }
            ],
        )

    def test_audio_dialect_tags(self):
        self.wxr.wtp.add_page(
            "Template:th-pron",
            10,
            """<table cellpadding=10>
<tr><th colspan="2">''[[w:Thai alphabet|Phonemic]]''<br><small>{<span title="This phonetic respelling violates Thai alphabet rules to indicate an irregular pronunciation.">Unorthographical</span>; <span title="The vowel in this word is pronounced irregularly short.">Short</span>}</small></th><td><div class="th-reading"><span lang="th" class="Thai ">เล็่น-เพื่อน</span><br><small><span title="Vowel sign appearing in front of the initial consonant.">e</span>&thinsp;l&thinsp;˘&thinsp;ˋ&thinsp;n&thinsp;&ndash;&thinsp;<span title="Vowel sign appearing in front of the initial consonant.">e</span>&thinsp;b&thinsp;ụ̄&thinsp;ˋ&thinsp;ɒ&thinsp;n</small></div></td></tr>
</table>""",
        )
        data = parse_page(
            self.wxr,
            "dizer",
            """==Portuguese==
===Pronunciation===
* {{audio|pt|LL-Q5146 (por)-JnpoJuwan-dizer.wav|a=<<Brazil>> (<<São Paulo>>)}}
===Verb===
# gloss""",
        )
        print(data[0]["sounds"])
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "audio": "LL-Q5146 (por)-JnpoJuwan-dizer.wav",
                    "tags": ["Brazil", "São-Paulo"],
                    "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/9/9c/LL-Q5146_%28por%29-JnpoJuwan-dizer.wav/LL-Q5146_%28por%29-JnpoJuwan-dizer.wav.ogg",
                    "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/9/9c/LL-Q5146_%28por%29-JnpoJuwan-dizer.wav/LL-Q5146_%28por%29-JnpoJuwan-dizer.wav.mp3",
                }
            ],
        )
