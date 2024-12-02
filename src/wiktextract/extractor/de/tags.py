from .models import WordEntry

# Sense tags
# https://de.wiktionary.org/wiki/Vorlage:K
# https://de.wiktionary.org/wiki/Vorlage:K/Abk
K_TEMPLATE_TAGS = {
    "Abl.": "ablative",
    "Ablativ": "ablative",
    "abw.": "derogatory",
    "abwertend": "derogatory",
    "AE": "US",
    "AmE": "US",
    "adv.": "adverbial",
    "Akkusativ": "accusative",
    "alemann.": "Alemannic",
    "alemannisch": "Alemannic",
    "allg.": "general",
    "allgemein": "general",
    "alltagsspr.": "colloquial",
    "amtsspr.": "officialese",
    # "ansonsten": "otherwise",  # combined with other text
    "attr.": "attributive",
    # "auch": "also",
    "bair.": "Bavarian",
    "bairisch": "Bavarian",
    "bar.": "Bavarian",
    "BE": "British",
    "BrE": "British",
    "Bedva.": "outdated",
    "Bedvatd.": "outdated",
    "veraltende Bedeutung": "outdated",
    # "bei": "",
    # "bes.": "especially",
    # "besonders": "especially",
    # "beziehungsweise": "",
    # "bzw.": "",
    # "bildungsspr.": "",
    # "bis": "",
    # "bisweilen": "",
    # "das": "",
    "Dativ": "dative",
    # "DDR": "",
    "Deutschland": "Germany",
    # "der": "",
    "dichter.": "poetic",
    # "die": "",
    "Dim.": "diminutive",
    "Dimin.": "diminutive",
    "Diminutiv": "diminutive",
    # "eher": "",
    "erzg.": "Erzgebirgisch",
    "erzgeb.": "Erzgebirgisch",
    "erzgebirgisch": "Erzgebirgisch",
    "euph.": "euphemistic",
    "fachspr.": "jargon",
    "fachsprachlich": "jargon",
    "fam.": "familiär",
    "fig": "figurative",
    "fig.": "figurative",
    # "früher": "",
    # "gegenwartslateinisch": "",
    "geh.": "gehoben",
    "Genitiv": "genitive",
    "gsm": "Swiss German",
    "häufig": "often",
    "haben": "auxiliary",
    "hebben": "auxiliary",
    "hauptsächlich": "primarily",
    "hist.": "historical",
    "ieS": "narrowly",
    "i.e.S.": "narrowly",
    "i. e. S.": "narrowly",
    # "im": "",
    # "in": "",
    # "in Bezug auf": "relational",
    "indekl.": "indeclinable",
    # "insbes.": "",
    "Instrumental": "instrumental",
    "intrans.": "intransitive",
    "intransitiv": "intransitive",
    # "iPl": "in plural",
    "iron.": "ironic",
    # "iwS": "",
    # "jugendspr.": "",
    "kinderspr.": "childish",
    "kirchenlateinisch": "Church Latin",
    "klasslat.": "Classical Latin",
    "klassischlateinisch": "Classical Latin",
    "kPl.": "no-plural",
    "kein Plural": "no-plural",
    "kSg.": "no-singulative",
    "kSt.": "no-comparative",
    "landsch.": "regional",
    "lautm.": "onomatopoeic",
    "Ling.": "linguistics",
    "mA": "accusative",
    "md.": "Central German",
    "mdal.": "dialectal",
    "Med.": "medicine",  # topic
    # "meist": "mostly",
    # "meistens": "mostly",
    "metaphor.": "metaphoric",
    "meton.": "metonymically",
    "mG": "genitive",
    "mitteld.": "Central German",
    # "mitunter": "",
    "mlat.": "Medieval Latin",
    "mittellateinisch": "Medieval Latin",
    "mundartl.": "dialectal",
    "nDu.": "only-dual",
    "nigr.": "Niger",
    "nigrisch": "Niger",
    "nkLat.": "post-Classical Latin",
    "nachklassischlateinisch": "post-Classical Latin",
    "nlat.": "New Latin",
    "neulateinisch": "New Latin",
    "nordd.": "North German",
    "norddeutsch": "North German",
    "nordwestd.": "Northwestern Germany",
    "nPl.": "plural-only",
    "Österreich": "Austrian German",
    "österr.": "Austrian German",
    "österreichisch": "Austrian German",
    "ostfränkisch": "East Franconian German",
    "pej.": "pejorative",
    "poet.": "poetic",
    "PräpmG": "genitive prepositional",
    "PmG": "genitive prepositional",
    "reg.": "regional",
    "refl.": "reflexive",
    "reflexiv": "reflexive",
    # "respektive": "",
    "sal.": "casual",
    "salopp": "casual",
    "scherzh.": "jocular",
    "schriftspr.": "literary",
    # "schülerspr.": "",
    "schwäb.": "Swabian",
    "schwäbisch": "Swabian",
    "Schweiz": "Swiss Standard German",
    "schweiz.": "Swiss Standard German",
    "schweizerisch": "Swiss Standard German",
    "Schweizerdeutsch": "Swiss German",
    "schweizerdeutsch": "Swiss German",
    # "seemannsspr.": "",
    "sein": "auxiliary verb",
    # "sehr": "",  # very
    "selten": "rare",
    "seltener": "rare",
    "seltener auch": "rare",
    "soldatenspr.": ["military", "slang"],
    # "sonderspr.": "",
    # "sonst": "",
    # "sowie": "",
    "spätlat.": "Late Latin",
    "spätlateinisch": "Late Latin",
    # "später": "",
    "speziell": "special",
    "südd.": "South German",
    "süddt.": "South German",
    # "techn.": "",
    # "teils": "",
    # "teilweise": "",
    "tlwva.": "outdated",
    "tlwvatd.": "outdated",
    "trans.": "transitive",
    "transitiv": "transitive",
    # "über": "",
    # "überwiegend": "mostly",
    "übertr.": "figurative",
    "übertragen": "figurative",
    "ugs.": "colloquial",
    "umgangssprachlich": "colloquial",
    # "und": "",
    "ungebr.": "uncommon",
    "unpers.": "impersonal",
    "unpersönlich": "impersonal",
    # "ursprünglich": "",
    "va.": "outdated",
    "vatd.": "outdated",
    "veraltend": "outdated",
    # "verh.": "",
    "volkst.": "popular",
    # "von": "",
    # "vor allem": "",
    # "vor allem in": "",
    "vul.": "vulgar",
    "vulg.": "vulgar",
    "vlat.": ["vulgar", "Latin"],
    "vulgärlat": ["vulgar", "Latin"],
    "vulgärlateinisch": ["vulgar", "Latin"],
    "wien.": "Vienna",
    "wienerisch": "Vienna",
    # "Wpräp": "",
    # "z. B.": "",
    # "z. T.": "",
    # "zijn": "",
    # "zum Beispiel": "",
    # "zum Teil": "",
    # "zumeist": "",
    "Kardinalzahl": "cardinal",
    "Sammelbegriff": "collective",
    "Fachsprache": "jargon",
    "formale Sprachen": "formal",
    "Programmiersprachen": "programming",
    "Rechnerarchitektur": "programming",
    "Geografie": "geography",
    "Geometrie": "geometry",
    "Finanzwesen": "finance",
    "juristisch": "law",
    "Physik": "physics",
}

GENDER_TAGS = {
    "n": "neuter",
    "m": "masculine",
    "f": "feminine",
    # Vorlage:Deklinationsseite Adjektiv
    "Maskulinum": "masculine",
    "Femininum": "feminine",
    "Neutrum": "neuter",
}

NUMBER_TAGS = {
    # Vorlage:Deutsch Substantiv Übersicht
    "Singular": "singular",
    "Plural": "plural",
}

CASE_TAGS = {
    # Vorlage:Deutsch Substantiv Übersicht
    "Nominativ": "nominative",
    "Genitiv": "genitive",
    "Dativ": "dative",
    "Akkusativ": "accusative",
}

COMPARISON_TAGS = {
    # Vorlage:Deutsch Adjektiv Übersicht
    # Vorlage:Deklinationsseite Adjektiv
    "Positiv": "positive",
    "Komparativ": "comparative",
    "Superlativ": "superlative",
}

DECLENSION_TAGS = {
    # https://en.wikipedia.org/wiki/German_declension
    # Vorlage:Deklinationsseite Adjektiv
    "Starke Deklination": "strong",
    "Schwache Deklination": "weak",
    "Gemischte Deklination": "mixed",
}

OTHER_TAGS = {
    # Vorlage:Deklinationsseite Adjektiv
    "Prädikativ": "predicative",
    "erweiterte": "extended",
    "Höflichkeitsform": "honorific",
    # Vorlage:Deutsch Verb schwach untrennbar reflexiv
    "nichterweitert": "not-extended",
    "erweitert": "extended",
}

TENSE_TAGS = {
    # Vorlage:Deutsch Verb Übersicht
    "Präsens": "present",
    "Präteritum": "past",
    "Perfekt": "perfect",
    "Futur I": "future-i",
    "Futur II": "future-ii",
    "Plusquamperfekt": "pluperfect",
}

MOOD_TAGS = {
    # Vorlage:Deutsch Verb Übersicht
    # Vorlage:Deutsch Verb regelmäßig
    "Konjunktiv I": "subjunctive-i",
    "Konjunktiv II": "subjunctive-ii",
    "Imperativ": "imperative",
    "Imperative": "imperative",
    "Indikativ": "indicative",
}

VERB_FORM_TAGS = {
    # Vorlage:Deutsch Verb Übersicht
    "Partizip II": "participle-2",
    "Hilfsverb": "auxiliary",
    "Infinitive": "infinitive",
    "Infinitiv": "infinitive",
    "Partizipien": "participle",
}

VOICE_TAGS = {
    # Vorlage:Deutsch Verb unregelmäßig
    "Aktiv": "active",
    "Vorgangspassiv": "processual passive",
    "Zustandspassiv": "statal passive",
    "Passiv": "passive",
    "Gerundivum": "gerundive",
    # Vorlage:Deutsch Verb schwach untrennbar reflexiv
    "Zustandsreflexiv": "statal reflexive",
}

PERSON_TAGS = {
    # Vorlage:Deutsch Verb unregelmäßig
    "1. Person Singular": ["first-person", "singular"],
    "1. Person Plural": ["first-person", "plural"],
    "2. Person Singular": ["second-person", "singular"],
    "2. Person Plural": ["second-person", "plural"],
    "3. Person Singular": ["third-person", "singular"],
    "3. Person Plural": ["third-person", "plural"],
    # Vorlage:Deutsch Verb schwach untrennbar reflexiv
    "Sg. 1. Pers.": ["first-person", "singular"],
    "Pl. 1. Pers.": ["first-person", "plural"],
    "Sg. 2. Pers.": ["second-person", "singular"],
    "Pl. 2. Pers.": ["second-person", "plural"],
    "Sg. 3. Pers.": ["third-person", "singular"],
    "Pl. 3. Pers.": ["third-person", "plural"],
}

INFLECTION_TABLE_TAGS = {
    # Vorlage:Deutsch Verb regelmäßig
    "ungebräuchlich": "uncommon",
    "veraltet": "archaic",
    # Vorlage:Deutsch Verb schwach trennbar reflexiv
    "Nebensatzkonjugation": "subordinate-clause",
    "Hauptsatzkonjugation": "main-clause",
}

GRAMMATICAL_TAGS = {
    **K_TEMPLATE_TAGS,
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **CASE_TAGS,
    **COMPARISON_TAGS,
    **DECLENSION_TAGS,
    **OTHER_TAGS,
    **TENSE_TAGS,
    **MOOD_TAGS,
    **VERB_FORM_TAGS,
    **VOICE_TAGS,
    **PERSON_TAGS,
    **INFLECTION_TABLE_TAGS,
}

K_TEMPLATE_TOPICS = {
    "Biologie": "biology",
    "Linguistik": "linguistics",
    "Wortbildung": "morphology",
    "Behörde": "government",
    "Astronomie": "astronomy",
    "Immobilienbranche": "real-estate",
    "Kunst": "arts",
    "Informatik": "computing",
    "Nautik": "nautical",
    "Sport": "sports",
    "Schuhwerk": "footwear",
    "Textilien": "textiles",
    "Zahlungsmittel": "payment-method",
    "Ökologie": "ecology",
    "Internet": "Internet",
    "Religion": "religion",
    "Militärsprache": "military",
    "Systematik": "systematics",
    "Zoologie": "zoology",
    "Seefahrt": "seafaring",
    "Soldatensprache": {"topic": "military", "tag": "slang"},
    "Botanik": "botany",
    "Marine": "navy",
    "Informationstechnologie": "computing",
    "Betriebswirtschaftslehre": "business",
    "Recht": "law",
    "Elektronik": "electronics",
    "Emotion": "emotion",
    "Mathematik": "mathematics",
    "Bürgerliches Recht": "civil-Law",
    "Militär": "military",
    "Politik": "politics",
    "Werkzeug": "tools",
    "Medizin": "medicine",
    "Ornithologie": "ornithology",
    "Technik": "technology",
    "Waffentechnik": "weaponry",
    "Anatomie": "anatomy",
    "Fußball": "football",
    "Kartenspiel": "card-games",
    "Theoretische Informatik": "computing",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in GRAMMATICAL_TAGS:
            tag = GRAMMATICAL_TAGS[raw_tag]
            if isinstance(tag, str):
                data.tags.append(tag)
            elif isinstance(tag, list):
                data.tags.extend(tag)
        elif raw_tag in K_TEMPLATE_TOPICS and hasattr(data, "topics"):
            topic = K_TEMPLATE_TOPICS[raw_tag]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, dict):
                data.topics.append(topic.get("topic"))
                data.tags.append(topic.get("tag"))
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
