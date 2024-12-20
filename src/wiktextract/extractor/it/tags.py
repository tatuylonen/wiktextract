from .models import WordEntry

TABLE_TAGS = {
    # https://it.wiktionary.org/wiki/Template:It-decl-agg4
    "singolare": "singular",
    "plurale": "plural",
    "positivo": "positive",
    "superlativo assoluto": ["absolute", "superlative"],
    "maschile": "masculine",
    "femminile": "feminine",
    # https://it.wiktionary.org/wiki/Template:It-decl-agg2
    "m e f": ["masculine", "feminine"],
    # https://it.wiktionary.org/wiki/Template:It-conj
    "infinito": "infinitive",
    "verbo ausiliare": "auxiliary",
    "gerundio": "gerund",
    "participio presente": ["present", "participle"],
    "participio passato": ["past", "participle"],
    "prima": "first-person",
    "seconda": "second-person",
    "terza": "third-person",
    "presente": "present",
    "imperfetto": "imperfect",
    "passato remoto": "past-remote",
    "futuro": "future",
    "passato prossimo": ["past", "perfect"],
    "trapassato prossimo": ["pluperfect", "past", "perfect"],
    "trapassato remoto": ["historic", "past-remote"],
    "futuro anteriore": ["future", "perfect"],
    "passato": "past",
    "trapassato": ["past", "perfect"],
    "imperativo": "imperative",
    "riflessivo pronominale": ["reflexive", "pronominal"],
}

FORM_LINE_TEMPLATE_TAGS = {
    # https://it.wiktionary.org/wiki/Template:A_cmp
    "comparativo": "comparative",
    "superlativo": "superlative",
}

# https://it.wiktionary.org/wiki/Template:Term/d
TERM_TEMPLATE_TOPICS = {
    "abbigliamento": "clothing",
    "aeronautica": "aeronautics",
    "agricoltura": "agriculture",
    "algebra": "algebra",
    "ambito sportivo": "sports",
    "anatomia": "anatomy",
    # "animali": "",
    "antropologia": "anthropology",
    "araldica": "heraldry",
    "archeologia": "archaeology",
    "architettura": "architecture",
    "aritmetica": "arithmetic",
    "arm.": "weaponry",
    "arma": "weaponry",
    "armamento": "weaponry",
    "armi": "weaponry",
    "arte": "arts",
    "astrologia": "astrology",
    "astronomia": "astronomy",
    "botanica": "botany",
    "biochimica": "biochemistry",
    "biologia": "biology",
    "biotecnologia": "biotechnology",
    # "burocrazia": "",
    "calcio": "soccer",
    "carte": "card-games",
    "chimica": "chemistry",
    "chimica generale": "chemistry",
    "chimica inorganica": "chemistry",
    "chimica organica": "chemistry",
    "chimica analitica": "chemistry",
    "chimica industriale": "chemistry",
    "chirurgia": "surgery",
    "cinematografia": "cinematography",
    "colore": "color",
    "commercio": "commerce",
    # "composti organici": "",
    # "composti inorganici": "",
    "cristianesimo": "Christianity",
    "danza": "dance",
    # "diritto": "",
    "ecclesiastico": "ecclesiastical",
    "ecologia": "ecology",
    "economia": "economics",
    "edilizia": "construction",
    "elementi chimici": "chemistry",
    "elettronica": "electronics",
    "elettrotecnica": "electrical-engineering",
    "entomologia": "entomology",
    "equitazione": "equitation",
    "erpetologia": "herpetology",
    # "esoterismo": "",
    "etnologia": "ethnology",
    "falegnameria": "carpentry",
    # "familiare": "",
    "farmacologia": "pharmacology",
    "ferrovia": "railways",
    "filosofia": "philosophy",
    "finanza": "finance",
    "fisica": "physics",
    "fisiologia": "physiology",
    "fonologia": "phonology",
    # "forestierismo": "",
    "fotografia": "photography",
    # "gastronomia": "gastronomy",
    "genetica": "genetics",
    "geografia": "geography",
    "geologia": "geology",
    "geometria": "geometry",
    "gioco": "games",
    "giornalistico": "journalism",
    "grammatica": "grammar",
    "idraulica": "hydraulics",
    "informatica": "informatics",
    "ingegneria": "engineering",
    "internet": "Internet",
    "ittiologia": "ichthyology",
    "legale": "law",
    "letteratura": "literature",
    "linguistica": "linguistics",
    # "macelleria": "",
    "malacologia": "malacology",
    "mammalogia": "mammalogy",
    "marina": "navy",
    "matematica": "mathematics",
    "meccanica": "mechanics",
    "medicina": "medicine",
    "metallurgia": "metallurgy",
    "meteorologia": "meteorology",
    # "Metrica": "",
    # "Metrica classica": "",
    # "Metrica contemporanea": "",
    # "Metrica latina": "",
    "militare": "military",
    "minerale": "mineralogy",
    "mineralogia": "mineralogy",
    "mitologia": "mythology",
    "moda": "fashion",
    "musica": "music",
    "numismatica": "numismatics",
    "ornitologia": "ornithology",
    # "pedagogia": "pedagogy",
    # "pittura": "painting",
    "poesia": "poetry",
    # "polimeri": "",
    "politica": "politics",
    # "Popolare": "",
    # "Professioni": "",
    "psichiatria": "psychiatry",
    "psicanalisi": "psychoanalysis",
    "psicologia": "psychology",
    "religione": "religion",
    "topografia": "topography",
    # "Toponimi": "",
    "paleontologia": "paleontology",
    "pianta": "botany",
    "scacchi": "chess",
    # "Scuola": "",
    "sessualità": "sexuality",
    "sociologia": "sociology",
    "sport": "sports",
    "sport invernali": "sports",
    "statistica": "statistics",
    "storia": "history",
    # "strumenti musicali": "",
    "teatro": "theater",
    "tecnica": "technology",
    "tecnologia": "technology",
    "telecomunicazioni": "telecommunications",
    "tessile": "textiles",
    "tipografia": "typography",
    "veterinaria": "veterinary",
    "zoologia": "zoology",
    # "zootecnica": "",
}

TERM_TEMPLATE_TAGS = {
    "antico": "archaic",
    "obsoleto": "obsolete",
    "formale": "formal",
    "gergale": "slang",
    "informale": "informal",
    "letterario": "literary",
    "neologismo": "neologism",
    "offensivo": "offensive",
    "raro": "rare",
    "regionale": "regional",
    "volgare": "vulgar",
}

# https://it.wiktionary.org/wiki/Categoria:Template_ambito
GLOSS_LIST_TEMPATE_TAGS = {
    "accrescitivo": "augmentative",  # Template:Accr
    "colloquiale": "colloquial",  # Template:Coll
    "diminutivo": "diminutive",  # Template:Dim
    "per estensione": "broadly",  # Template:Est
    "senso figurato": "figuratively",  # Template:Fig
    "letteralmente": "literally",  # Template:Lett
    "peggiorativo": "pejorative",  # Template:Pegg
    "riferito solo a persone": "person",  # Template:Pers
    "per sineddoche": "synecdoche",  # Template:Sndc
    "specialmente al plurale": ["especially", "in-plural"],  # Template:Spec pl
    "spregiativo": "pejorative",  # Template:Spreg
    "vezzeggiativo": "endearing",  # Template:Vezz
    "volgare": "vulgar",  # Template:Vulg
}


TAGS = {
    **TABLE_TAGS,
    **FORM_LINE_TEMPLATE_TAGS,
    **TERM_TEMPLATE_TAGS,
    **GLOSS_LIST_TEMPATE_TAGS,
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag in TERM_TEMPLATE_TOPICS and hasattr(data, "topics"):
            data.topics.append(TERM_TEMPLATE_TOPICS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
