from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestEnDescendant(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_reconstruction(self):
        self.wxr.wtp.add_page(
            "Template:l",
            10,
            '<span class="Latn" lang="ine-pro">&#42;glew-t-</span>',
        )
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{1}}}
| ine-pro = <span class="desc-arr" title="reshaped by analogy or addition of morphemes">⇒</span>
| ine-bsl-pro = Proto-Balto-Slavic:
| sla-pro = Proto-Slavic:
| sl = Slovene: <span class="Latn" lang="sl">[[:gluta#Slovene|glûta]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">lump, swelling</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>
| iir-pro = Proto-Indo-Iranian:
| inc-pro = Proto-Indo-Aryan:
| sa = Sanskrit: <span class="Deva" lang="sa">[[:ग्लौ#Sanskrit|ग्लौ]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="sa-Latn" class="tr Latn">gláu-</span>, <span class="mention-gloss-double-quote">“</span><span class="mention-gloss">swelling, tumor</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>
}}""",
        )
        data = parse_page(
            self.wxr,
            "Reconstruction:Proto-Indo-European/glew-",
            """==Proto-Indo-European==
===Root===
# to [[ball]] up, [[clump]] together
====Extensions====
* {{l|ine-pro||*glew-t-}}
** {{desc|ine-pro||der=1|nolb=1}}
*** {{desc|ine-bsl-pro|}}
**** {{desc|sla-pro|}}
***** {{desc|sl|glûta|t=lump, swelling}}
====Derived terms====
* Unsorted formations:
** {{desc|iir-pro|}}
*** {{desc|inc-pro|}}
**** {{desc|sa|ग्लौ|tr=gláu-|t=swelling, tumor}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "unknown",
                    "lang_code": "ine-pro",
                    "raw_tags": ["derived"],
                    "word": "*glew-t-",
                    "descendants": [
                        {
                            "lang": "unknown",
                            "lang_code": "ine-pro",
                            "raw_tags": [
                                "reshaped by analogy or addition of morphemes"
                            ],
                            "descendants": [
                                {
                                    "lang": "Proto-Balto-Slavic",
                                    "lang_code": "ine-bsl-pro",
                                    "descendants": [
                                        {
                                            "lang": "Proto-Slavic",
                                            "lang_code": "sla-pro",
                                            "descendants": [
                                                {
                                                    "lang": "Slovene",
                                                    "lang_code": "sl",
                                                    "sense": "lump, swelling",
                                                    "word": "glûta",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "lang": "Unsorted formations",
                    "lang_code": "unknown",
                    "raw_tags": ["derived"],
                    "descendants": [
                        {
                            "lang": "Proto-Indo-Iranian",
                            "lang_code": "iir-pro",
                            "descendants": [
                                {
                                    "lang": "Proto-Indo-Aryan",
                                    "lang_code": "inc-pro",
                                    "descendants": [
                                        {
                                            "lang": "Sanskrit",
                                            "lang_code": "sa",
                                            "roman": "gláu-",
                                            "sense": "swelling, tumor",
                                            "word": "ग्लौ",
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                },
            ],
        )

    def test_desc_tags(self):
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """Livonian: <span class="Latn" lang="liv">[[:vež#Livonian|ve’ž]]</span>, <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">Salaca</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="liv">[[:vez#Livonian|vez]]</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">dated</span><span class="ib-brac qualifier-brac">)</span>""",
        )
        data = parse_page(
            self.wxr,
            "Reconstruction:Proto-Finnic/veci",
            """==Proto-Finnic==
===Noun===
# [[water]]
====Descendants====
* {{desc|liv|ve’ž|vez<q:Salaca>|qq2=dated}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {"lang": "Livonian", "lang_code": "liv", "word": "ve’ž"},
                {
                    "lang": "Livonian",
                    "lang_code": "liv",
                    "word": "vez",
                    "tags": ["Salaca", "dated"],
                },
            ],
        )

    def test_badly_formatted_language_names(self):
        self.wxr.wtp.add_page(
            "Template:l",
            10,
            '<span class="Latn" lang="ine-pro">&#42;glew-t-</span>',
        )
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{1}}}
| poz-pnp-pro = Proto-Nuclear Polynesian:
| poz-pep-pro = Proto-Eastern Polynesian:
| haw = Hawaiian: <span class="Latn" lang="haw"><a href="/wiki/kapu#Hawaiian" title="kapu">kapu</a></span><ul><li><span class="desc-arr" title="borrowed">→</span> English: <span class="Latn" lang="en"><a href="/wiki/kapu#English" title="kapu">kapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li>
| mi = Māori: <span class="Latn" lang="mi"><a href="/wiki/tapu#Māori" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
| ty = Tahitian: <span class="Latn" lang="ty"><a href="/wiki/tapu#Tahitian" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li>
| rap = Rapa Nui: <span class="Latn" lang="rap"><a href="/wiki/tapu#Rapa_Nui" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li>
| sm = Samoan: <span class="Latn" lang="sm"><a href="/wiki/tapu#Samoan" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
| tkl = Tokelauan: <span class="Latn" lang="tkl"><a href="/wiki/tapu#Tokelauan" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li></ul></li>
| to = Tongan: <span class="Latn" lang="to"><a href="/wiki/tapu#Tongan" title="tapu">tapu</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
| en = <span class="desc-arr" title="borrowed">→</span> English: <span class="Latn" lang="en"><a href="/wiki/taboo#English" title="taboo">taboo</a></span>
}}""",
        )
        data = parse_page(
            self.wxr,
            "Reconstruction:Proto-Polynesian/tapu",
            """==Proto-Polynesian==
===Adjective===
# [[taboo]]

====Descendants====
* {{desc|poz-pnp-pro|-}}
** {{desc|poz-pep-pro|-}}
*** Marquesic
**** {{desc|haw|kapu}}
*** Tahitic
**** {{desc|mi|tapu}}
**** {{desc|ty|tapu}}
*** {{desc|rap|tapu}}
** Samoic-Outlier
*** Samoic
**** {{desc|sm|tapu}}
**** {{desc|tkl|tapu}}
* Tongic
** {{desc|to|tapu}}
*** {{desc|en|taboo|bor=1}}
""",
        )
        print(data[0]["descendants"])
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang_code": "poz-pnp-pro",
                    "lang": "Proto-Nuclear Polynesian",
                    "descendants": [
                        {
                            "lang_code": "poz-pep-pro",
                            "lang": "Proto-Eastern Polynesian",
                            "descendants": [
                                {
                                    "lang_code": "unknown",
                                    "lang": "Marquesic",
                                    "descendants": [
                                        {
                                            "lang": "Hawaiian",
                                            "lang_code": "haw",
                                            "word": "kapu",
                                            "descendants": [
                                                {
                                                    "lang": "English",
                                                    "lang_code": "en",
                                                    "word": "kapu",
                                                    "raw_tags": ["borrowed"],
                                                }
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "lang_code": "unknown",
                                    "lang": "Tahitic",
                                    "descendants": [
                                        {
                                            "lang": "Māori",
                                            "lang_code": "mi",
                                            "word": "tapu",
                                        },
                                        {
                                            "lang": "Tahitian",
                                            "lang_code": "ty",
                                            "word": "tapu",
                                        },
                                    ],
                                },
                                {
                                    "lang": "Rapa Nui",
                                    "lang_code": "rap",
                                    "word": "tapu",
                                },
                            ],
                        },
                        {
                            "lang_code": "unknown",
                            "lang": "Samoic-Outlier",
                            "descendants": [
                                {
                                    "lang_code": "unknown",
                                    "lang": "Samoic",
                                    "descendants": [
                                        {
                                            "lang": "Samoan",
                                            "lang_code": "sm",
                                            "word": "tapu",
                                        },
                                        {
                                            "lang": "Tokelauan",
                                            "lang_code": "tkl",
                                            "word": "tapu",
                                        },
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Tongic",
                    "descendants": [
                        {
                            "lang": "Tongan",
                            "lang_code": "to",
                            "word": "tapu",
                            "descendants": [
                                {
                                    "lang": "English",
                                    "lang_code": "en",
                                    "word": "taboo",
                                    "raw_tags": ["borrowed"],
                                }
                            ],
                        }
                    ],
                },
            ],
        )
