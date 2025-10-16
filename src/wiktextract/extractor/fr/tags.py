# Grammatical glossary appendix:
# https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical
# List of templates:
# https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles
from .models import WordEntry

# https://en.wikipedia.org/wiki/Grammatical_gender
GENDER_TAGS: dict[str, str | list[str]] = {
    "commun": "common",
    "féminin": "feminine",
    "masculin": "masculine",
    "neutre": "neuter",
    # https://fr.wiktionary.org/wiki/Modèle:mf
    "masculin et féminin identiques": ["masculine", "feminine"],
    # table header: https://fr.wiktionary.org/wiki/Modèle:fr-rég
    "masculin et féminin": ["masculine", "feminine"],
    # "Modèle:mf ?", "Modèle:fm ?"
    "masculin ou féminin (l’usage hésite)": ["masculine", "feminine"],
    "féminin ou masculin (l’usage hésite)": ["feminine", "masculine"],
    "invariable": "invariable",  # Modèle:invar
    # Modèle:flex-ku-nommixt
    "masculin sing.": ["masculine", "singular"],
    "féminin sing.": ["feminine", "singular"],
    # Template:ja-flx-adj-な
    "neutre négatif": ["neuter", "negative"],
    "neutre passé": ["neuter", "past"],
    "neutre négatif passé": ["neuter", "negative", "past"],
    "poli négatif": ["polite", "negative"],
    "poli passé": ["polite", "past"],
    "poli négatif passé": ["polite", "negative", "past"],
    # Template:m
    "masculin animé": ["masculine", "animate"],
    "masculin inanimé": ["masculine", "inanimate"],
    # Template:f
    "féminin animé": ["feminine", "animate"],
    "féminin inanimé": ["feminine", "inanimate"],
    # Template:n
    "neutre animé": ["neuter", "animate"],
    "neutre inanimé": ["neuter", "inanimate"],
}

# https://en.wikipedia.org/wiki/Grammatical_number
NUMBER_TAGS: dict[str, str | list[str]] = {
    "singulier": "singular",
    "pluriel": "plural",
    "duel": "dual",
    "collectif": "collective",
    "singulatif": "singulative",
    "indénombrable": "uncountable",  # sv-nom-c-ind
    "au singulier": "singular",
    "au singulier uniquement": "singular-only",
    "au pluriel": "plural",
    "au pluriel uniquement": "plural-only",
    "singulier et pluriel identiques": ["singular", "plural"],
    "nom collectif": "collective",
    # "générique": "",  # Modèle:g
    # "nom d'unité": "",  # Modèle:nu
    "généralement indénombrable": "uncountable",
    "dénombrable": "countable",
    # Modèle:br-nom
    "pluriel 1": "plural",
    "pluriel 2": "plural",
    "pluriel 3": "plural",
    "pluriel 4": "plural",
    # https://fr.wiktionary.org/wiki/Modèle:avk-tab-conjug
    "1": "first-person",
    "2": "second-person",
    "3": "third-person",
    "4": "fourth-person",
    # Template:nl-conj-cons
    # https://en.wikipedia.org/wiki/Dutch_grammar#Personal_pronouns
    "ik": ["first-person", "singular"],
    "jij": ["second-person", "singular", "informal"],
    "hij, zij, het": "third-person",
    "wij": ["first-person", "plural"],
    "jullie": ["second-person", "plural", "informal"],
    "zij": ["third-person", "plural"],
    "u": "second-person",
}

# https://en.wikipedia.org/wiki/Grammatical_mood
MOOD_TAGS: dict[str, str] = {
    "indicatif": "indicative",
    "subjonctif": "subjunctive",
    "conditionnel": "conditional",
    "impératif": "imperative",
    "volitif": "volitive",
    "déclaratif": "declarative",
    "interrogatif": "interrogative",
    "aperceptif": "apperceptive",
    "euphémique": "euphemistic",
    "évidentiel": "evidential",
    "spéculatif": "speculative",
    "assertif": "assertive",
    "hortatif": "hortative",
    "promissif": "promissive",
    "conditionnel / subjonctif": ["conditional", "subjunctive"],
    "conjonctif": "subjunctive",
    "provisionnel": "temporal",
    # Template:de-conj
    "subjonctif i": "subjunctive-i",
    "subjonctif ii": "subjunctive-ii",
}

VERB_FORM_TAGS: dict[str, str | list[str]] = {
    "participe": "participle",
    "imparfait": "imperfect",
    # Template:ku-conj-trans
    "parfait": "perfect",
    "imparfait narratif": ["imperfect", "narrative"],
    "infinitif": "infinitive",
    "gérondif": "gerund",
    # template "pt-verbe-flexion"
    "infinitif personnel": ["infinitive", "personal"],
    "supin": "supine",
    # Template:ko-conj
    "conjugaison": "conjugation",
    "radical": "radical",
    "formes finales": "final",
    "registre formel": "formal",
    "registre informel": "informal",
    "non poli": "impolite",
    "poli": "polite",
    "formes nominales": "nominal",
    "formes conjonctives": "subjunctive",
    # Template:ja-在る
    "formes de base": "base-form",
    "affirmatif": "affirmative",
    "négatif": "negative",
    "adverbial": "adverbial",
    # Template:bg-verbe186
    "aoriste": "aorist",
    "participe passé passif": ["participle", "past", "passive"],
    "participe passé actif": ["participle", "past", "active"],
    "participe imparfait": ["participle", "imperfect"],
    "auxiliaire": "auxiliary",
    "bitransitif": "ditransitive",
    "déterminé": "determinate",
    "indéterminé": "indeterminate",
    # Template:irrégulier
    "irrégulier": "irregular",
}

# https://en.wikipedia.org/wiki/Grammatical_case
CASE_TAGS: dict[str, str | list[str]] = {
    "ablatif": "ablative",
    "accusatif": "accusative",
    "accusatif génitif": ["accusative", "genitive"],
    "nominatif": "nominative",
    "datif": "dative",
    "génitif": "genitive",
    "vocatif": "vocative",
    "instrumental": "instrumental",
    "locatif": "locative",
    "comitatif": "comitative",
    "essif": "essive",
    "illatif": "illative",
    # Template:ro-nom-tab
    "nominatif\naccusatif": ["nominative", "accusative"],
    "datif\ngénitif": ["dative", "genitive"],
    # Template:ko-nom
    "nominatif / attributif": ["nominative", "attributive"],
    # Modèle:fro-adj
    "sujet": "subject",
    "régime": "oblique",
}

# https://en.wikipedia.org/wiki/Grammatical_tense
TENSE_TAGS: dict[str, str | list[str]] = {
    "présent": "present",
    "passé": "past",
    "passé simple": "past",
    "futur": "future",
    "futur simple": "future",
    # https://en.wikipedia.org/wiki/Passé_composé
    "passé composé": ["past", "multiword-construction"],
    "plus-que-parfait": "pluperfect",
    "passé antérieur": ["past", "anterior"],
    "futur antérieur": ["future", "perfect"],
    "prétérit": "preterite",
    "présent simple, 3ᵉ pers. sing.": ["present", "third-person", "singular"],
    "participe passé": ["participle", "past"],
    "participe présent": ["participle", "present"],
    # Template:ku-conj-trans
    "présent progressif": ["present", "progressive"],
    "prétérit et imparfait": ["preterite", "imperfect"],
    "non passé": "non-past",
    "présent / futur": ["present", "future"],
    # Template:de-conj
    "futur i": "future-i",
    "futur ii": "future-ii",
    # Template:it-irrégulier-avere-1
    "présent affirmatif": ["present", "affirmative"],
    "présent négatif": ["present", "negative"],
}

# https://en.wikipedia.org/wiki/Grammatical_person
PERSON_TAGS: dict[str, str | list[str]] = {
    "1ᵉ personne": "first-person",
    "1ʳᵉ personne": "first-person",
    "2ᵉ personne": "second-person",
    "3ᵉ personne": "third-person",
    # Modèle:avk-conj
    "1ʳᵉ du sing.": ["first-person", "singular"],
    "2ᵉ du sing.": ["second-person", "singular"],
    "3ᵉ du sing.": ["third-person", "singular"],
    "1ʳᵉ du plur.": ["first-person", "plural"],
    "2ᵉ du plur.": ["second-person", "plural"],
    "3ᵉ du plur.": ["third-person", "plural"],
    "4ᵉ du plur.": ["fourth-person", "plural"],
}

SEMANTICS_TAGS: dict[str, str] = {
    # https://en.wikipedia.org/wiki/Definiteness
    "défini": "definite",
    "indéfini": "indefinite",
    # template:ro-nom-tab
    "articulé": "definite",
    "non articulé": "indefinite",
}

COMPARISON_TAGS: dict[str, str] = {
    # https://en.wikipedia.org/wiki/Comparison_(grammar)
    "positif": "positive",
    "comparatif": "comparative",
    "superlatif": "superlative",
    "non comparable": "not-comparable",
    "superlatif absolu": ["superlative", "absolute"],
}

# https://en.wikipedia.org/wiki/Occitan_language#Writing_system
OCCITAN_NORM_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:oc-norme_mistralienne
    "graphie mistralienne": "Mistralian",
    # https://fr.wiktionary.org/wiki/Modèle:oc-norme_classique
    # "graphie normalisée": "",
    # Modèle:oc-norme bonnaudienne
    # "graphie bonnaudienne": "",
}

# https://en.wikipedia.org/wiki/Breton_mutations
# https://fr.wiktionary.org/wiki/Modèle:br-nom
BRETON_MUTATION_TAGS: dict[str, str] = {
    "non muté": "unmutated",
    "adoucissante": "mutation-soft",
    "durcissante": "mutation-hard",
    "spirante": "mutation-spirant",
    "nasale": "mutation-nasal",
}

JA_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:ja-trans
    "kanji": "kanji",
    "hiragana": "hiragana",
    "katakana": "katakana",
    "transcription": "transcription",
}

OTHER_GRAMMATICAL_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:be-tab-cas
    "prépositionnel": "prepositional",
    "anglicisme": "Anglicism",
    "pronominal": "pronominal",
    "diminutif": "diminutive",
    "réfléchi": "reflexive",  # Modèle:réfl
    "réciproque": "reciprocal",  # Modèle:réciproque
    "impersonnel": "impersonal",  # Modèle:impers
    "transitif": "transitive",  # Modèle:t
    "transitif indirect": ["transitive", "indirect"],  # Modèle:transitif indir
    "intransitif": "intransitive",  # Modèle:i
    "injurieux": "offensive",  # Modèle:injurieux
    # Modèle:zh-formes
    "simplifié": "Simplified-Chinese",
    "traditionnel": "Traditional-Chinese",
    # Modèle:flex-ku-nomf
    "ézafé principal": ["ezafe", "primary"],
    "ézafé secondaire": ["ezafe", "secondary"],
    "cas oblique": "oblique",
    # Modèle:ku-conj-trans
    "forme affirmative": "affirmative",
    "forme négative": "negative",
    # Modèle:bg-nom
    "forme de base": "base-form",
    "pluriel numéral": ["plural", "numeral"],
    "animé": "animate",
    "inanimé": "inanimate",
    # Template:ko-nom
    "hangeul": "hangeul",
    "hanja": "hanja",
    "avec clitique": "clitic",
    "indéclinable": "indeclinable",
    "toponyme": "toponymic",
    "applicatif": "applicative",
    "causatif": "causative",
    "sigle": "abbreviation",
    "attributif": "attributive",
    "prédicatif": "predicative",
    # Template:cy-mut
    "non muté": "unmutated",
    "lénition": "lenition",
    "nasalisation": "nasalization",
    "syllabaire": "Syllabics",
    "par ellipse": "ellipsis",  # Template:ellipse
    "ironique": "ironic",
    "suffixe": "suffix",
    # Template:avk-tab-conjug
    "conjugaison présent indicatif": ["present", "indicative"],
    # Modèle:de-adjectif-déclinaisons
    "déclinaison forte": "strong",
    "déclinaison faible": "weak",
    "déclinaison mixte": "mixed",
    "singulier / pluriel": ["singular", "plural"],
}

# template text before gloss
SENSE_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:figuré
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_relation_entre_les_définitions
    # Catégorie:Modèles de genre textuel
    # Catégorie:Modèles de registre
    "sens figuré": "figuratively",
    "sens propre": "literally",
    "par métonymie": "metonymically",  # Modèle:par métonymie
    "par hyperbole": "hyperbole",
    "par extension": "broadly",
    "par analogie": "analogy",
    "en particulier": "especially",
    "par litote": "litotes",
    "par euphémisme": "euphemism",
    "spécifiquement": "specifically",
    "génériquement": "generically",
    "spécialement": "especially",
    "généralement": "generally",
    "enclise": "enclitic",
    "idiotisme": "idiomatic",
    "péjoratif": "pejorative",
    "désuet": "obsolete",
    "archaïsme": "archaic",
    "vieilli": "dated",
    "néologisme": "neologism",
    "argot": "slang",
    "rare": "rare",
    # "plus rare": "rare",
    "littéraire": "literary",  # Modèle:littéraire
    "poétique": "poetic",  # Modèle:poétique
    # "didactique": "",  # Modèle:didactique
    "soutenu": "formal",  # Modèle:soutenu
    "informel": "informal",  # Modèle:informel
    "familier": "familiar",  # Modèle:familier
    "très familier": "very-familiar",  # Modèle:très familier
    "populaire": "colloquial",  # Modèle:populaire
    "vulgaire": "vulgar",  # Modèle:vulgaire
    "langage enfantin": "childish",  # Modèle:enfantin
    # Catégorie:Modèles de thématique
    "anglicisme informatique": "Anglicism",
    "proverbe": "proverb",
    "collectivement": "collectively",
    "courant": "common",  # Modèle:courant
    "adjectif attribut": ["adjective", "attributive"],
}

# https://en.wikipedia.org/wiki/Voice_(grammar)
VOICE_TAGS: dict[str, str | list[str]] = {
    # https://fr.wiktionary.org/wiki/Modèle:eo-conj
    "participe actif": ["participle", "active"],
    "participe passif": ["participle", "passive"],
    "adverbe actif": ["adverb", "active"],
    "adverbe passif": ["adverb", "passive"],
    "substantif\nactif": ["subsuntive", "active"],
    "substantif\npassif": ["subsuntive", "passive"],
    "actif": "active",
    "passif": "passive",
    "adverbe": "adverb",
}

# Module:lexique/data
LEXIQUE_TAGS = {
    "hindouisme": "Hinduism",
    "judaïsme": "Judaism",
    "marxisme": "Marxism",
    "nazisme": "Nazism",
    "physique": "physical",
    "rhétorique": "rhetoric",
    "antiquité": "Ancient",
    "antiquité grecque": "Ancient-Greek",
    "antiquité romaine": "Ancient-Roman",
    "bible": "Biblical",
    "moyen âge": "Middle-Ages",
    "union européenne": "European-Union",
    "analyse": "analytic",
}

# Template:cmn-pron
# https://fr.wiktionary.org/wiki/自由
ZH_PRON_TAGS = {
    "pinyin": "Pinyin",
    "efeo": "EFEO",  # https://en.wikipedia.org/wiki/EFEO_Chinese_transcription
    "wade-giles": "Wade-Giles",
    "yale": "Yale",
    "zhuyin": "Bopomofo",
    "mandarin": "Mandarin",
    "cantonais": "Cantonese",
    "cantonais (yue)": "Cantonese",
    "jyutping": "Jyutping",
    "hakka": "Hakka",
    "pha̍k-fa-sṳ": "Phak-fa-su",
    "meixian, guangdong": ["Meixian", "Guangdong"],
    "jin": "Jin",
    "mindong": "Min-Dong",
    # https://en.wikipedia.org/wiki/Bàng-uâ-cê
    "bàng-uâ-cê (fuzhou)": ["Bang-ua-ce", "Fuzhou"],
    "minnan": "Min-Nan",
    "pe̍h-ōe-jī (hokkien : fujian, taïwan)": [
        "Peh-oe-ji",
        "Hokkien",
        "Fujian",
        "Taiwan",
    ],
    "chaozhou, peng'im": ["Chaozhou", "Peng'im"],
    "wu": "Wu",
    "shanghai": "Shanghai",
    "chinois médiéval": "Medieval-Chinese",
    "chinois archaïque": "Old-Chinese",
    "baxter-sagart": "Baxter-Sagart",
    "zhengzhang": "Zhengzhang",
}

ASPECT_TAGS = {
    "perfectif": "perfective",  # Modèle:perfectif
    "imperfectif": "imperfective",  # Modèle:imperfectif
}

GRAMMATICAL_TAGS: dict[str, str | list[str]] = {
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **MOOD_TAGS,
    **VERB_FORM_TAGS,
    **CASE_TAGS,
    **TENSE_TAGS,
    **PERSON_TAGS,
    **SEMANTICS_TAGS,
    **COMPARISON_TAGS,
    **OCCITAN_NORM_TAGS,
    **BRETON_MUTATION_TAGS,
    **JA_TAGS,
    **OTHER_GRAMMATICAL_TAGS,
    **SENSE_TAGS,
    **VOICE_TAGS,
    **LEXIQUE_TAGS,
    **ZH_PRON_TAGS,
    **ASPECT_TAGS,
}


def translate_raw_tags(data: WordEntry) -> WordEntry:
    from .topics import SLANG_TOPICS, TOPIC_TAGS

    raw_tags = []
    for raw_tag in data.raw_tags:
        raw_tag_lower = raw_tag.lower()
        if raw_tag_lower in GRAMMATICAL_TAGS:
            tr_tag = GRAMMATICAL_TAGS[raw_tag_lower]
            if isinstance(tr_tag, str) and tr_tag not in data.tags:
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                for t in tr_tag:
                    if t not in data.tags:
                        data.tags.append(t)
        elif hasattr(data, "topics") and raw_tag_lower in TOPIC_TAGS:
            data.topics.append(TOPIC_TAGS[raw_tag_lower])
        elif hasattr(data, "topics") and raw_tag_lower in SLANG_TOPICS:
            data.topics.append(SLANG_TOPICS[raw_tag_lower])
            if "slang" not in data.tags:
                data.tags.append("slang")
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
    return data
