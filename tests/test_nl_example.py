from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="nl"),
            WiktionaryConfig(
                dump_file_lang_code="nl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_bijv_2(self):
        self.wxr.wtp.add_page(
            "Sjabloon:=jpn=",
            10,
            "== ''Japans'' ==",
            need_pre_expand=True,
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-noun-",
            10,
            "====''Zelfstandig naamwoord''====",
            need_pre_expand=True,
        )
        data = parse_page(
            self.wxr,
            "日本",
            """{{=jpn=}}
{{-noun-|jpn}}
# [[Japan]]
{{bijv-2|この[[車]]は'''日本'''[[製]]だ。|Deze auto werd gemaakt in '''Japan'''.}}""",
        )
        self.assertEqual(
            data[0]["senses"][0]["examples"],
            [
                {
                    "text": "この車は日本製だ。",
                    "translation": "Deze auto werd gemaakt in Japan.",
                }
            ],
        )

    def test_citeer(self):
        import wiktextract.clean as clean_module

        clean_module.IMAGE_LINK_RE = None  # clear cache
        self.wxr.wtp.add_page(
            "Sjabloon:=eng=",
            10,
            "== ''Engels'' ==",
            need_pre_expand=True,
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-noun-",
            10,
            "====''Zelfstandig naamwoord''====",
            need_pre_expand=True,
        )
        self.wxr.wtp.add_page(
            "Sjabloon:citeer",
            10,
            """#:«(in reactie op het lachende publiek)<br>'''Silence'''! I kill you!»<ref name="Spark of Insanity">[[Bestand:Crystal128-browser.svg|15px|link=https://www.youtube.com/watch?v=GBvfiCdk-jc&t=1m10s|Bronlink ]] [https://www.youtube.com/watch?v=GBvfiCdk-jc&t=1m10s Weblink bron]&#32;Jeff Dunham als ''Achmed the Dead Terrorist'' in “Spark of Insanity”&#32;(17 september 2007)</ref><div style="margin-left:2em;">'''''Stilte'''! Ik maak jullie af!''</div>""",
        )
        data = parse_page(
            self.wxr,
            "silence",
            """{{=eng=}}
{{-noun-|eng}}
# [[stilte]]
#*{{citeer
|soort=voorstelling
|lang=en
|actor=Jeff Dunham
|role=Achmed the Dead Terrorist
|url=https://www.youtube.com/watch?v=GBvfiCdk-jc&t=1m10s
|date=2007-09-17
|title=Spark of Insanity
|passage=(in reactie op het lachende publiek)<br>'''Silence'''! I kill you!
|vertaling='''Stilte'''! Ik maak jullie af!}}""",
        )
        self.assertEqual(data[0]["senses"][0]["glosses"], ["stilte"])
        self.assertEqual(
            data[0]["senses"][0]["examples"],
            [
                {
                    "text": "(in reactie op het lachende publiek)\nSilence! I kill you!",
                    "translation": "Stilte! Ik maak jullie af!",
                    "ref": "Weblink bron Jeff Dunham als Achmed the Dead Terrorist in “Spark of Insanity” (17 september 2007)",
                }
            ],
        )
