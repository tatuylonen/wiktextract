from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
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
