import unittest
from typing import List

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.pronunciation import process_pron_graf_template
from wiktextract.wxr_context import WiktextractContext


class TestESPronunciation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"), WiktionaryConfig(dump_file_lang_code="es")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> List[WordEntry]:
        return [WordEntry(word="test", lang_code="es", lang_name="Language")]

    def test_es_extract_pronunciation(self):
        # Test cases taken from https://es.wiktionary.org/wiki/Plantilla:pron-graf

        test_cases = [
            {
                "input": "{{pron-graf|fone=ˈsim.ple}}",
                "sounds": [{"ipa": ["ˈsim.ple"]}],
                "spellings": [],
            },
            {
                "input": "{{pron-graf|g=exemplo|gnota=desusado}}",
                "sounds": [],
                "spellings": [
                    {
                        "alternative": "exemplo",
                        "note": "desusado",
                        "same_pronunciation": True,
                    }
                ],
            },
            {
                "input": "{{pron-graf|leng=grc|tl=parádeigma}}",
                "sounds": [{"roman": ["parádeigma"]}],
                "spellings": [],
            },
            {
                "input": """{{pron-graf|leng=hit
            |ts=wa-a-tar|ts2=u̯a-a-tar
            |tl=wātar|tl2=u̯ātar
            |pron=no
            |v=𒉿𒋻|vnota=watar}}
            """,
                "sounds": [
                    {
                        "roman": ["wātar", "u̯ātar"],
                        "syllabic": ["wa-a-tar", "u̯a-a-tar"],
                    }
                ],
                "spellings": [
                    {
                        "alternative": "𒉿𒋻",
                        "note": "watar",
                        "same_pronunciation": False,
                    }
                ],
            },
            {
                "input": "{{pron-graf|leng=de|fone=ˈzɪm.pəl|fone2=ˈzɪmpl̩}}",
                "sounds": [{"ipa": ["ˈzɪm.pəl", "ˈzɪmpl̩"]}],
                "spellings": [],
            },
            {
                "input": "{{pron-graf|leng=en|pron=Reino Unido|fone=ˈɒ.pə.zɪt|fone2=ˈɒ.pə.sɪt|2pron=EE.UU.|2fone=ˈɑ.pə.sɪt|2fone2=ˈɑ.pə.sət}}",
                "sounds": [
                    {"ipa": ["ˈɒ.pə.zɪt", "ˈɒ.pə.sɪt"], "tag": ["Reino Unido"]},
                    {"ipa": ["ˈɑ.pə.sɪt", "ˈɑ.pə.sət"], "tag": ["EE.UU."]},
                ],
                "spellings": [],
            },
            {
                "input": "{{pron-graf|leng=en|pron=británico|audio2=En-uk-direction.ogg|2pron=americano|2audio=En-us-direction.ogg}}",
                "sounds": [
                    {
                        "audio": ["En-uk-direction.ogg"],
                        "tag": ["británico"],
                    },
                    {
                        "audio": ["En-us-direction.ogg"],
                        "tag": ["americano"],
                    },
                ],
                "spellings": [],
            }
            #             {
            #                 "input": """{{pron-graf|leng=??
            # |ts=pa-ra-me-tir-uš
            # |tl=parámetros
            # |pron=estándar|fone=paˈɾa.me.tɾos|audio=Example.ogg|fone2=paˈɾa.me.tɾoː|fono3=paˈra.me.tros
            # |2pron=segunda variación|2fono=paˈla.me.tlo|2fone2=paˈla.me.tɫo|2audio2=Example.ogg
            # |3pron=tercera variación|3fone=paˈʐa.me.tʐo|3audio=Example.ogg|g=𒉺𒊏𒈨𒋻𒍑|gnota=pa-ra-me-tar-uš
            # |v=𒉺𒊏𒈨𒋼𒊑𒍑|vnota=parámetreos
            # |h=parámetroz
            # |p=parametros|p2=barámetros|palt2=barámetrōs}}""",
            #                 "sounds": [],
            #                 "spellings": [],
            #             },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                # self.wxr.wtp.add_page("Modèle:pron-graf", 10, body="")
                self.wxr.wtp.start_page("")
                page_data = self.get_default_page_data()

                root = self.wxr.wtp.parse(case["input"])

                process_pron_graf_template(
                    self.wxr, page_data[-1], root.children[0]
                )

                if case["sounds"] != []:
                    sounds = page_data[0].model_dump(exclude_defaults=True)[
                        "sounds"
                    ]
                    for sound in sounds:
                        if "ogg_url" in sound:
                            del sound["ogg_url"]
                        if "mp3_url" in sound:
                            del sound["mp3_url"]
                    self.assertEqual(
                        sounds,
                        case["sounds"],
                    )
                else:
                    self.assertFalse(page_data[0].sounds, case["sounds"])

                if case["spellings"] != []:
                    self.assertEqual(
                        page_data[0].model_dump(exclude_defaults=True)[
                            "spellings"
                        ],
                        case["spellings"],
                    )
                else:
                    self.assertFalse(page_data[0].spellings, case["spellings"])
