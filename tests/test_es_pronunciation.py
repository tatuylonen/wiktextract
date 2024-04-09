import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.pronunciation import (
    process_audio_template,
    process_pron_graf_template,
)
from wiktextract.wxr_context import WiktextractContext


class TestESPronunciation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(
                lang_code="es",
                extension_tags={
                    "phonos": {"parents": ["phrasing"], "content": ["flow"]}
                },
            ),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_sound_file(self):
        self.wxr.wtp.start_page("amigo")
        self.wxr.wtp.add_page(
            "Plantilla:pron-graf",
            10,
            """{|
|<span>amigo</span>
|-
|'''pronunciación''' (AFI)
|[aˈmi.ɣ̞o] <phonos file="LL-Q1321 (spa)-AdrianAbdulBaha-amigo.wav" leng="es"><small>''Colombia''</small></phonos><br/>
|-
|'''rima'''
|[[:Categoría:ES:Rimas:i.ɡo|i.ɡo]][[Categoría:ES:Rimas:i.ɡo]]
|}""",
        )
        root = self.wxr.wtp.parse(
            "{{pron-graf|audio=LL-Q1321 (spa)-AdrianAbdulBaha-amigo.wav|aunota=Colombia}}"
        )
        word_entry = WordEntry(word="amigo", lang_code="es", lang="Español")
        process_pron_graf_template(self.wxr, word_entry, root.children[0])
        data = word_entry.model_dump(exclude_defaults=True)["sounds"]
        for key in data[0].copy().keys():
            if key.endswith("_url"):
                del data[0][key]
        self.assertEqual(
            data,
            [
                {
                    "ipa": "[aˈmi.ɣ̞o]",
                    "audio": "LL-Q1321 (spa)-AdrianAbdulBaha-amigo.wav",
                    "raw_tags": ["Colombia"],
                },
                {
                    "rhymes": "i.ɡo",
                },
            ],
        )

    def test_multiple_ipas(self):
        self.wxr.wtp.start_page("opposite")
        self.wxr.wtp.add_page(
            "Plantilla:pron-graf",
            10,
            """{|
|style="background:#DBDBDB;" colspan="2"|<span>opposite</span>
|-
|'''Reino Unido, Canadá''' (AFI)
|/ˈɒp.ə.zɪt/<br/>/ˈɒp.ə.sɪt/<br/>
|-
|'''EE. UU., Canadá''' (AFI)
|/ˈɑ.pə.sɪt/<br/>/ˈɑp.sɪt/<br/>/ˈɑ.pə.zɪt/<br/>
|-
|'''grafías alternativas'''
|[[opposit]]<ref>arcaica</ref>
|}""",
        )
        root = self.wxr.wtp.parse("""{{pron-graf|leng=en
|pron=Reino Unido, Canadá|fono=ˈɒp.ə.zɪt|fono2=ˈɒp.ə.sɪt
|2pron=EE. UU., Canadá|2fono=ˈɑ.pə.sɪt|2aunota=EE. UU.|2fono2=ˈɑp.sɪt|2fono3=ˈɑ.pə.zɪt
|g=opposit|gnota=arcaica}}""")
        word_entry = WordEntry(word="opposite", lang_code="en", lang="Inglés")
        process_pron_graf_template(self.wxr, word_entry, root.children[0])
        data = word_entry.model_dump(exclude_defaults=True)["sounds"]
        for key in data[1].copy().keys():
            if key.endswith("_url"):
                del data[1][key]
        self.assertEqual(
            data,
            [
                {
                    "ipa": "/ˈɒp.ə.zɪt/",
                    "raw_tags": ["Reino Unido, Canadá"],
                },
                {
                    "ipa": "/ˈɒp.ə.sɪt/",
                    "raw_tags": ["Reino Unido, Canadá"],
                },
                {
                    "ipa": "/ˈɑ.pə.sɪt/",
                    "raw_tags": ["EE. UU., Canadá"],
                },
                {
                    "ipa": "/ˈɑp.sɪt/",
                    "raw_tags": ["EE. UU., Canadá"],
                },
                {
                    "ipa": "/ˈɑ.pə.zɪt/",
                    "raw_tags": ["EE. UU., Canadá"],
                },
                {
                    "alternative": "opposit",
                    "note": "arcaica",
                },
            ],
        )

    def test_pron_graf_roman(self):
        self.wxr.wtp.start_page("月")
        self.wxr.wtp.add_page(
            "Plantilla:pron-graf",
            10,
            """{|
|<span>月</span>
|-
|'''pronunciación'''
|<span> falta [[Wikcionario:Pronunciación|agregar]]</span>
|-
|'''transliteraciones'''
|tsuki<ref>sustantivo, acepción 1</ref>,&nbsp;getsu<ref>sustantivo, acepción 2</ref>
|}""",
        )
        root = self.wxr.wtp.parse(
            "{{pron-graf|leng=ja|tl1=tsuki|tlnota1=sustantivo, acepción 1|tl2=getsu|tlnota2=sustantivo, acepción 2}}"
        )
        word_entry = WordEntry(word="月", lang_code="ja", lang="Japonés")
        process_pron_graf_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["sounds"],
            [
                {"roman": "tsuki", "note": "sustantivo, acepción 1"},
                {"roman": "getsu", "note": "sustantivo, acepción 2"},
            ],
        )

    def test_process_audio_template(self):
        # https://es.wiktionary.org/wiki/os#Latín
        self.wxr.wtp.start_page("os")
        word_entry = WordEntry(word="os", lang="Latín", lang_code="la")
        root = self.wxr.wtp.parse(
            "{{audio|la-cls-os-long.ogg|'''Audio''' (clásico)|nb=apr}}"
        )
        process_audio_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["sounds"],
            [
                {
                    "audio": "la-cls-os-long.ogg",
                    "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/18/La-cls-os-long.ogg/La-cls-os-long.ogg.mp3",
                    "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/la-cls-os-long.ogg",
                }
            ],
        )
