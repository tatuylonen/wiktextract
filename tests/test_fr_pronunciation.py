from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.extractor.fr.pronunciation import extract_pronunciation
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_pron_list(self):
        page_data = [
            WordEntry(word="bonjour", lang_code="en", lang="Anglais"),
            WordEntry(word="bonjour", lang_code="fr", lang="Français"),
            WordEntry(word="bonjour", lang_code="fr", lang="Français"),
        ]
        self.wxr.wtp.add_page("Modèle:pron", 10, body="\\bɔ̃.ʒuʁ\\")
        self.wxr.wtp.start_page("bonjour")
        root = self.wxr.wtp.parse(
            """=== Prononciation ===
* {{pron|bɔ̃.ʒuʁ|fr}}
** {{écouter|France (Paris)|bõ.ʒuːʁ|audio=Fr-bonjour.ogg|lang=fr}}"""
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="bonjour", lang_code="fr", lang="Français"),
        )
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {"word": "bonjour", "lang_code": "en", "lang": "Anglais"},
                {
                    "word": "bonjour",
                    "lang_code": "fr",
                    "lang": "Français",
                    "sounds": [
                        {
                            "ipa": "\\bɔ̃.ʒuʁ\\",
                        },
                        {
                            "ipa": "bõ.ʒuːʁ",
                            "raw_tags": ["France (Paris)"],
                            "audio": "Fr-bonjour.ogg",
                            "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fr-bonjour.ogg",
                            "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/bc/Fr-bonjour.ogg/Fr-bonjour.ogg.mp3",
                        },
                    ],
                },
                {
                    "word": "bonjour",
                    "lang_code": "fr",
                    "lang": "Français",
                    "sounds": [
                        {
                            "ipa": "\\bɔ̃.ʒuʁ\\",
                        },
                        {
                            "ipa": "bõ.ʒuːʁ",
                            "raw_tags": ["France (Paris)"],
                            "audio": "Fr-bonjour.ogg",
                            "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fr-bonjour.ogg",
                            "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/bc/Fr-bonjour.ogg/Fr-bonjour.ogg.mp3",
                        },
                    ],
                },
            ],
        )

    def test_str_pron(self):
        page_data = []
        self.wxr.wtp.add_page("Modèle:Yale-zh", 10, body="Yale")
        self.wxr.wtp.start_page("你好")
        root = self.wxr.wtp.parse(
            """=== {{S|prononciation}} ===
* '''cantonais''' {{pron||yue}}
** {{Yale-zh}} : nei⁵hou²"""
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="你好", lang_code="zh", lang="Chinois"),
        )
        self.assertEqual(
            [
                sound.model_dump(exclude_defaults=True)
                for sound in page_data[-1].sounds
            ],
            [{"tags": ["Cantonese", "Yale"], "zh_pron": "nei⁵hou²"}],
        )

    def test_no_ipa(self):
        """
        The pronunciation block could have no IPA data but contain some audio
        files.
        Test wikitext from https://fr.wiktionary.org/wiki/mars
        """
        page_data = []
        self.wxr.wtp.start_page("mars")
        root = self.wxr.wtp.parse(
            """=== {{S|prononciation}} ===
{{ébauche-pron|sv}}
* {{écouter|lang=sv|Suède||audio=LL-Q9027 (swe)-Moonhouse-mars.wav}}"""
        )
        self.wxr.wtp.add_page(
            "Modèle:écouter",
            10,
            "<span><span>Suède</span>&nbsp;: écouter «&nbsp;<span>mars</span> <span><span>[<small><span>[//fr.wiktionary.org Prononciation ?]</span></small>]</span></span>&nbsp;» <span>[[File:LL-Q9027 (swe)-Moonhouse-mars.wav]]</span></span>",
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="你好", lang_code="fr", lang="Français"),
        )
        self.assertEqual(
            page_data[-1].sounds[0].model_dump(exclude_defaults=True),
            {
                "raw_tags": ["Suède"],
                "audio": "LL-Q9027 (swe)-Moonhouse-mars.wav",
                "wav_url": "https://commons.wikimedia.org/wiki/Special:FilePath/LL-Q9027 (swe)-Moonhouse-mars.wav",
                "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3f/LL-Q9027_(swe)-Moonhouse-mars.wav/LL-Q9027_(swe)-Moonhouse-mars.wav.ogg",
                "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3f/LL-Q9027_(swe)-Moonhouse-mars.wav/LL-Q9027_(swe)-Moonhouse-mars.wav.mp3",
            },
        )

    def test_paronymes_subsection(self):
        # https://fr.wiktionary.org/wiki/wagonnet
        page_data = []
        self.wxr.wtp.add_page("Modèle:pron", 10, body="\\{{{1|}}}\\")
        self.wxr.wtp.start_page("wagonnet")
        root = self.wxr.wtp.parse(
            """=== {{S|prononciation}} ===
* {{pron|va.ɡɔ.nɛ|fr}}

==== {{S|paronymes}} ====
* [[wagonnée]]
* [[wagonnier]]
"""
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="wagonnet", lang_code="fr", lang="Français"),
        )
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True),
            {
                "word": "wagonnet",
                "lang_code": "fr",
                "lang": "Français",
                "paronyms": [{"word": "wagonnée"}, {"word": "wagonnier"}],
                "sounds": [{"ipa": "\\va.ɡɔ.nɛ\\"}],
            },
        )

    def test_pron_prim_template(self):
        page_data = []
        self.wxr.wtp.start_page("dictionnaire")
        root = self.wxr.wtp.parse(
            "=== {{S|prononciation}} ===\n* {{pron-rimes|dik.sjɔ.nɛʁ|fr}}"
        )
        self.wxr.wtp.add_page(
            "Modèle:pron-rimes",
            10,
            'La prononciation <span class="API" title="Prononciation API">\\dik.sjɔ.nɛʁ\\</span> rime avec les [[Annexe:Rimes en français en \\ɛʁ\\|mots qui finissent en <span class="API" title="Prononciation API">\\ɛʁ\\</span>]].[[Catégorie:Rimes en français en \\ɛʁ\\]]',
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="dictionnaire", lang_code="fr", lang="Français"),
        )
        data = page_data[0].model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"], [{"ipa": "\\dik.sjɔ.nɛʁ\\", "rhymes": "\\ɛʁ\\"}]
        )
        self.assertEqual(data["categories"], ["Rimes en français en \\ɛʁ\\"])

    def test_cmn_pron(self):
        # GH issue 620
        page_data = []
        self.wxr.wtp.start_page("作")
        root = self.wxr.wtp.parse(
            "=== {{S|prononciation}} ===\n{{cmn-pron|zuō|zuó|zuò}}"
        )
        self.wxr.wtp.add_page(
            "Modèle:pinyin",
            10,
            "[[Wiktionnaire:Sinogrammes - Index Pinyin|Pinyin]]",
        )
        self.wxr.wtp.add_page("Modèle:EFEO", 10, "[[EFEO|EFEO]]")
        self.wxr.wtp.add_page("Modèle:Wade", 10, "[[w:Wade-Giles|Wade-Giles]]")
        self.wxr.wtp.add_page(
            "Modèle:Yale-zh", 10, "[[w:Romanisation Yale|Yale]]"
        )
        self.wxr.wtp.add_page("Modèle:zhuyin", 10, "[[zhuyin|Zhuyin]]")
        self.wxr.wtp.add_page(
            "Modèle:lang",
            10,
            '<span lang="{{{1}}}" xml:lang="{{{1}}}" class="lang-{{{1}}}"><bdi>{{{2}}}</bdi></span>',
        )
        self.wxr.wtp.add_page(
            "Modèle:cmn-pron",
            10,
            """* '''mandarin''' [[Annexe:Prononciation/mandarin|<span class="API" title="Prononciation API">\\t͡su̯ɔ˥\\</span>]], [[Annexe:Prononciation/mandarin|<span class="API" title="Prononciation API">\\t͡su̯ɔ˧˥\\</span>]], [[Annexe:Prononciation/mandarin|<span class="API" title="Prononciation API">\\t͡su̯ɔ˥˩\\</span>]]
** {{pinyin}} : {{lang|"zh-Latn-pinyin|zuō, zuó, zuò}}
** {{EFEO}} : {{lang|zh-Latn|tso, tso, tso}}
** {{Wade}} : {{lang|zh-Latn|tso<sup>1</sup>, tso<sup>2</sup>, tso<sup>4</sup>}}
** {{Yale-zh}} : {{lang|zh-Latn|dzwō, dzwó, dzwò}}
** {{zhuyin}} : {{lang|zh-Bopomofo|ㄗㄨㄛ，ㄗㄨㄛˊ，ㄗㄨㄛˋ}}""",
        )
        extract_pronunciation(
            self.wxr,
            page_data,
            root.children[0],
            WordEntry(word="作", lang_code="zh", lang="Chinois"),
        )
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[0].sounds],
            [
                {"ipa": "\\t͡su̯ɔ˥\\", "tags": ["Mandarin"]},
                {"ipa": "\\t͡su̯ɔ˧˥\\", "tags": ["Mandarin"]},
                {"ipa": "\\t͡su̯ɔ˥˩\\", "tags": ["Mandarin"]},
                {"zh_pron": "zuō", "tags": ["Mandarin", "Pinyin"]},
                {"zh_pron": "zuó", "tags": ["Mandarin", "Pinyin"]},
                {"zh_pron": "zuò", "tags": ["Mandarin", "Pinyin"]},
                {"zh_pron": "tso", "tags": ["Mandarin", "EFEO"]},
                {"zh_pron": "tso¹", "tags": ["Mandarin", "Wade-Giles"]},
                {"zh_pron": "tso²", "tags": ["Mandarin", "Wade-Giles"]},
                {"zh_pron": "tso⁴", "tags": ["Mandarin", "Wade-Giles"]},
                {"zh_pron": "dzwō", "tags": ["Mandarin", "Yale"]},
                {"zh_pron": "dzwó", "tags": ["Mandarin", "Yale"]},
                {"zh_pron": "dzwò", "tags": ["Mandarin", "Yale"]},
                {"zh_pron": "ㄗㄨㄛ", "tags": ["Mandarin", "bopomofo"]},
                {"zh_pron": "ㄗㄨㄛˊ", "tags": ["Mandarin", "bopomofo"]},
                {"zh_pron": "ㄗㄨㄛˋ", "tags": ["Mandarin", "bopomofo"]},
            ],
        )
