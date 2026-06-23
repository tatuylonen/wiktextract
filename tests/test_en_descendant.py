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
        print(data[0]["descendants"])
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "unknown",
                    "lang_code": "ine-pro",
                    "tags": ["derived"],
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
                    "tags": ["derived"],
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

    def test_badly_formatted_language_names2(self):
        # habeo/Latin
        self.wxr.wtp.add_page(
            "Template:top3",
            10,
            """<div class="columns-bg ul-column-count" data-column-count="3">""",
        )
        self.wxr.wtp.add_page(
            "Template:bottom",
            10,
            """</div>""",
        )
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{1}}}
|rup = Aromanian: <span class="Latn" lang="rup"><a href="/wiki/amu#Aromanian" title="amu">amu</a></span>, <span class="Latn" lang="rup"><a href="/wiki/am#Aromanian" title="am">am</a></span>, <span class="Latn" lang="rup"><a href="/wiki/aveari#Aromanian" title="aveari">aveari</a></span><style data-mw-deduplicate="TemplateStyles:r68481116">.mw-parser-output .desc-arr[title]{cursor:help}.mw-parser-output .desc-arr[title="uncertain"]{font-size:.7em;vertical-align:super}</style>
|ruo = Istro-Romanian: <span class="Latn" lang="ruo"><a href="/wiki/am#Istro-Romanian" title="am">am</a></span>, <span class="Latn" lang="ruo"><a href="/wiki/amu#Istro-Romanian" title="amu">amu</a></span>, <span class="Latn" lang="ruo"><a href="/wiki/ve#Istro-Romanian" title="ve">ve</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|ruq = Megleno-Romanian: <span class="Latn" lang="ruq"><a href="/wiki/am#Megleno-Romanian" title="am">am</a></span>, <span class="Latn" lang="ruq"><a href="/w/index.php?title=veari&amp;action=edit&amp;redlink=1" class="new" title="veari (page does not exist)">veari</a></span>, <span class="Latn" lang="ruq"><a href="/wiki/veri#Megleno-Romanian" title="veri">veri</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|ro = Romanian: <span class="Latn" lang="ro"><a href="/wiki/avea#Romanian" title="avea">avea</a></span>, <span class="Latn" lang="ro"><a href="/wiki/avere#Romanian" title="avere">avere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|co = Corsican: <span class="Latn" lang="co"><a href="/wiki/av%C3%A8#Corsican" title="avè">avè</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|dlm = Dalmatian: <span class="Latn" lang="dlm"><a href="/wiki/avar#Dalmatian" title="avar">avar</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|ist = Istriot: <span class="Latn" lang="ist"><a href="/wiki/av%C3%AC#Istriot" title="avì">avì</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|it = Italian: <span class="Latn" lang="it"><a href="/wiki/avere#Italian" title="avere">avere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|nap = Neapolitan: <span class="Latn" lang="nap"><a href="/wiki/avere#Neapolitan" title="avere">avere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|scn = Sicilian: <span class="Latn" lang="scn"><a href="/wiki/aviri#Sicilian" title="aviri">aviri</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|vec = Venetan: <span class="Latn" lang="vec"><a href="/wiki/aver#Venetan" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|egl = Emilian: <span class="Latn" lang="egl"><a href="/wiki/avair#Emilian" title="avair">avair</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|lld = Ladin: <span class="Latn" lang="lld"><a href="/wiki/avei#Ladin" title="avei">avei</a></span>, <span class="Latn" lang="lld"><a href="/wiki/av%C3%ABi#Ladin" title="avëi">avëi</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|lij = Ligurian: <span class="Latn" lang="lij"><a href="/wiki/av%C3%A9i#Ligurian" title="avéi">avéi</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|pms = Piedmontese: <span class="Latn" lang="pms"><a href="/wiki/av%C3%A8j#Piedmontese" title="avèj">avèj</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|rgn = Romagnol: <span class="Latn" lang="rgn"><a href="/wiki/av%C3%A9r#Romagnol" title="avér">avér</a></span>, <span class="Latn" lang="rgn"><a href="/wiki/av%C4%93r#Romagnol" title="avēr">avēr</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|fur = Friulian: <span class="Latn" lang="fur"><a href="/wiki/v%C3%AA#Friulian" title="vê">vê</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|rm = Romansh: <span class="Latn" lang="rm"><a href="/wiki/avair#Romansh" title="avair">avair</a></span>, <span class="Latn" lang="rm"><a href="/wiki/haver#Romansh" title="haver">haver</a></span>, <span class="Latn" lang="rm"><a href="/wiki/aver#Romansh" title="aver">aver</a></span>, <span class="Latn" lang="rm"><a href="/wiki/aveir#Romansh" title="aveir">aveir</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|frp = Franco-Provençal: <span class="Latn" lang="frp"><a href="/wiki/av%C3%AAr#Franco-Provençal" title="avêr">avêr</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|roa-ang = Angevin: <span class="Latn" lang="roa-ang"><a href="/wiki/avair#Angevin" title="avair">avair</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|roa-bbn = Bourbonnais-Berrichon: <span class="Latn" lang="roa-bbn"><a href="/wiki/avo%C3%A9r#Bourbonnais-Berrichon" title="avoér">avoér</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|roa-cha = Champenois: <span class="Latn" lang="roa-cha"><a href="/w/index.php?title=aivoir&amp;action=edit&amp;redlink=1" class="new" title="aivoir (page does not exist)">aivoir</a></span>, <span class="Latn" lang="roa-cha"><a href="/w/index.php?title=aivor&amp;action=edit&amp;redlink=1" class="new" title="aivor (page does not exist)">aivor</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|fro = Old French: <span class="Latn" lang="fro"><a href="/wiki/avoir#Old_French" title="avoir">avoir</a></span>, <span class="Latn" lang="fro"><a href="/wiki/aveir#Old_French" title="aveir">aveir</a></span>, <span class="Latn" lang="fro"><a href="/wiki/aver#Old_French" title="aver">aver</a></span> <span class="ib-brac label-brac">(</span><span class="ib-content label-content">archaic or northern</span><span class="ib-brac label-brac">)</span>, <span class="Latn" lang="fro"><a href="/wiki/avoyr#Old_French" title="avoyr">avoyr</a></span> <span class="ib-brac label-brac">(</span><span class="ib-content label-content">alternative spelling</span><span class="ib-brac label-brac">)</span><ul><li>Bourguignon: <span class="Latn" lang="roa-brg"><a href="/wiki/aivoi#Bourguignon" title="aivoi">aivoi</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Gallo: <span class="Latn" lang="roa-gal"><a href="/wiki/aveir#Gallo" title="aveir">aveir</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Middle French: <span class="Latn" lang="frm"><a href="/wiki/avoir#Middle_French" title="avoir">avoir</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"><ul><li>French: <span class="Latn" lang="fr"><a href="/wiki/avoir#French" title="avoir">avoir</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li><li>Norman: <span class="Latn" lang="nrf"><a href="/wiki/aveir#Norman" title="aveir">aveir</a></span>, <span class="Latn" lang="nrf"><a href="/wiki/aver#Norman" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Picard: <span class="Latn" lang="pcd"><a href="/wiki/avo%C3%A8r#Picard" class="mw-redirect" title="avoèr">avoèr</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Walloon: <span class="Latn" lang="wa"><a href="/wiki/aveur#Walloon" title="aveur">aveur</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li><span class="desc-arr" title="borrowed">→</span> Middle English: <span class="Latn" lang="enm"><a href="/wiki/aver#Middle_English" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"><ul><li>English: <span class="Latn" lang="en"><a href="/wiki/aver#English" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li></ul></li></ul></li></ul>
|ca = Catalan: <span class="Latn" lang="ca"><a href="/wiki/haver#Catalan" title="haver">haver</a></span>, <span class="Latn" lang="ca"><a href="/wiki/heure#Catalan" title="heure">heure</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|pro = Old Occitan: <span class="Latn" lang="pro"><a href="/wiki/aver#Old_Occitan" title="aver">aver</a></span>, <span class="Latn" lang="pro"><a href="/wiki/haver#Old_Occitan" title="haver">haver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|oc = Occitan: <span class="Latn" lang="oc"><a href="/wiki/aver#Occitan" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|oc-gas = Gascon: <span class="Latn" lang="oc"><a href="/w/index.php?title=%C3%A0uger&amp;action=edit&amp;redlink=1" class="new" title="àuger (page does not exist)">àuger</a></span>, <span class="Latn" lang="oc"><a href="/wiki/er#Occitan" title="er">er</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|oc-pro = Provençal: <span class="Latn" lang="oc"><a href="/w/index.php?title=aguer&amp;action=edit&amp;redlink=1" class="new" title="aguer (page does not exist)">aguer</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|oc-viv = Vivaro-Alpine: <span class="Latn" lang="oc"><a href="/w/index.php?title=aguer&amp;action=edit&amp;redlink=1" class="new" title="aguer (page does not exist)">aguer</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|an = Aragonese: <span class="Latn" lang="an"><a href="/wiki/haber#Aragonese" title="haber">haber</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|roa-ole = Old Leonese: <span class="Latn" lang="roa-ole"><a href="/wiki/aver#Old_Leonese" title="aver">aver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|ast = Asturian: <span class="Latn" lang="ast"><a href="/wiki/haber#Asturian" title="haber">haber</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|ext = Extremaduran: <span class="Latn" lang="ext"><a href="/wiki/avel#Extremaduran" title="avel">avel</a></span>, <span class="Latn" lang="ext"><a href="/wiki/bel#Extremaduran" title="bel">bel</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|roa-leo = Leonese: <span class="Latn" lang="roa-leo"><a href="/wiki/habere#Leonese" title="habere">habere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|mwl = Mirandese: <span class="Latn" lang="mwl"><a href="/wiki/haber#Mirandese" title="haber">haber</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|roa-opt = Old Galician-Portuguese: <span class="Latn" lang="roa-opt"><a href="/wiki/aver#Old_Galician-Portuguese" title="aver">aver</a></span>, <span class="Latn" lang="roa-opt"><a href="/wiki/haver#Old_Galician-Portuguese" title="haver">haver</a></span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">latinized form</span><span class="ib-brac qualifier-brac">)</span><ul><li>Galician: <span class="Latn" lang="gl"><a href="/wiki/haber#Galician" title="haber">haber</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Portuguese: <span class="Latn" lang="pt"><a href="/wiki/haver#Portuguese" title="haver">haver</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul>
|osp = Old Spanish: <span class="Latn" lang="osp"><a href="/wiki/aver#Old_Spanish" title="aver">aver</a></span><ul><li>Ladino: <span class="Latn" lang="lad"><a href="/wiki/aver#Ladino" title="aver">aver</a></span><span class="Zsym mention" style="font-size:100%;">&nbsp;/ </span><span class="Hebr" lang="lad"><a href="/wiki/%D7%90%D7%91%D7%99%D7%A8#Ladino" title="אביר">אביר</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li><li>Spanish: <span class="Latn" lang="es"><a href="/wiki/haber#Spanish" title="haber">haber</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li></ul>
|sc-old = Old Sardinian: <span class="Latn" lang="sc"><a href="/wiki/avere#Sardinian" title="avere">avere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|sc-sro = Campidanese: <span class="Latn" lang="sc"><a href="/wiki/ai#Sardinian" title="ai">ai</a></span>, <span class="Latn" lang="sc"><a href="/wiki/airi#Sardinian" title="airi">airi</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116">
|sc-src = Logudorese: <span class="Latn" lang="sc"><a href="/wiki/%C3%A0ere#Sardinian" title="àere">àere</a></span><link rel="mw-deduplicated-inline-style" href="mw-data:TemplateStyles:r68481116"></li></ul></li></ul></li></ul>
}}""",
        )
        data = parse_page(
            self.wxr,
            "Reconstruction:Proto-Polynesian/tapu",
            """==Latin==
===Verb===
# [[foo]]

====Descendants====
{{top3}}
* Balkan Romance:
** {{desc|rup|amu|am|aveari}}
** {{desc|ruo|am|amu|ve}}
** {{desc|ruq|am|veari|veri}}
** {{desc|ro|avea|avere}}
* Italo-Dalmatian:
** {{desc|co|avè}}
** {{desc|dlm|avar}}
** {{desc|ist|avì}}
** {{desc|it|avere}}
** {{desc|nap|avere}}
** {{desc|scn|aviri}}
** {{desc|vec|aver}}
* Padanian:
** {{desc|egl|avair}}
** {{desc|lld|avei|avëi}}
** {{desc|lij|avéi}}
** {{desc|pms|avèj}}
** {{desc|rgn|avér|avēr}}
* Rhaeto-Romance:
** {{desc|fur|vê}}
** {{desc|rm|avair|haver|aver|aveir}}
* Gallo-Romance:
** {{desc|frp|avêr}}
** Oïl:
*** {{desc|roa-ang|avair}}
*** {{desc|roa-bbn|avoér}}
*** {{desc|roa-cha|aivoir|aivor}}
*** {{desc|fro|avoir}}
* Occitano-Romance:
** {{desc|ca|haver|heure}}
** {{desc|pro|aver|haver}}
*** {{desc|oc|aver}}
**** {{desc|oc-gas|àuger|er}}
**** {{desc|oc-pro|aguer}}
**** {{desc|oc-viv|aguer}}
**** Forms perhaps influenced by deriv's of {{m|la|videō|vidēre}}:
****: {{desc|oc-gas|aveir}}, {{l|oc-gas|avéser}}, {{l|oc-gas|avéder}}, {{l|oc-gas|eir}}
****: {{desc|oc-lan|aveire}}, {{l|oc-lan|avedre}}
* Ibero-Romance:
** {{desc|an|haber}}
** {{desc|roa-ole|aver}}
*** {{desc|ast|haber}}
*** {{desc|ext|avel|bel}}
*** {{desc|roa-leo|habere}}
*** {{desc|mwl|haber}}
** {{desc|roa-opt|aver}}
** {{desc|osp|aver}}
* Insular Romance:
** {{desc|sc-old|avere}}
*** {{desc|sc-sro|ai|airi}}
*** {{desc|sc-src|àere}}
{{bottom}}
""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang_code": "unknown",
                    "lang": "Balkan Romance",
                    "descendants": [
                        {
                            "lang": "Aromanian",
                            "lang_code": "rup",
                            "word": "amu",
                        },
                        {"lang": "Aromanian", "lang_code": "rup", "word": "am"},
                        {
                            "lang": "Aromanian",
                            "lang_code": "rup",
                            "word": "aveari",
                        },
                        {
                            "lang": "Istro-Romanian",
                            "lang_code": "ruo",
                            "word": "am",
                        },
                        {
                            "lang": "Istro-Romanian",
                            "lang_code": "ruo",
                            "word": "amu",
                        },
                        {
                            "lang": "Istro-Romanian",
                            "lang_code": "ruo",
                            "word": "ve",
                        },
                        {
                            "lang": "Megleno-Romanian",
                            "lang_code": "ruq",
                            "word": "am",
                        },
                        {
                            "lang": "Megleno-Romanian",
                            "lang_code": "ruq",
                            "word": "veari",
                        },
                        {
                            "lang": "Megleno-Romanian",
                            "lang_code": "ruq",
                            "word": "veri",
                        },
                        {"lang": "Romanian", "lang_code": "ro", "word": "avea"},
                        {
                            "lang": "Romanian",
                            "lang_code": "ro",
                            "word": "avere",
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Italo-Dalmatian",
                    "descendants": [
                        {"lang": "Corsican", "lang_code": "co", "word": "avè"},
                        {
                            "lang": "Dalmatian",
                            "lang_code": "dlm",
                            "word": "avar",
                        },
                        {"lang": "Istriot", "lang_code": "ist", "word": "avì"},
                        {"lang": "Italian", "lang_code": "it", "word": "avere"},
                        {
                            "lang": "Neapolitan",
                            "lang_code": "nap",
                            "word": "avere",
                        },
                        {
                            "lang": "Sicilian",
                            "lang_code": "scn",
                            "word": "aviri",
                        },
                        {"lang": "Venetan", "lang_code": "vec", "word": "aver"},
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Padanian",
                    "descendants": [
                        {
                            "lang": "Emilian",
                            "lang_code": "egl",
                            "word": "avair",
                        },
                        {"lang": "Ladin", "lang_code": "lld", "word": "avei"},
                        {"lang": "Ladin", "lang_code": "lld", "word": "avëi"},
                        {
                            "lang": "Ligurian",
                            "lang_code": "lij",
                            "word": "avéi",
                        },
                        {
                            "lang": "Piedmontese",
                            "lang_code": "pms",
                            "word": "avèj",
                        },
                        {
                            "lang": "Romagnol",
                            "lang_code": "rgn",
                            "word": "avér",
                        },
                        {
                            "lang": "Romagnol",
                            "lang_code": "rgn",
                            "word": "avēr",
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Rhaeto-Romance",
                    "descendants": [
                        {"lang": "Friulian", "lang_code": "fur", "word": "vê"},
                        {"lang": "Romansh", "lang_code": "rm", "word": "avair"},
                        {"lang": "Romansh", "lang_code": "rm", "word": "haver"},
                        {"lang": "Romansh", "lang_code": "rm", "word": "aver"},
                        {"lang": "Romansh", "lang_code": "rm", "word": "aveir"},
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Gallo-Romance",
                    "descendants": [
                        {
                            "lang": "Franco-Provençal",
                            "lang_code": "frp",
                            "word": "avêr",
                        },
                        {
                            "lang_code": "unknown",
                            "lang": "Oïl",
                            "descendants": [
                                {
                                    "lang": "Angevin",
                                    "lang_code": "roa-ang",
                                    "word": "avair",
                                },
                                {
                                    "lang": "Bourbonnais-Berrichon",
                                    "lang_code": "roa-bbn",
                                    "word": "avoér",
                                },
                                {
                                    "lang": "Champenois",
                                    "lang_code": "roa-cha",
                                    "word": "aivoir",
                                },
                                {
                                    "lang": "Champenois",
                                    "lang_code": "roa-cha",
                                    "word": "aivor",
                                },
                                {
                                    "lang": "Old French",
                                    "lang_code": "fro",
                                    "word": "avoir",
                                    "descendants": [
                                        {
                                            "lang": "Bourguignon",
                                            "lang_code": "roa-brg",
                                            "word": "aivoi",
                                        },
                                        {
                                            "lang": "Gallo",
                                            "lang_code": "roa-gal",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Middle French",
                                            "lang_code": "frm",
                                            "word": "avoir",
                                            "descendants": [
                                                {
                                                    "lang": "French",
                                                    "lang_code": "fr",
                                                    "word": "avoir",
                                                }
                                            ],
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aver",
                                        },
                                        {
                                            "lang": "Picard",
                                            "lang_code": "pcd",
                                            "word": "avoèr",
                                        },
                                        {
                                            "lang": "Walloon",
                                            "lang_code": "wa",
                                            "word": "aveur",
                                        },
                                        {
                                            "lang": "Middle English",
                                            "lang_code": "enm",
                                            "word": "aver",
                                            "raw_tags": ["borrowed"],
                                            "descendants": [
                                                {
                                                    "lang": "English",
                                                    "lang_code": "en",
                                                    "word": "aver",
                                                }
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "lang": "Old French",
                                    "lang_code": "fro",
                                    "word": "aveir",
                                    "descendants": [
                                        {
                                            "lang": "Bourguignon",
                                            "lang_code": "roa-brg",
                                            "word": "aivoi",
                                        },
                                        {
                                            "lang": "Gallo",
                                            "lang_code": "roa-gal",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Middle French",
                                            "lang_code": "frm",
                                            "word": "avoir",
                                            "descendants": [
                                                {
                                                    "lang": "French",
                                                    "lang_code": "fr",
                                                    "word": "avoir",
                                                }
                                            ],
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aver",
                                        },
                                        {
                                            "lang": "Picard",
                                            "lang_code": "pcd",
                                            "word": "avoèr",
                                        },
                                        {
                                            "lang": "Walloon",
                                            "lang_code": "wa",
                                            "word": "aveur",
                                        },
                                        {
                                            "lang": "Middle English",
                                            "lang_code": "enm",
                                            "word": "aver",
                                            "raw_tags": ["borrowed"],
                                            "descendants": [
                                                {
                                                    "lang": "English",
                                                    "lang_code": "en",
                                                    "word": "aver",
                                                }
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "lang": "Old French",
                                    "lang_code": "fro",
                                    "word": "aver",
                                    "raw_tags": ["archaic or northern"],
                                    "descendants": [
                                        {
                                            "lang": "Bourguignon",
                                            "lang_code": "roa-brg",
                                            "word": "aivoi",
                                        },
                                        {
                                            "lang": "Gallo",
                                            "lang_code": "roa-gal",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Middle French",
                                            "lang_code": "frm",
                                            "word": "avoir",
                                            "descendants": [
                                                {
                                                    "lang": "French",
                                                    "lang_code": "fr",
                                                    "word": "avoir",
                                                }
                                            ],
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aver",
                                        },
                                        {
                                            "lang": "Picard",
                                            "lang_code": "pcd",
                                            "word": "avoèr",
                                        },
                                        {
                                            "lang": "Walloon",
                                            "lang_code": "wa",
                                            "word": "aveur",
                                        },
                                        {
                                            "lang": "Middle English",
                                            "lang_code": "enm",
                                            "word": "aver",
                                            "raw_tags": ["borrowed"],
                                            "descendants": [
                                                {
                                                    "lang": "English",
                                                    "lang_code": "en",
                                                    "word": "aver",
                                                }
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "lang": "Old French",
                                    "lang_code": "fro",
                                    "word": "avoyr",
                                    "raw_tags": ["alternative spelling"],
                                    "descendants": [
                                        {
                                            "lang": "Bourguignon",
                                            "lang_code": "roa-brg",
                                            "word": "aivoi",
                                        },
                                        {
                                            "lang": "Gallo",
                                            "lang_code": "roa-gal",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Middle French",
                                            "lang_code": "frm",
                                            "word": "avoir",
                                            "descendants": [
                                                {
                                                    "lang": "French",
                                                    "lang_code": "fr",
                                                    "word": "avoir",
                                                }
                                            ],
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aveir",
                                        },
                                        {
                                            "lang": "Norman",
                                            "lang_code": "nrm",
                                            "word": "aver",
                                        },
                                        {
                                            "lang": "Picard",
                                            "lang_code": "pcd",
                                            "word": "avoèr",
                                        },
                                        {
                                            "lang": "Walloon",
                                            "lang_code": "wa",
                                            "word": "aveur",
                                        },
                                        {
                                            "lang": "Middle English",
                                            "lang_code": "enm",
                                            "word": "aver",
                                            "raw_tags": ["borrowed"],
                                            "descendants": [
                                                {
                                                    "lang": "English",
                                                    "lang_code": "en",
                                                    "word": "aver",
                                                }
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Occitano-Romance",
                    "descendants": [
                        {"lang": "Catalan", "lang_code": "ca", "word": "haver"},
                        {"lang": "Catalan", "lang_code": "ca", "word": "heure"},
                        {
                            "lang": "Old Occitan",
                            "lang_code": "pro",
                            "word": "aver",
                            "descendants": [
                                {
                                    "lang": "Occitan",
                                    "lang_code": "oc",
                                    "word": "aver",
                                    "descendants": [
                                        {
                                            "lang": "Gascon",
                                            "lang_code": "oc-gas",
                                            "word": "àuger",
                                        },
                                        {
                                            "lang": "Gascon",
                                            "lang_code": "oc-gas",
                                            "word": "er",
                                        },
                                        {
                                            "lang": "Provençal",
                                            "lang_code": "oc-pro",
                                            "word": "aguer",
                                        },
                                        {
                                            "lang": "Vivaro-Alpine",
                                            "lang_code": "oc-viv",
                                            "word": "aguer",
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "lang": "Old Occitan",
                            "lang_code": "pro",
                            "word": "haver",
                            "descendants": [
                                {
                                    "lang": "Occitan",
                                    "lang_code": "oc",
                                    "word": "aver",
                                    "descendants": [
                                        {
                                            "lang": "Gascon",
                                            "lang_code": "oc-gas",
                                            "word": "àuger",
                                        },
                                        {
                                            "lang": "Gascon",
                                            "lang_code": "oc-gas",
                                            "word": "er",
                                        },
                                        {
                                            "lang": "Provençal",
                                            "lang_code": "oc-pro",
                                            "word": "aguer",
                                        },
                                        {
                                            "lang": "Vivaro-Alpine",
                                            "lang_code": "oc-viv",
                                            "word": "aguer",
                                        },
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Ibero-Romance",
                    "descendants": [
                        {
                            "lang": "Aragonese",
                            "lang_code": "an",
                            "word": "haber",
                        },
                        {
                            "lang": "Old Leonese",
                            "lang_code": "roa-ole",
                            "word": "aver",
                            "descendants": [
                                {
                                    "lang": "Asturian",
                                    "lang_code": "ast",
                                    "word": "haber",
                                },
                                {
                                    "lang": "Extremaduran",
                                    "lang_code": "ext",
                                    "word": "avel",
                                },
                                {
                                    "lang": "Extremaduran",
                                    "lang_code": "ext",
                                    "word": "bel",
                                },
                                {
                                    "lang": "Leonese",
                                    "lang_code": "roa-leo",
                                    "word": "habere",
                                },
                                {
                                    "lang": "Mirandese",
                                    "lang_code": "mwl",
                                    "word": "haber",
                                },
                            ],
                        },
                        {
                            "lang": "Old Galician-Portuguese",
                            "lang_code": "roa-opt",
                            "word": "aver",
                            "descendants": [
                                {
                                    "lang": "Galician",
                                    "lang_code": "gl",
                                    "word": "haber",
                                },
                                {
                                    "lang": "Portuguese",
                                    "lang_code": "pt",
                                    "word": "haver",
                                },
                            ],
                        },
                        {
                            "lang": "Old Galician-Portuguese",
                            "lang_code": "roa-opt",
                            "word": "haver",
                            "raw_tags": ["latinized form"],
                            "descendants": [
                                {
                                    "lang": "Galician",
                                    "lang_code": "gl",
                                    "word": "haber",
                                },
                                {
                                    "lang": "Portuguese",
                                    "lang_code": "pt",
                                    "word": "haver",
                                },
                            ],
                        },
                        {
                            "lang": "Old Spanish",
                            "lang_code": "osp",
                            "word": "aver",
                            "descendants": [
                                {
                                    "lang": "Ladino",
                                    "lang_code": "lad",
                                    "word": "aver",
                                },
                                {
                                    "lang": "Ladino",
                                    "lang_code": "lad",
                                    "word": "אביר",
                                },
                                {
                                    "lang": "Spanish",
                                    "lang_code": "es",
                                    "word": "haber",
                                },
                            ],
                        },
                    ],
                },
                {
                    "lang_code": "unknown",
                    "lang": "Insular Romance",
                    "descendants": [
                        {
                            "lang": "Old Sardinian",
                            "lang_code": "sc-old",
                            "word": "avere",
                            "descendants": [
                                {
                                    "lang": "Campidanese",
                                    "lang_code": "sc-sro",
                                    "word": "ai",
                                },
                                {
                                    "lang": "Campidanese",
                                    "lang_code": "sc-sro",
                                    "word": "airi",
                                },
                                {
                                    "lang": "Logudorese",
                                    "lang_code": "sc-src",
                                    "word": "àere",
                                },
                            ],
                        }
                    ],
                },
            ],
        )
