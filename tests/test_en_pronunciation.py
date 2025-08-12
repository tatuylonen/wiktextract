from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.extractor.en.pronunciation import parse_pronunciation
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
                    "other": "fà-ràng",
                    "raw_tags": ["Paiboon"],
                    "tags": ["romanization"],
                },
                {
                    "other": "fá-ràng",
                    "raw_tags": ["Paiboon"],
                    "tags": ["romanization"],
                },
                {
                    "other": "fa-rang",
                    "raw_tags": ["Royal Institute"],
                    "tags": ["romanization"],
                },
                {
                    "other": "fa-rang",
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
