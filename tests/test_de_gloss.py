import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.gloss import (
    extract_glosses,
    process_K_template,
    extract_tags_from_gloss_text,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestGlossList(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(dump_file_lang_code="de"),
        )

    def set_up_K_template(self) -> None:
        self.wxr.wtp.add_page(
            "Vorlage:K",
            10,
            """
<i>{{
#if: {{{1|}}} | {{#ifeq: {{K/Abk|||{{{1|}}}}} | nvT | {{K/Abk|{{{1|}}}}} | {{#ifeq: {{K/Abk|{{{1|}}} }} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{1|}}}}} | [[{{K/Abk|{{{1|}}}}}]] | {{K/Abk|{{{1|}}}}} }} }} }} }}{{
#if: {{{2|}}} | {{#if: {{{t1|}}} | {{#switch: {{{t1|}}} | :=&#58; | ;=&#59; | _= | #default={{{t1|}}} }} | {{#ifeq: {{K/Abk|||{{{1|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{2|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{2|}}}}} | nvT | {{K/Abk|{{{2|}}}}} | {{#ifeq: {{K/Abk|{{{2|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{2|}}}}} | [[{{K/Abk|{{{2|}}}}}]] | {{K/Abk|{{{2|}}}}} }} }} }} }}{{
#if: {{{3|}}} | {{#if: {{{t2|}}} | {{#switch: {{{t2|}}} | :=&#58; | ;=&#59; | _= | #default={{{t2|}}} }} | {{#ifeq: {{K/Abk|||{{{2|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{3|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{3|}}}}} | nvT | {{K/Abk|{{{3|}}}}} | {{#ifeq: {{K/Abk|{{{3|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{3|}}}}} | [[{{K/Abk|{{{3|}}}}}]] | {{K/Abk|{{{3|}}}}} }} }} }} }}{{
#if: {{{4|}}} | {{#if: {{{t3|}}} | {{#switch: {{{t3|}}} | :=&#58; | ;=&#59; | _= | #default={{{t3|}}} }} | {{#ifeq: {{K/Abk|||{{{3|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{4|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{4|}}}}} | nvT | {{K/Abk|{{{4|}}}}} | {{#ifeq: {{K/Abk|{{{4|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{4|}}}}} | [[{{K/Abk|{{{4|}}}}}]] | {{K/Abk|{{{4|}}}}} }} }} }} }}{{
#if: {{{5|}}} | {{#if: {{{t4|}}} | {{#switch: {{{t4|}}} | :=&#58; | ;=&#59; | _= | #default={{{t4|}}} }} | {{#ifeq: {{K/Abk|||{{{4|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{5|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{5|}}}}} | nvT | {{K/Abk|{{{5|}}}}} | {{#ifeq: {{K/Abk|{{{5|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{5|}}}}} | [[{{K/Abk|{{{5|}}}}}]] | {{K/Abk|{{{5|}}}}} }} }} }} }}{{
#if: {{{6|}}} | {{#if: {{{t5|}}} | {{#switch: {{{t5|}}} | :=&#58; | ;=&#59; | _= | #default={{{t5|}}} }} | {{#ifeq: {{K/Abk|||{{{5|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{6|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{6|}}}}} | nvT | {{K/Abk|{{{6|}}}}} | {{#ifeq: {{K/Abk|{{{6|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{6|}}}}} | [[{{K/Abk|{{{6|}}}}}]] | {{K/Abk|{{{6|}}}}} }} }} }} }}{{
#if: {{{7|}}} | {{#if: {{{t6|}}} | {{#switch: {{{t6|}}} | :=&#58; | ;=&#59; | _= | #default={{{t6|}}} }} | {{#ifeq: {{K/Abk|||{{{6|}}}}} | nvT | | {{#invoke:Kontext|Konjunktion|{{{7|}}}}} }} }}&#32;{{#ifeq: {{K/Abk|||{{{7|}}}}} | nvT | {{K/Abk|{{{7|}}}}} | {{#ifeq: {{K/Abk|{{{7|}}}}} | {{PAGENAME}} | {{PAGENAME}} | {{#ifexist: {{K/Abk|{{{7|}}}}} | [[{{K/Abk|{{{7|}}}}}]] | {{K/Abk|{{{7|}}}}} }} }} }} }}{{
#if: {{{ft|}}} | {{#if: {{{1|}}} | {{#if: {{{t7|}}} | {{#switch: {{{t7|}}} | :=&#58; | ;=&#59; | _= | #default={{{t7|}}} }} | , }}&#32;}}{{{ft}}} }}&#58;</i>{{#if: {{NAMESPACE}} | |
{{#if: {{{1|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{1|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{1|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{2|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{2|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{2|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{3|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{3|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{3|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{4|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{4|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{4|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{5|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{5|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{5|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{6|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{6|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{6|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{7|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{7|}}}}}&#32;({{{{{spr|}}}|nolink=ja}}) | [[Kategorie:{{K/Abk||{{{7|}}}}}&#32;({{{{{spr|}}}|nolink=ja}})]]| }} }}
{{#if: {{{spr|}}} |
{{#if: {{{1|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{1|}}}}}}} | [[Kategorie:{{K/Abk|2={{{1|}}} }}]] }} }}
{{#if: {{{2|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{2|}}}}}}} | [[Kategorie:{{K/Abk|2={{{2|}}} }}]] }} }}
{{#if: {{{3|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{3|}}}}}}} | [[Kategorie:{{K/Abk|2={{{3|}}} }}]] }} }}
{{#if: {{{4|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{4|}}}}}}} | [[Kategorie:{{K/Abk|2={{{4|}}} }}]] }} }}
{{#if: {{{5|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{5|}}}}}}} | [[Kategorie:{{K/Abk|2={{{5|}}} }}]] }} }}
{{#if: {{{6|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{6|}}}}}}} | [[Kategorie:{{K/Abk|2={{{6|}}} }}]] }} }}
{{#if: {{{7|}}} | {{#if: {{K/Abk|4={{K/Abk|2={{{7|}}}}}}} | [[Kategorie:{{K/Abk|2={{{7|}}} }}]] }} }}
|
{{#if: {{{1|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{1|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{1|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{1|}}}}} | [[Kategorie:{{K/Abk||{{{1|}}}}}]]}}}} }}
{{#if: {{{2|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{2|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{2|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{2|}}}}} | [[Kategorie:{{K/Abk||{{{2|}}}}}]]}}}} }}
{{#if: {{{3|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{3|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{3|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{3|}}}}} | [[Kategorie:{{K/Abk||{{{3|}}}}}]]}}}} }}
{{#if: {{{4|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{4|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{4|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{4|}}}}} | [[Kategorie:{{K/Abk||{{{4|}}}}}]]}}}} }}
{{#if: {{{5|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{5|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{5|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{5|}}}}} | [[Kategorie:{{K/Abk||{{{5|}}}}}]]}}}} }}
{{#if: {{{6|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{6|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{6|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{6|}}}}} | [[Kategorie:{{K/Abk||{{{6|}}}}}]]}}}} }}
{{#if: {{{7|}}} | {{#ifexist: {{ns:14}}:{{K/Abk||{{{7|}}}}}&#32;(Deutsch) | [[Kategorie:{{K/Abk||{{{7|}}}}}&#32;(Deutsch)]] | {{#ifexist: {{ns:14}}:{{K/Abk||{{{7|}}}}} | [[Kategorie:{{K/Abk||{{{7|}}}}}]]}}}}}} }}
}}{{#ifeq: {{NAMESPACENUMBER}} | 0 | {{#if: {{{Prä|}}}{{{Kas|}}} | [[Kategorie:Verb mit Präposition {{{Prä|}}} + {{#switch: {{{Kas|}}} | Akk.=Akkusativ | Dat.|Dativ=Dativ | Gen.=Genitiv | #default={{{Kas|}}} }} ({{{{{spr|de}}}|nolink=ja}})]]}}}}""",
        )

        self.wxr.wtp.add_page(
            "Vorlage:K/Abk",
            10,
            """
{{#if: {{{1|}}}|{{#switch: {{{1|}}}
|Abl. | Ablativ = mit [[Ablativ]]
|AE | AmE = [[W:US-amerikanisches Englisch|US-amerikanisch]]
|Akkusativ | mA = mit [[Akkusativ]]
|abw. = abwertend
|adv. = adverbial
|alemann. = alemannisch
|allg. = allgemein
|alltagsspr. = [[Alltagssprache|alltagssprachlich]]
|amtsspr. = [[Amtssprache|amtssprachlich]]
|attr. = attributiv
|bar. | bair. = bairisch
|BE | BrE = [[W:Britisches Englisch|britisch]]
|bes.= besonders
|bzw. = beziehungsweise
|bildungsspr. = bildungssprachlich
|Dativ | mD = mit [[Dativ]]
|DDR = [[W:Sprachgebrauch in der DDR|DDR]]
|dichter. = dichterisch
|Dim. | Dimin. = Diminutiv
|erzg. | erzgeb. = erzgebirgisch
|euph. = euphemistisch
|fachspr. = fachsprachlich
|fam. = familiär
|fig = figürlich
|fig. = figurativ
|ostfränkisch = [[W:Ostfränkische Dialekte|ostfränkisch]]
|geh. = gehoben
|Genitiv | mG = mit [[Genitiv]]
|gsm = [[W:Schweizerdeutsch|schweizerdeutsch]]
|haben = [[Hilfsverb]] [[haben]]
|hebben = [[Hilfsverb]] »[[hebben]]«
|hist. = historisch
|indekl. = indeklinabel
|Instrumental = mit [[Instrumental]]
|intrans. = [[intransitiv]]
|iron. = ironisch
|jugendspr. = jugendsprachlich
|kinderspr. = [[Kindersprache|kindersprachlich]]
|klasslat. = klassischlateinisch 
|kPl. = kein [[Plural]]
|kSg. = kein [[Singular]]
|kSt. | kStg. = keine Steigerung
|landsch. = landschaftlich
|lautm. = lautmalerisch
|Ling. = Linguistik
|md. | mitteld. = mitteldeutsch
|mdal. | mundartl. = mundartlich
|Med. = Medizin
|metaphor. = metaphorisch
|meton. = metonymisch
|nDu. = nur [[Dual]]
|mlat. = mittellateinisch
|nigr. = nigrisch
|nkLat. | nachklassischlateinisch = Nachklassisches Latein
|nlat. = neulateinisch
|nordd. = norddeutsch
|nordwestd. = nordwestdeutsch
|nPl. = nur [[Plural]]
|Österr. | Österreich = [[W:Österreichisches Deutsch|Österreich]]
|österr. | österreichisch = [[W:Österreichisches Deutsch|österreichisch]]
|pej. = pejorativ
|poet. = poetisch
|Plural | iPl = im Plural
|PmG | PräpmG = Präposition mit Genitiv
|PmD | PräpmD = Präposition mit Dativ
|reg. = regional
|refl. = reflexiv
|sal. = salopp
|scherzh. = scherzhaft
|schriftspr. = schriftsprachlich
|schülerspr. = [[Schülersprache|schülersprachlich]]
|schwäb. = schwäbisch
|Schweiz = [[W:Schweizer Hochdeutsch|Schweiz]]
|schweiz. | schweizerisch = [[W:Schweizer Hochdeutsch|schweizerisch]]
|Schweizerdeutsch = [[W:Schweizerdeutsch|Schweizerdeutsch]]
|schweizerdeutsch = [[W:Schweizerdeutsch|schweizerdeutsch]]
|seemannsspr. = [[Seemannssprache|seemannssprachlich]]
|sein = [[Hilfsverb]] [[sein]]
|soldatenspr. = [[Soldatensprache|soldatensprachlich]]
|sonderspr. = [[Sondersprache|sondersprachlich]]
|spätlat. = spätlateinisch
|südd. | süddt. = süddeutsch
|techn. = technisch
|tlwva. | Bedva. | veraltete Bedeutung= [[veraltet]]e [[Bedeutung]]
|tlwvatd. | Bedvatd. | veraltende Bedeutung= [[veraltend]]e [[Bedeutung]]
|trans. = [[transitiv]]
|übertr. = [[im übertragenen Sinn|übertragen]]
|ugs. = umgangssprachlich
|unpers. = unpersönlich
|ungebr. = ungebräuchlich
|va. = veraltet
|vatd. = veraltend
|verh. = verhüllend
|volkst. = volkstümlich 
|vul. |vulg. = vulgär
|vulgärlat. | vlat. = vulgärlateinisch
|wien. = wienerisch
|z. B. =  zum Beispiel
|z. T. = zum Teil
|#default= {{{1}}} }} }}{{#if: {{{2|}}}|{{#switch: {{{2|}}}
|Akkusativ |mA = Akkusativobjekt
|alemann. | alemannisch = Alemannisch
|bar. |bair. | bairisch = Bairisch
|bildungsspr. = Bildungssprache
|Dativ |mD = Verb mit Dativobjekt
|DDR = DDR-Sprachgebrauch
|Dim. | Dimin. = Diminutiv
|erzg. | erzgeb. | erzgebirgisch = Erzgebirgisch
|fam. = familiär
|fig = figürlich
|fig. = figurativ
|gegenwartslateinisch = Gegenwartslatein
|geh. = gehobener Wortschatz
|Genitiv |mG = Verb mit Genitivobjekt
|gsm | schweizerdeutsch = Schweizerdeutsch
|indekl. = Adjektiv indeklinabel
|Instrumental = Verb mit Instrumentalobjekt
|intrans. | intransitiv = Verb intransitiv
|iterativ = Verb iterativ
|kirchenlateinisch = Kirchenlatein
|klasslat.| klassischlateinisch  = Klassisches Latein
|Ling. = Linguistik
|mlat. | mittellateinisch = Mittellatein
|nkLat. | nachklassischlateinisch  = Nachklassisches Latein
|nigr. | nigrisch = Nigrisches Hausa
|nlat. | neulateinisch = Neulatein
|nordd. | norddeutsch = Norddeutsch
|österr. | österreichisch | Österreich = Österreichisches Deutsch
|ostfränkisch = Ostfränkisch
|Partizip = 
|pej. = pejorativ
|Plural | iPl = im Plural
|PmG | PräpmG = Präposition mit Genitiv
|PmD | PräpmD = Präposition mit Dativ
|refl. | reflexiv = Verb reflexiv
|schriftspr. = Schriftsprache
|schwäb. | schwäbisch = Schwäbisch
|schweiz. | schweizerisch | Schweiz = Schweizer Hochdeutsch
|spätlat. | spätlateinisch = Spätlatein
|Sprachen = 
|südd. = Süddeutsch
|tlwva. | Bedva. | veraltete Bedeutung = veraltete Bedeutungen
|tlwvatd. | Bedvatd. | veraltende Bedeutung = veraltende Bedeutungen
|trans. | transitiv = Verb transitiv
|übertr. = übertragen
|ugs. = Umgangssprache
|unpers. = Verb unpersönlich
|unpersönlich = Verb unpersönlich
|va. | veraltet = veralteter Wortschatz
|vatd. | veraltend = veraltender Wortschatz
|vul. | vulg. = Vulgärsprache
|vulgärlat. | vlat. | vulgärlateinisch = Vulgärlatein
|wien. | wienerisch = Wienerisch
|#default= {{{2}}} }} }}{{#if: {{{3|}}}|{{#switch: {{{3|}}}
|allg. | allgemein
|ansonsten
|auch
|bei
|bes. | besonders
|beziehungsweise | bzw.
|bis
|bisweilen
|das
|der
|die
|eher
|früher
|häufig
|hauptsächlich
|im
|in
|insbes. | insbesondere
|leicht
|meist
|meistens
|mit
|mitunter
|noch
|noch in
|nur
|nur noch
|oder
|oft
|oftmals
|ohne
|respektive
|sehr
|seltener
|seltener auch
|sonst
|sowie
|später
|speziell
|teils
|teilweise
|über
|überwiegend
|ursprünglich
|und
|von
|vor allem
|vor allem in
|z. B. | zum Beispiel
|z. T. | zum Teil
|zumeist=nvT 
|#default= {{{3}}} }} }}{{#if: {{{4|}}}|{{#switch: {{{4|}}}
|Gegenwartslatein
|Kirchenlatein
|Klassisches Latein
|Mittellatein
|Nachklassisches Latein
|Neulatein
|Nigrisches Hausa
|Spätlatein
|Vulgärlatein={{{4}}}
|#default= }} }}""",
        )

        self.wxr.wtp.add_page(
            "Modul:Kontext",
            828,
            """
-- Unterroutinen für die Vorlage K
local Kontext = {}

-- Feststellung, ob eine Konjunktion vorliegt
	function Kontext.Konjunktion(frame)
		local parnext = frame.args[1]
		local retp = "" -- returnstring
		if (parnext) then
			if (parnext ~= "beziehungsweise") and
			   (parnext ~= "oder") and
			   (parnext ~= "respektive") and
			   (parnext ~= "sowie") and
			   (parnext ~= "und")
			then
				retp = ","
			end
		end
		return retp
	end
return Kontext""",
        )

        self.wxr.wtp.add_page("Vorlage:!", 10, "|")
        self.wxr.wtp.add_page(
            "Vorlage:de",
            10,
            "{{safesubst:#if:{{{nolink|}}}|Deutsch|'''[[Deutsch]]'''}}",
        )
        self.wxr.wtp.add_page(
            "Vorlage:cs",
            10,
            "{{safesubst:#if:{{{nolink|}}}|Tschechisch|[[Tschechisch]]}}",
        )

        category_pages = [
            "Kategorie:\nVerb transitiv",
            "Kategorie:\nVerb reflexiv",
            "Kategorie:\nVerb intransitiv",
            "Kategorie:\nUmgangssprache",
            "Kategorie:\nveraltender Wortschatz",
            "Kategorie:\nveralteter Wortschatz",
            "Kategorie:\nÖsterreichisches Deutsch",
        ]

        for page_title in category_pages:
            self.wxr.wtp.add_page(
                page_title,
                14,
                "",
            )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_de_extract_glosses(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(":[1] gloss1 \n:[2] gloss2")

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "raw_glosses": ["[1] gloss1"],
                            "senseid": "1",
                        },
                        {
                            "glosses": ["gloss2"],
                            "raw_glosses": ["[2] gloss2"],
                            "senseid": "2",
                        },
                    ]
                }
            ],
        )

    def test_de_extract_glosses_with_subglosses(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            ":[1] gloss1\n::[a] subglossA\n::[b] subglossB"
        )

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "raw_glosses": ["[1] gloss1"],
                            "senseid": "1",
                        },
                        {
                            "glosses": ["subglossA"],
                            "raw_glosses": ["[a] subglossA"],
                            "senseid": "1a",
                        },
                        {
                            "glosses": ["subglossB"],
                            "raw_glosses": ["[b] subglossB"],
                            "senseid": "1b",
                        },
                    ]
                }
            ],
        )

    def test_de_extract_glosses_with_only_subglosses(self):
        self.set_up_K_template()
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            ":[1] {{K|tag}}\n::[a] subglossA\n::[1b] subglossB"
        )

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)
        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "tags": ["tag"],
                            "glosses": ["subglossA"],
                            "raw_glosses": ["[a] subglossA"],
                            "senseid": "1a",
                        },
                        {
                            "tags": ["tag"],
                            "glosses": ["subglossB"],
                            "raw_glosses": ["[1b] subglossB"],
                            "senseid": "1b",
                        },
                    ]
                }
            ],
        )

    def test_process_K_template_removes_K_template_nodes(self):
        self.set_up_K_template()

        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("{{K|tag1|tag2}} gloss1")

        gloss_data = defaultdict(list)

        self.assertEqual(len(root.children), 2)

        process_K_template(self.wxr, gloss_data, root)

        self.assertEqual(
            gloss_data,
            {
                "tags": ["tag1", "tag2"],
            },
        )

        self.assertEqual(len(root.children), 1)

    def test_process_K_template(self):
        self.set_up_K_template()

        # Test cases chosen from:
        # https://de.wiktionary.org/wiki/Vorlage:K/Doku
        test_cases = [
            # https://de.wiktionary.org/wiki/delektieren
            {
                "input": "{{K|refl.}}",
                "expected": {
                    "tags": ["reflexiv"],
                    "categories": ["Verb reflexiv"],
                },
            },
            # https://de.wiktionary.org/wiki/delektieren
            {
                "input": "{{K|trans.}}",
                "expected": {
                    "tags": ["transitiv"],
                    "categories": ["Verb transitiv"],
                },
            },
            # https://de.wiktionary.org/wiki/abbreviare
            {
                "input": "{{K|trans.|ft=etwas in seinem [[räumlich]]en oder [[zeitlich]]en [[Ausmaß]] verringern|spr=it}}",
                "expected": {
                    "tags": [
                        "transitiv",
                        "etwas in seinem räumlichen oder zeitlichen Ausmaß verringern",
                    ],
                    # Not for all languages (e.g., spr=it) the category link is created
                    # "categories": ["Verb transitiv"],
                },
            },
            # https://de.wiktionary.org/wiki/abbreviare
            {
                "input": "{{K|trans.|Linguistik|Wortbildung|spr=it}}",
                "expected": {
                    "tags": [
                        "transitiv",
                        "Linguistik",
                        "Wortbildung",
                    ],
                    # Not for all languages (e.g., spr=it) the category link is created
                    # "categories": ["Verb transitiv"],
                },
            },
            # https://de.wiktionary.org/wiki/Bakterie
            {"input": "{{K|Biologie}}", "expected": {"tags": ["Biologie"]}},
            # https://de.wiktionary.org/wiki/Kraut
            {
                "input": "{{K|kPl.|ugs.}}",
                "expected": {
                    "tags": ["kein Plural", "umgangssprachlich"],
                    "categories": ["Umgangssprache"],
                },
            },
            # https://de.wiktionary.org/wiki/almen
            # Ideally we would filter out "besonders" but there doesn't seem
            # to be a general rule which tags are semmantially relevant
            {
                "input": "{{K|trans.|t1=;|besonders|t2=_|bayrisch|österr.}}",
                "expected": {
                    "tags": [
                        "transitiv",
                        "besonders bayrisch",
                        "österreichisch",
                    ],
                    "categories": [
                        "Verb transitiv",
                        "Österreichisches Deutsch",
                    ],
                },
            },
            # https://de.wiktionary.org/wiki/Agentur
            {
                "input": "{{K|Behörde|ft=seit etwa 2000 in Deutschland}}",
                "expected": {
                    "tags": ["Behörde", "seit etwa 2000 in Deutschland"]
                },
            },
            # https://de.wiktionary.org/wiki/Objekt
            {
                "input": "{{K|Astronomie|ft=kurz für}}",
                "expected": {
                    "tags": ["Astronomie", "kurz für"],
                },
            },
            # https://de.wiktionary.org/wiki/einlaufen
            {
                "input": "{{K|intrans.|Nautik|t7=_|ft=(von Schiffen)}}",
                "expected": {
                    "tags": ["intransitiv", "Nautik (von Schiffen)"],
                    "categories": ["Verb intransitiv"],
                },
            },
            # https://de.wiktionary.org/wiki/Pfund
            {
                "input": "{{K|veraltet|veraltend|t1=;|t7=_|ft=(in Deutschland)}}",
                "expected": {
                    "tags": ["veraltet", "veraltend (in Deutschland)"],
                    "categories": [
                        "veralteter Wortschatz",
                        "veraltender Wortschatz",
                    ],
                },
            },
            # https://de.wiktionary.org/wiki/umkippen
            {"input": "{{K|sein}}", "expected": {"tags": ["Hilfsverb sein"]}},
            # https://de.wiktionary.org/wiki/umkippen
            {
                "input": "{{K|sein|salopp}}",
                "expected": {
                    "tags": ["Hilfsverb sein", "salopp"],
                },
            },
            # https://de.wiktionary.org/wiki/Hasskommentar
            {
                "input": "{{K|Internet|ft=[[soziales Netzwerk{{!}}soziale Netzwerke]]}}",
                "expected": {
                    "tags": ["Internet", "soziale Netzwerke"],
                },
            },
            # https://de.wiktionary.org/wiki/abominabilis
            {
                "input": "{{K|spätlateinisch|spr=la}}",
                "expected": {
                    "tags": ["spätlateinisch"],
                    "categories": ["Spätlatein"],
                },
            },
            # https://de.wiktionary.org/wiki/zählen
            {
                "input": "{{K|intrans.|Prä=auf|Kas=Akk.|ft=(auf jemanden/etwas zählen)}}",
                "expected": {
                    "tags": [
                        "intransitiv",
                        "(auf jemanden/etwas zählen)",
                        "auf + Akk.",
                    ],
                    "categories": [
                        "Verb intransitiv",
                        "Verb mit Präposition auf + Akkusativ (Deutsch)",
                    ],
                },
            },
            # https://de.wiktionary.org/wiki/bojovat
            {
                "input": "{{K|intrans.|Prä=proti|Kas=Dativ||ft=bojovat [[proti]] + [[Dativ]]|spr=cs}}",
                "expected": {
                    "tags": [
                        "intransitiv",
                        "bojovat proti + Dativ",
                        "proti + Dativ",
                    ],
                    "categories": [
                        # Not for all languages (e.g., spr=cs) the category link is created
                        # "Verb intransitiv",
                        "Verb mit Präposition proti + Dativ (Tschechisch)",
                    ],
                },
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                gloss_data = defaultdict(list)

                self.wxr.wtp.start_page("")

                root = self.wxr.wtp.parse(case["input"])

                process_K_template(self.wxr, gloss_data, root)
                self.assertEqual(
                    gloss_data,
                    case["expected"],
                )

    def test_de_extract_tags_from_gloss_text(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Hengst
            {
                "input": "Zoologie: männliches Tier aus der Familie der Einhufer und Kamele",
                "expected_tags": ["Zoologie"],
                "expected_gloss": "männliches Tier aus der Familie der Einhufer und Kamele",
            },
            # https://de.wiktionary.org/wiki/ARD
            {
                "input": "umgangssprachlich, Kurzwort, Akronym: für das erste Fernsehprogramm der ARD",
                "expected_tags": ["umgangssprachlich", "Kurzwort", "Akronym"],
                "expected_gloss": "für das erste Fernsehprogramm der ARD",
            },
            # https://de.wiktionary.org/wiki/Endspiel
            {
                "input": "Drama von Samuel Beckett: Menschliche Existenz in der Endphase des Verfalls und der vergeblichen Suche nach einem Ausweg",
                "expected_tags": None,
                "expected_gloss": "Drama von Samuel Beckett: Menschliche Existenz in der Endphase des Verfalls und der vergeblichen Suche nach einem Ausweg",
            }
            # Add more test cases as needed
        ]
        for case in test_cases:
            with self.subTest(case=case):
                gloss_data = defaultdict(list)

                gloss_text = extract_tags_from_gloss_text(
                    gloss_data, case["input"]
                )

                if case["expected_tags"] is None:
                    self.assertEqual(gloss_data, {})
                else:
                    self.assertEqual(
                        gloss_data,
                        {
                            "tags": case["expected_tags"],
                        },
                    )
                self.assertEqual(gloss_text, case["expected_gloss"])
