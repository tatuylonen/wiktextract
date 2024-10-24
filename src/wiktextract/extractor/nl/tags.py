from .models import WordEntry

# https://nl.wiktionary.org/wiki/Categorie:Werkwoordsjablonen
VERB_TAGS = {
    "ergatief": "ergative",  # Sjabloon:erga
    "inergatief": "unergative",  # Sjabloon:inerg
    "hulpwerkwoord": "auxiliary",  # Sjabloon:auxl
}

# https://nl.wiktionary.org/wiki/Categorie:WikiWoordenboek:Contextlabels
GLOSS_TAGS = {
    "figuurlijk": "figuratively",
    "verouderd": "obsolete",  # Sjabloon:verouderd
    "scheldwoord": "pejorative",
    "afkorting": "abbreviation",
    "causatief": "causative",
    # "chattaal": "",
    "dichterlijk": "poetic",
    "eufemisme": "euphemistic",
    "familienaam": "surname",
    "formeel": "formal",
    "gezegde": "proverb",
    # "heteroniem": "heteronym",
    "historisch": "historical",
    "informeel": "informal",
    "initiaalwoord": "acronym",
    # "klemtoonhomogram": "",
    "krachtterm": "vulgar",
    # "leesteken": "punctuation",
    "letterwoord": "acronym",
    "middeleeuwen": "Middle-Ages",
}

TABLE_TAGS = {
    # Sjabloon:-nlnoun-
    "enkelvoud": "singular",
    "meervoud": "plural",
    "verkleinwoord": "diminutive",
    # Sjabloon:adjcomp
    "stellend": "positive",
    "vergrotend": "comparative",
    "overtreffend": "superlative",
    "onverbogen": "uninflected",
    "verbogen": "inflected",
    "partitief": "partitive",
    # Sjabloon:-nlverb-
    "onbepaalde wijs": "infinitive",
    "kort": "short-form",
    "onvoltooid": "imperfect",
    "tegenwoordig": "present",
    "toekomend": "future",
    "voltooid": "perfect",
    "onvoltooid deelwoord": ["imperfect", "participle"],
    "voltooid deelwoord": ["past", "participle"],
    "gebiedende wijs": "imperative",
    "aanvoegende wijs": "subjunctive",
    "aantonende wijs": "indicative",
    "eerste": "first-person",
    "tweede": "second-person",
    "derde": "third-person",
    "verleden": "past",
    "voorwaardelijk": "conditional",
}


TAGS = {**VERB_TAGS, **GLOSS_TAGS, **TABLE_TAGS}

# https://nl.wiktionary.org/wiki/Categorie:WikiWoordenboek:Contextlabels
TOPICS = {
    "aardrijkskunde": "geography",
    "adel": "nobility",
    "anatomie": "anatomy",
    "antropologie": "anthropology",
    "archeologie": "archaeology",
    "astrologie": "astrology",
    "astronomie": "astronomy",
    # "bacteriën": "bacterium",
    # "badminton": "badminton",
    "basketbal": "basketball",
    "bedrijf": "business",
    "bedrijfskunde": "business",  # "business administration",
    # "bedrijfstak": "industrial branch",
    "beeldhouwkunst": "arts",  # "sculpting"
    # "beroep": "profession",
    "beschrijvende plantkunde": "botany",  # "descriptive botany"
    # "bidsprinkhanen": "mantises",
    "biochemie": "biochemistry",
    "biologie": "biology",
    "bloemplanten": "botany",
    "boekbinderij": "bookbinding",
    "boekhouding": "accounting",
    "bosbouw": "forestry",
    "bouwkunde": "architecture",
    # "breukgetal": "",
    "bridge": "bridge",
    # "buideldieren": "marsupial",
    # "buikpotigen": "",
    # "buissnaveligen": "",
    # "buistandigen": "",
    # "cloacadieren": "monotreme",
    "communicatie": "communications",
    # "coniferen": "conifers",
    "cosmetica": "cosmetics",
    "cryptografie": "cryptography",
    # "cultuur": "culture",
    "dag": "weekday",
    "dans": "dance",
    "demografie": "demography",
    "demoniem": "demonym",
    "dichtkunst": "poetry",
    # "dierengeluid": "animal sound",
    "diergeneeskunde": ["veterinary", "medicine"],
    "dierkunde": "zoology",
    # "dierluizen": "",
    "diplomatie": "diplomacy",
    "drinken": "beverages",
    # "duifachtigen": "",
    # "duikers": "",
    # "dysfemisme": "dysphemism",
    "ecologie": "ecology",
    "economie": "economics",
    # "eendvogels": "anseriform",
    # "eenheid": "",
    "effectenhandel": "trading",
    "egyptologie": "Egyptology",
    # "toponiem: eiland": "",
    "elektronica": "electronics",
    "elektrotechniek": "electrical-engineering",
    # "element": "element",
    "emotie": "emotion",
    # "evenhoevigen": "",
    # "familie": "family",
    "farmacologie": "pharmacology",
    # "feest": "party",
    # "fietsen": "cycle",
    "filatelie": "philately",
    "filmkunst": "cinematography",
    "filosofie": "philosophy",
    "financieel": "financial",
    # "flamingoachtigen": "",
    "folklore": "folklore",
    "fotografie": "photography",
    # "fruit": "fruit",
    # "futen": "grebe",
    "fysiologie": "physiology",
    "genetica": "genetics",
    # "gentachtigen": "",
    "geologie": "geology",
    "geopolitiek": "geopolitics",
    "gereedschap": "tools",
    "geschiedenis": "history",
    "glaciologie": "glaciology",
    # "godheid": "deity",
    # "graan": "grain",
    "grammatica": "grammar",
    "groente": "vegetable",
    # "grondmechanica": "",
    "haar": "hairstyle",
    "handel": "business",
    "heraldiek": "heraldry",
    "hobby": "hobbies",
    "hoofddeksel": "headgear",
    # "horeca": "",
    "houtbewerking": "woodworking",
    # "huishouden": "housekeeping",
    "imkerij": "beekeeping",
    # "industrie": "industry",
    "informatica": "computer sciences",
    "internet": "Internet",
    # "jaarwisseling": "",
    "jachttaal": "hunting",
    # "jongerentaal": "",
    "juridisch": "legal",
    "kaartspel": "card-games",
    # "kamperen": "camping",
    # "kerst": "Christmas",
    # "kindertaal": "child language",
    "kleding": "clothing",
    "kleur": "colour",
    # "knutselen": "",
    "kookkunst": "culinary",
    # "krachtsport": "",
    "kristallografie": "crystallography",
    # "kruid": "",
    # "kuiperij": "",
    "kunst": "arts",
    "landbouw": "agriculture",
    "landmeetkunde": "surveying",
    "leenstelsel": "feudalism",
    # "leerbewerking": "",
    # "leidekkerij": "",
    "letterkunde": "literature",
    "lhbt": "LGBT",
    "logica": "logic",
    "luchtvaart": "aviation",
    # "maatschappij": "company",
    # "magie": "magic",
    "makelaardij": "real-estate",
    # "materiaalkunde": "materials science",
    # "media": "",
    "medisch": "medicine",
    # "meer": "lake",
    "meetkunde": "geometry",
    "metaalbewerking": "metalworking",
    "metallurgie": "metallurgy",
    "klimatologie": "climatology",
    "meteorologie": "meteorology",
    # "metonymisch": "",
    "meubel": "furniture",
    "mijnbouw": "mining",
    "milieukunde": "ecology",
    "militair": "military",
    "mineraal": "mining",
    "mineralogie": "mineralogy",
    # "misdaad": "crime",
    "mode": "fashion",
    # "molenaarsambacht": "",
    "muziek": "music",
    "muziekinstrument": "music",
    "mycologie": "mycology",
    "mythologie": "mythology",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag in TOPICS:
            tr_topic = TOPICS[raw_tag]
            if isinstance(tr_topic, str):
                data.topics.append(tr_topic)
            elif isinstance(tr_topic, list):
                data.topics.extend(tr_topic)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
