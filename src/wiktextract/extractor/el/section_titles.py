# https://simple.wiktionary.org/wiki/Category:Part_of_speech_templates
import re
from enum import Enum, auto
from typing import TypedDict


class Heading(Enum):
    Err = auto()
    Ignored = auto()
    POS = auto()
    Etym = auto()
    Pron = auto()
    Infl = auto()
    Related = auto()
    Synonym = auto()
    Homonym = auto()
    Antonym = auto()
    Translation = auto()
    Derived = auto()
    Ref = auto()
    Notes = auto()


Tags = list[str]
POSName = str
POSMap = TypedDict(
    "POSMap",
    {
        "pos": POSName,
        # "debug" is legacy from [en], might be implemented
        "debug": str,
        "tags": Tags,
    },
    total=False,
)

# Main entries for different kinds of POS headings; no aliases
# XXX translate these
POS_HEADINGS: dict[str, POSMap] = {
    # "": {"pos": "", "tags": [""],
    # άρθρο: article // article // article of a charter, law, contract etc.
    # // limb
    "άρθρο": {"pos": "article"},
    # έκφραση - πολυλεκτικός όρος:   έκφραση: expression '' ???,
    # πολυλεκτικός: polylectic όρος: term (word, phrase; limitation,
    # restriction) // definition, stipulation // clause // article όρος:
    # mount, mountain
    "έκφραση - πολυλεκτικός όρος": {"pos": "phrase"},
    # έκφραση και επίρρημα (επιρρηματική έκφραση):   έκφραση: expression
    # και: and // also // plus, and // past (time) επίρρημα: adverb (lexical
    # category) επιρρηματική: [επιρρηματικός: adverbial, relating to an
    # adverb] // Nominative feminine singular form of επιρρηματικός
    # (epirrimatikós). // Accusative feminine singular form of επιρρηματικός
    # (epirrimatikós). // Vocative feminine singular form of επιρρηματικός
    # (epirrimatikós). έκφραση: expression
    "έκφραση και επίρρημα (επιρρηματική έκφραση)": {"pos": "adv_phrase"},
    # έκφραση του bask:   έκφραση: expression του: [ο: the definite
    # masculine singular article. the] // genitive masculine singular of ο
    # (o) (the) // genitive neuter singular of ο (o) (the) του: him, it //
    # his, its 'bask' ???,
    ## "bask in something"
    ## "EXPRESSING 'BASK'" -> phrases?
    ## No special handling
    "έκφραση του": {"pos": "phrase"},
    # έκφραση: expression
    "έκφραση": {"pos": "phrase"},
    # ένθημα:   ένθημα: infix, interfix
    "ένθημα": {"pos": "infix"},
    # αμετάβατο ρήμα:   αμετάβατο: [αμετάβατος: intransitive] // Accusative
    # masculine singular form of αμετάβατος (ametávatos). // Nominative,
    # accusative and vocative neuter singular form of αμετάβατος
    # (ametávatos). ρήμα: verb
    "αμετάβατο ρήμα": {"pos": "verb", "tags": ["intransitive"]},
    "απαρέμφατο": {"pos": "verb", "tags": ["infinitive"]},
    # αντωνυμία:   αντωνυμία: pronoun // antonymy
    "αντωνυμία": {"pos": "pron"},
    # αριθμητικό:   αριθμητικό: numeral αριθμητικό: [αριθμητικός:
    # arithmetical, numerical] // Accusative masculine singular form of
    # αριθμητικός (arithmitikós). // Nominative, accusative and vocative
    # neuter singular form of αριθμητικός (arithmitikós).
    "αριθμητικό": {"pos": "num", "tags": ["number"]},
    # βαθμός επιθέτου:   βαθμός: grade (of job, exams, position in
    # employment) // rank // degree (unit of temperature) // (plural) marks,
    # grades // degree (severity of burns) // degree (of an adjective)
    # επιθέτου: [επίθετο: adjective // surname] // genitive singular of
    # επίθετο (epítheto)
    "βαθμός επιθέτου": {"pos": "adj", "tags": ["comparative"]},
    # βιβλίο φράσεων:   βιβλίο: book 'φράσεων' ???,
    "βιβλίο φράσεων": {"pos": "phrase"},
    # γερουνδιακό:   'γερουνδιακό' ???,
    "γερουνδιακό": {"pos": "verb", "tags": ["participle", "gerund"]},
    # γερούνδιο:   γερούνδιο: gerund
    "γερούνδιο": {"pos": "verb", "tags": ["participle", "gerund"]},
    # γνωμικά:   'γνωμικά' ???,
    "γνωμικά": {"pos": "phrase"},
    # γραμματικό στοιχείο:   γραμματικό: [γραμματικός: grammatical (relating
    # to grammar) // grammatical (using correct grammar)] // [γραμματικός:
    # grammarian // scribe, secretary] // Accusative masculine singular form
    # of γραμματικός (grammatikós). // Nominative, accusative and vocative
    # neuter singular form of γραμματικός (grammatikós). γραμματικό:
    # [γραμματικός: grammatical (relating to grammar) // grammatical (using
    # correct grammar)] // [γραμματικός: grammarian // scribe, secretary] //
    # Accusative singular form of γραμματικός (grammatikós). στοιχείο: unit,
    # element, cell (a portion of a whole) // element // unit, element, cell
    # (a portion of a whole) // item of data, piece of information // unit,
    # element, cell (a portion of a whole) // letter, piece of type // unit,
    # element, cell (a portion of a whole) // cell, battery // unit,
    # element, cell (a portion of a whole) // subset of a population
    "γραμματικό στοιχείο": {"pos": "particle"},
    # διλεκτικό ουσιαστικό:   'διλεκτικό' ???,  ουσιαστικό: noun,
    # substantive
    # two-word noun
    "διλεκτικό ουσιαστικό": {"pos": "noun"},
    # επίθετο - έκφραση:   επίθετο: adjective // surname '' ???,  έκφραση:
    # expression
    "επίθετο - έκφραση": {"pos": "adj"},
    # επίθετο - ουσιαστικό:   επίθετο: adjective // surname '' ???,
    # ουσιαστικό: noun, substantive
    "επίθετο - ουσιαστικό": {"pos": "adj"},
    # επίθετο ή ουσιαστικό:   επίθετο: adjective // surname ή: or // either
    # … or ουσιαστικό: noun, substantive
    "επίθετο ή ουσιαστικό": {"pos": "adj", "tags": ["adjective", "noun"]},
    # επίθετο και επίρρημα:   επίθετο: adjective // surname και: and // also
    # // plus, and // past (time) επίρρημα: adverb (lexical category)
    "επίθετο και επίρρημα": {"pos": "adj", "tags": ["adjective", "adverb"]},
    # επίθετο και ουσιαστικό:   επίθετο: adjective // surname και: and //
    # also // plus, and // past (time) ουσιαστικό: noun, substantive
    "επίθετο και ουσιαστικό": {"pos": "adj", "tags": ["adjective", "noun"]},
    # επίθετο, επιφώνημα, επίρρημα:   επίθετο: adjective // surname
    # επιφώνημα: interjection, exclamation επίρρημα: adverb (lexical
    # category)
    "επίθετο, επιφώνημα, επίρρημα": {"pos": "adj"},
    # επίθετο, ουσιαστικό, ρήμα:   επίθετο: adjective // surname ουσιαστικό:
    # noun, substantive ρήμα: verb
    "επίθετο, ουσιαστικό, ρήμα": {"pos": "adj"},
    # επίθετο, ουσιαστικό:   επίθετο: adjective // surname ουσιαστικό: noun,
    # substantive
    "επίθετο, ουσιαστικό": {"pos": "adj"},
    # επίθετο:   επίθετο: adjective // surname
    "επίθετο": {"pos": "adj"},
    # επίθημα για το σχηματισμό ουδέτερων ουσιαστικών:   επίθημα: suffix
    # για: for // for // for, by // for // about το: [ο: the definite
    # masculine singular article. the] // nominative neuter singular of ο
    # (o) (the) // accusative neuter singular of ο (o) (the) το: it (3rd
    # person neuter singular, nominative) // it (3rd person neuter singular,
    # accusative) 'σχηματισμό' ???,  ουδέτερων: [ουδέτερος: neuter, sexless
    # // neutral, non-aligned // the gender: neuter // neutral] // Genitive
    # masculine plural form of ουδέτερος (oudéteros). // Genitive feminine
    # plural form of ουδέτερος (oudéteros). // Genitive neuter plural form
    # of ουδέτερος (oudéteros). 'ουσιαστικών' ???,
    "επίθημα για το σχηματισμό ουδέτερων ουσιαστικών": {"pos": "suffix"},
    # επίθημα:   επίθημα: suffix
    "επίθημα": {"pos": "suffix"},
    # επίρρημα - επιφώνημα:   επίρρημα: adverb (lexical category) '' ???,
    # επιφώνημα: interjection, exclamation
    "επίρρημα - επιφώνημα": {"pos": "adv_phrase"},
    # επίρρημα, επίθετο:   επίρρημα: adverb (lexical category) επίθετο:
    # adjective // surname
    "επίρρημα, επίθετο": {"pos": "adv"},
    # επίρρημα, κλιτικός τύπος επιθέτου:   επίρρημα: adverb (lexical
    # category) 'κλιτικός' ???,  τύπος: sort, type, mould, stamp (of a
    # person character) // model, type (of car, etc) // shape, form // the
    # press, the newspapers collectively // formality, convention // formula
    # // a man, a guy, a chap επιθέτου: [επίθετο: adjective // surname] //
    # genitive singular of επίθετο (epítheto)
    "επίρρημα, κλιτικός τύπος επιθέτου": {"pos": "adv"},
    # επίρρημα, ουσιαστικό:   επίρρημα: adverb (lexical category)
    # ουσιαστικό: noun, substantive
    "επίρρημα, ουσιαστικό": {"pos": "adv"},
    # επίρρημα:   επίρρημα: adverb (lexical category)
    "επίρρημα": {"pos": "adv"},
    # επιθετικό συνθετικό:   'επιθετικό' ???,  συνθετικό: combining form
    # συνθετικό: [συνθετικός: synthetic // composite, component] //
    # Accusative masculine singular form of συνθετικός (synthetikós). //
    # Nominative, accusative and vocative neuter singular form of συνθετικός
    # (synthetikós).
    "επιθετικό συνθετικό": {"pos": "adj"},
    # επιρρηματική έκφραση:   επιρρηματική: [επιρρηματικός: adverbial,
    # relating to an adverb] // Nominative feminine singular form of
    # επιρρηματικός (epirrimatikós). // Accusative feminine singular form of
    # επιρρηματικός (epirrimatikós). // Vocative feminine singular form of
    # επιρρηματικός (epirrimatikós). έκφραση: expression
    "επιρρηματική έκφραση": {"pos": "adv_phrase"},
    # επιφώνημα - ουσιαστικό:   επιφώνημα: interjection, exclamation '' ???,
    # ουσιαστικό: noun, substantive
    "επιφώνημα - ουσιαστικό": {"pos": "intj"},
    # επιφώνημα και ουσιαστικό:   επιφώνημα: interjection, exclamation και:
    # and // also // plus, and // past (time) ουσιαστικό: noun, substantive
    "επιφώνημα και ουσιαστικό": {"pos": "intj"},
    # επιφώνημα:   επιφώνημα: interjection, exclamation
    "επιφώνημα": {"pos": "intj"},
    # θηλυκό:   θηλυκό: woman, female θηλυκό: [θηλυκός: female (feminine
    # gender) // feminine (female person or animal)] // Accusative masculine
    # singular form of θηλυκός (thilykós). // Nominative, accusative and
    # vocative neuter singular form of θηλυκός (thilykós).
    "θηλυκό": {"pos": "noun", "tags": ["feminine"]},
    # κάντζι:   'κάντζι' ???,
    "κάντζι": {"pos": "character", "tags": ["kanji"]},
    # κατάληξη αρσενικών επιθέτων:   κατάληξη: ending, termination // result
    # or outcome // ending, suffix αρσενικών: [αρσενικός: masculine] //
    # Genitive masculine plural form of αρσενικός (arsenikós). // Genitive
    # feminine plural form of αρσενικός (arsenikós). // Genitive neuter
    # plural form of αρσενικός (arsenikós). επιθέτων: [επίθετο: adjective //
    # surname] // genitive plural of επίθετο (epítheto)
    "κατάληξη αρσενικών επιθέτων": {
        "pos": "suffix",
        "tags": ["masculine", "adjective"],
    },
    # κατάληξη αρσενικών ουσιαστικών:   κατάληξη: ending, termination //
    # result or outcome // ending, suffix αρσενικών: [αρσενικός: masculine]
    # // Genitive masculine plural form of αρσενικός (arsenikós). //
    # Genitive feminine plural form of αρσενικός (arsenikós). // Genitive
    # neuter plural form of αρσενικός (arsenikós). 'ουσιαστικών' ???,
    "κατάληξη αρσενικών ουσιαστικών": {
        "pos": "suffix",
        "tags": ["masculine", "noun"],
    },
    # κατάληξη επιρρημάτων:   κατάληξη: ending, termination // result or
    # outcome // ending, suffix επιρρημάτων: [επίρρημα: adverb (lexical
    # category)] // Genitive plural form of επίρρημα (epírrima).
    "κατάληξη επιρρημάτων": {"pos": "suffix", "tags": ["adverbial"]},
    # κατάληξη θηλυκών ουσιαστικών:   κατάληξη: ending, termination //
    # result or outcome // ending, suffix θηλυκών: [θηλυκός: female
    # (feminine gender) // feminine (female person or animal)] // Genitive
    # masculine plural form of θηλυκός (thilykós). // Genitive feminine
    # plural form of θηλυκός (thilykós). // Genitive neuter plural form of
    # θηλυκός (thilykós). θηλυκών: [θηλυκό: woman, female] // [θηλυκό:
    # [θηλυκός: female (feminine gender) // feminine (female person or
    # animal)] // Accusative masculine singular form of θηλυκός (thilykós).
    # // Nominative, accusative and vocative neuter singular form of θηλυκός
    # (thilykós).] // Genitive plural form of θηλυκό (thilykó).
    # 'ουσιαστικών' ???,
    "κατάληξη θηλυκών ουσιαστικών": {
        "pos": "suffix",
        "tags": ["feminine", "noun"],
    },
    # κατάληξη ουδέτερων ουσιαστικών:   κατάληξη: ending, termination //
    # result or outcome // ending, suffix ουδέτερων: [ουδέτερος: neuter,
    # sexless // neutral, non-aligned // the gender: neuter // neutral] //
    # Genitive masculine plural form of ουδέτερος (oudéteros). // Genitive
    # feminine plural form of ουδέτερος (oudéteros). // Genitive neuter
    # plural form of ουδέτερος (oudéteros). 'ουσιαστικών' ???,
    "κατάληξη ουδέτερων ουσιαστικών": {
        "pos": "suffix",
        "tags": ["neuter", "noun"],
    },
    # κατάληξη ρημάτων:   κατάληξη: ending, termination // result or outcome
    # // ending, suffix ρημάτων: [ρήμα: verb] // Genitive plural form of
    # ρήμα (ríma).
    "κατάληξη ρημάτων": {"pos": "suffix", "tags": ["verb"]},
    # κατάληξη:   κατάληξη: ending, termination // result or outcome //
    # ending, suffix
    "κατάληξη": {"pos": "suffix"},
    # κλιτικός τύπος άρθρου:   'κλιτικός' ???,  τύπος: sort, type, mould,
    # stamp (of a person character) // model, type (of car, etc) // shape,
    # form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap άρθρου: [άρθρο: article
    # // article // article of a charter, law, contract etc. // limb] //
    # Genitive singular form of άρθρο (árthro).
    "κλιτικός τύπος άρθρου": {"pos": "article", "tags": ["form-of"]},
    # κλιτικός τύπος αντωνυμίας:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap αντωνυμίας: [αντωνυμία:
    # pronoun // antonymy] // Genitive singular form of αντωνυμία
    # (antonymía).
    "κλιτικός τύπος αντωνυμίας": {"pos": "pron", "tags": ["form-of"]},
    # κλιτικός τύπος αριθμητικού:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap αριθμητικού:
    # [αριθμητικός: arithmetical, numerical] // Genitive masculine and
    # neuter singular form of αριθμητικός (arithmitikós). αριθμητικού:
    # [αριθμητικό: numeral] // [αριθμητικό: [αριθμητικός: arithmetical,
    # numerical] // Accusative masculine singular form of αριθμητικός
    # (arithmitikós). // Nominative, accusative and vocative neuter singular
    # form of αριθμητικός (arithmitikós).] // Genitive singular form of
    # αριθμητικό (arithmitikó).
    "κλιτικός τύπος αριθμητικού": {"pos": "num", "tags": ["number", "form-of"]},
    # κλιτικός τύπος γερουνδιακού:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap 'γερουνδιακού' ???,
    "κλιτικός τύπος γερουνδιακού": {
        "pos": "verb",
        "tags": ["participle", "gerund", "form-of"],
    },
    # κλιτικός τύπος επιθέτου:   'κλιτικός' ???,  τύπος: sort, type, mould,
    # stamp (of a person character) // model, type (of car, etc) // shape,
    # form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap επιθέτου: [επίθετο:
    # adjective // surname] // genitive singular of επίθετο (epítheto)
    "κλιτικός τύπος επιθέτου": {"pos": "adj", "tags": ["form-of"]},
    "κλιτικός τύπος επιθήματος": {"pos": "suffix"},
    # κλιτικός τύπος επιρρήματος:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap επιρρήματος: [επίρρημα:
    # adverb (lexical category)] // Genitive singular form of επίρρημα
    # (epírrima).
    "κλιτικός τύπος επιρρήματος": {"pos": "adv", "tags": ["form-of"]},
    # κλιτικός τύπος κυρίου ονόματος:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap κυρίου: [κύριος: mister
    # (title conferred on an adult male) // master (someone who has control
    # over something or someone) // sir (an address to any male)] //
    # [κύριος: main, principal, most important] // Genitive singular form of
    # κύριος (kýrios). ονόματος: [όνομα: name // name, reputation // noun
    # (sensu lato), a word class including substantives (nouns, sensu
    # stricto) and adjectives] // Genitive singular form of όνομα (ónoma).
    "κλιτικός τύπος κυρίου ονόματος": {"pos": "name", "tags": ["form-of"]},
    # κλιτικός τύπος μετοχής:   'κλιτικός' ???,  τύπος: sort, type, mould,
    # stamp (of a person character) // model, type (of car, etc) // shape,
    # form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap μετοχής: [μετοχή:
    # participle // share, stock] // Genitive singular form of μετοχή
    # (metochí).
    "κλιτικός τύπος μετοχής": {
        "pos": "verb",
        "tags": ["participle", "form-of"],
    },
    # κλιτικός τύπος ουσιαστικού (διλεκτικό ουσιαστικό):   'κλιτικός' ???,
    # τύπος: sort, type, mould, stamp (of a person character) // model, type
    # (of car, etc) // shape, form // the press, the newspapers collectively
    # // formality, convention // formula // a man, a guy, a chap
    # 'ουσιαστικού' ???,  'διλεκτικό' ???,  ουσιαστικό: noun, substantive
    "κλιτικός τύπος ουσιαστικού (διλεκτικό ουσιαστικό)": {
        "pos": "noun",
        "tags": ["form-of"],
    },
    # κλιτικός τύπος ουσιαστικού, ουδέτερο, πληθυντικός:   'κλιτικός' ???,
    # τύπος: sort, type, mould, stamp (of a person character) // model, type
    # (of car, etc) // shape, form // the press, the newspapers collectively
    # // formality, convention // formula // a man, a guy, a chap
    # 'ουσιαστικού' ???,  ουδέτερο: neuter ουδέτερο: [ουδέτερος: neuter,
    # sexless // neutral, non-aligned // the gender: neuter // neutral] //
    # Accusative masculine singular form of ουδέτερος (oudéteros). //
    # Nominative, accusative and vocative neuter singular form of ουδέτερος
    # (oudéteros). πληθυντικός: plural
    "κλιτικός τύπος ουσιαστικού, ουδέτερο, πληθυντικός": {
        "pos": "noun",
        "tags": ["form-of"],
    },
    # κλιτικός τύπος ουσιαστικού:   'κλιτικός' ???,  τύπος: sort, type,
    # mould, stamp (of a person character) // model, type (of car, etc) //
    # shape, form // the press, the newspapers collectively // formality,
    # convention // formula // a man, a guy, a chap 'ουσιαστικού' ???,
    "κλιτικός τύπος ουσιαστικού": {"pos": "noun", "tags": ["form-of"]},
    # κλιτικός τύπος πολυλεκτικού όρου:   'κλιτικός' ???,  τύπος: sort,
    # type, mould, stamp (of a person character) // model, type (of car,
    # etc) // shape, form // the press, the newspapers collectively //
    # formality, convention // formula // a man, a guy, a chap
    # 'πολυλεκτικού' ???,  'όρου' ???,
    "κλιτικός τύπος πολυλεκτικού όρου": {"pos": "name"},
    # κορεατικό αλφάβητο:   'κορεατικό' ???,  αλφάβητο: alphabet, a series
    # of letters or graphics representing particular sounds or phonemes //
    # the ABCs of a subject matter; the basics; the most basic fundamentals
    # of a certain sphere of knowledge // [αλφάβητος: Rare form of αλφάβητο
    # (alfávito).] // Accusative singular form of αλφάβητος (alfávitos).
    "κορεατικό αλφάβητο": {"pos": "character", "tags": ["hangeul"]},
    # κύριο όνομα:   κύριο: [κύριος: mister (title conferred on an adult
    # male) // master (someone who has control over something or someone) //
    # sir (an address to any male)] // [κύριος: main, principal, most
    # important] // Accusative masculine singular form of κύριος (kýrios).
    # // Nominative, accusative and vocative neuter singular form of κύριος
    # (kýrios). κύριο: [κύριος: mister (title conferred on an adult male) //
    # master (someone who has control over something or someone) // sir (an
    # address to any male)] // [κύριος: main, principal, most important] //
    # Accusative singular form of κύριος (kýrios). όνομα: name // name,
    # reputation // noun (sensu lato), a word class including substantives
    # (nouns, sensu stricto) and adjectives
    "κύριο όνομα": {"pos": "name"},
    # μετοχή του βαρυφορτώνω, βαρυφορτώνομαι:   μετοχή: participle // share,
    # stock του: [ο: the definite masculine singular article. the] //
    # genitive masculine singular of ο (o) (the) // genitive neuter singular
    # of ο (o) (the) του: him, it // his, its 'βαρυφορτώνω' ???,
    # 'βαρυφορτώνομαι' ???,
    "μετοχή του": {
        "pos": "verb",
        "tags": ["participle"],
    },
    "μετοχή": {"pos": "verb", "tags": ["participle"]},
    # μετοχικό επίθετο:   'μετοχικό' ???,  επίθετο: adjective // surname
    "μετοχικό επίθετο": {"pos": "adj", "tags": ["possessive"]},
    # μονολεκτικό ουσιαστικό:   'μονολεκτικό' ???,  ουσιαστικό: noun,
    # substantive
    "μονολεκτικό ουσιαστικό": {"pos": "noun"},
    # μόριο (καθαρεύουσα):   μόριο: molecule // particle, speck (a very
    # small piece of matter) // part (of the body) // part (of the body) //
    # genitalia, parts // particle // point (in an evaluative scale)
    # καθαρεύουσα: Katharevousa (purist variant of Modern Greek)
    "μόριο (καθαρεύουσα)": {"pos": "particle", "tags": ["Katharevousa"]},
    # μόριο:   μόριο: molecule // particle, speck (a very small piece of
    # matter) // part (of the body) // part (of the body) // genitalia,
    # parts // particle // point (in an evaluative scale)
    "μόριο": {"pos": "particle"},
    # ουσιαστικό (καθαρεύουσα):   ουσιαστικό: noun, substantive καθαρεύουσα:
    # Katharevousa (purist variant of Modern Greek)
    "ουσιαστικό (καθαρεύουσα)": {"pos": "noun", "tags": ["Katharevousa"]},
    # ουσιαστικό - επίθετο:   ουσιαστικό: noun, substantive '' ???,
    # επίθετο: adjective // surname
    "ουσιαστικό - επίθετο": {"pos": "noun", "tags": ["adjective", "noun"]},
    # ουσιαστικό - επιφώνημα:   ουσιαστικό: noun, substantive '' ???,
    # επιφώνημα: interjection, exclamation
    "ουσιαστικό - επιφώνημα": {"pos": "noun", "tags": ["interjection", "noun"]},
    # ουσιαστικό - κύριο όνομα:   ουσιαστικό: noun, substantive '' ???,
    # κύριο: [κύριος: mister (title conferred on an adult male) // master
    # (someone who has control over something or someone) // sir (an address
    # to any male)] // [κύριος: main, principal, most important] //
    # Accusative masculine singular form of κύριος (kýrios). // Nominative,
    # accusative and vocative neuter singular form of κύριος (kýrios).
    # κύριο: [κύριος: mister (title conferred on an adult male) // master
    # (someone who has control over something or someone) // sir (an address
    # to any male)] // [κύριος: main, principal, most important] //
    # Accusative singular form of κύριος (kýrios). όνομα: name // name,
    # reputation // noun (sensu lato), a word class including substantives
    # (nouns, sensu stricto) and adjectives
    "ουσιαστικό - κύριο όνομα": {"pos": "name"},
    # ουσιαστικό - πολυλεκτικός όρος:   ουσιαστικό: noun, substantive ''
    # ???,  πολυλεκτικός: polylectic όρος: term (word, phrase; limitation,
    # restriction) // definition, stipulation // clause // article όρος:
    # mount, mountain
    "ουσιαστικό - πολυλεκτικός όρος": {"pos": "noun"},
    # ουσιαστικό /ˈkɒndʌkt/:   ουσιαστικό: noun, substantive '/ˈkɒndʌkt/'
    # ???,
    "ουσιαστικό": {"pos": "noun"},
    # ουσιαστικό αρσενικό:   ουσιαστικό: noun, substantive αρσενικό:
    # [αρσενικός: masculine] // inflection of αρσενικός (arsenikós): //
    # masculine accusative singular // inflection of αρσενικός (arsenikós):
    # // neuter nominative/accusative/vocative singular αρσενικό: arsenic
    "ουσιαστικό αρσενικό": {"pos": "noun", "tags": ["masculine"]},
    # ουσιαστικό επίρρημα:   ουσιαστικό: noun, substantive επίρρημα: adverb
    # (lexical category)
    "ουσιαστικό επίρρημα": {"pos": "adv", "tags": ["adverb", "noun"]},
    # ουσιαστικό θηλυκό:   ουσιαστικό: noun, substantive θηλυκό: woman,
    # female θηλυκό: [θηλυκός: female (feminine gender) // feminine (female
    # person or animal)] // Accusative masculine singular form of θηλυκός
    # (thilykós). // Nominative, accusative and vocative neuter singular
    # form of θηλυκός (thilykós).
    "ουσιαστικό θηλυκό": {"pos": "noun", "tags": ["feminine"]},
    # ουσιαστικό και επίθετο:   ουσιαστικό: noun, substantive και: and //
    # also // plus, and // past (time) επίθετο: adjective // surname
    "ουσιαστικό και επίθετο": {"pos": "noun", "tags": ["adjective", "noun"]},
    # ουσιαστικό και επιφώνημα:   ουσιαστικό: noun, substantive και: and //
    # also // plus, and // past (time) επιφώνημα: interjection, exclamation
    "ουσιαστικό και επιφώνημα": {
        "pos": "noun",
        "tags": ["interjection", "noun"],
    },
    # ουσιαστικό και κλιτικός τύπος ουσιαστικού:   ουσιαστικό: noun,
    # substantive και: and // also // plus, and // past (time) 'κλιτικός'
    # ???,  τύπος: sort, type, mould, stamp (of a person character) //
    # model, type (of car, etc) // shape, form // the press, the newspapers
    # collectively // formality, convention // formula // a man, a guy, a
    # chap 'ουσιαστικού' ???,
    "ουσιαστικό και κλιτικός τύπος ουσιαστικού": {"pos": "noun"},
    # ουσιαστικό και κύριο όνομα:   ουσιαστικό: noun, substantive και: and
    # // also // plus, and // past (time) κύριο: [κύριος: mister (title
    # conferred on an adult male) // master (someone who has control over
    # something or someone) // sir (an address to any male)] // [κύριος:
    # main, principal, most important] // Accusative masculine singular form
    # of κύριος (kýrios). // Nominative, accusative and vocative neuter
    # singular form of κύριος (kýrios). κύριο: [κύριος: mister (title
    # conferred on an adult male) // master (someone who has control over
    # something or someone) // sir (an address to any male)] // [κύριος:
    # main, principal, most important] // Accusative singular form of κύριος
    # (kýrios). όνομα: name // name, reputation // noun (sensu lato), a word
    # class including substantives (nouns, sensu stricto) and adjectives
    "ουσιαστικό και κύριο όνομα": {
        "pos": "noun",
        "tags": ["proper-noun", "noun"],
    },
    # ουσιαστικό, επίθετο:   ουσιαστικό: noun, substantive επίθετο:
    # adjective // surname
    "ουσιαστικό, επίθετο": {"pos": "noun", "tags": ["adjective", "noun"]},
    # ουσιαστικό, πολυλεκτικός όρος:   ουσιαστικό: noun, substantive
    # πολυλεκτικός: polylectic όρος: term (word, phrase; limitation,
    # restriction) // definition, stipulation // clause // article όρος:
    # mount, mountain
    "ουσιαστικό, πολυλεκτικός όρος": {"pos": "noun"},
    # ουσιαστικό, ρήμα:   ουσιαστικό: noun, substantive ρήμα: verb
    "ουσιαστικό, ρήμα": {"pos": "noun", "tags": ["noun", "verb"]},
    # πoλυλεκτικό ουσιαστικό:   'πoλυλεκτικό' ???,  ουσιαστικό: noun,
    # substantive
    "πoλυλεκτικό ουσιαστικό": {"pos": "noun"},
    # παθητική μετοχή του μυώ:   'παθητική' ???,  μετοχή: participle //
    # share, stock του: [ο: the definite masculine singular article. the] //
    # genitive masculine singular of ο (o) (the) // genitive neuter singular
    # of ο (o) (the) του: him, it // his, its 'μυώ' ???,
    "παθητική μετοχή του": {"pos": "verb", "tags": ["participle", "passive"]},
    # παροιμία - έκφραση:   παροιμία: proverb, saying, adage, maxim (phrase
    # expressing a basic truth) '' ???,  έκφραση: expression
    "παροιμία - έκφραση": {"pos": "phrase", "tags": ["idiomatic"]},
    # παροιμία:   παροιμία: proverb, saying, adage, maxim (phrase expressing
    # a basic truth)
    "παροιμία": {"pos": "phrase", "tags": ["idiomatic"]},
    # περιφραστικό ουσιαστικό:   'περιφραστικό' ???,  ουσιαστικό: noun,
    # substantive
    "περιφραστικό ουσιαστικό": {"pos": "noun"},
    # πολυλεκτικό επίθετο:   'πολυλεκτικό' ???,  επίθετο: adjective //
    # surname
    "πολυλεκτικό επίθετο": {"pos": "adj"},
    # πολυλεκτικό επίρρημα:   'πολυλεκτικό' ???,  επίρρημα: adverb (lexical
    # category)
    "πολυλεκτικό επίρρημα": {"pos": "adv"},
    # πολυλεκτικό ουσιαστικό:   'πολυλεκτικό' ???,  ουσιαστικό: noun,
    # substantive
    "πολυλεκτικό ουσιαστικό": {"pos": "noun"},
    # πολυλεκτικός όρος επίθετο:   πολυλεκτικός: polylectic όρος: term
    # (word, phrase; limitation, restriction) // definition, stipulation //
    # clause // article όρος: mount, mountain επίθετο: adjective // surname
    "πολυλεκτικός όρος επίθετο": {"pos": "adh"},
    # πολυλεκτικός όρος ουσιαστικό:   πολυλεκτικός: polylectic όρος: term
    # (word, phrase; limitation, restriction) // definition, stipulation //
    # clause // article όρος: mount, mountain ουσιαστικό: noun, substantive
    "πολυλεκτικός όρος ουσιαστικό": {"pos": "noun"},
    # πολυλεκτικός όρος:   πολυλεκτικός: polylectic όρος: term (word,
    # phrase; limitation, restriction) // definition, stipulation // clause
    # // article όρος: mount, mountain
    "πολυλεκτικός όρος": {"pos": "noun"},
    # προσδιοριστής:   'προσδιοριστής' ???,
    "προσδιοριστής": {"pos": "det"},
    # πρόθεση:   πρόθεση: preposition // intent, intention, purpose πρόθεση:
    # prosthesis (an artificial replacement for a body part) // prosthetic
    "πρόθεση": {"pos": "prep"},
    # πρόθημα:   πρόθημα: prefix
    "πρόθημα": {"pos": "prefix"},
    # πρόσφυμα:   πρόσφυμα: affix
    "πρόσφυμα": {"pos": "affix"},
    # ρήμα - επιφώνημα:   ρήμα: verb '' ???,  επιφώνημα: interjection,
    # exclamation
    "ρήμα - επιφώνημα": {"pos": "verb", "tags": ["interjection", "verb"]},
    # ρήμα μεταβατικό:   ρήμα: verb μεταβατικό: [μεταβατικός: transitive //
    # transition // transitional] // Accusative masculine singular form of
    # μεταβατικός (metavatikós). // Nominative, accusative and vocative
    # neuter singular form of μεταβατικός (metavatikós).
    "ρήμα μεταβατικό": {"pos": "verb", "tags": ["transitive"]},
    # ρήμα, αόριστος:   ρήμα: verb αόριστος: vague // indefinite //
    # preterite αόριστος: aorist, past tense, simple past, perfective past
    "ρήμα, αόριστος": {"pos": "verb", "tags": ["aorist"]},
    # ρήμα, μόριο, ουσιαστικό:   ρήμα: verb μόριο: molecule // particle,
    # speck (a very small piece of matter) // part (of the body) // part (of
    # the body) // genitalia, parts // particle // point (in an evaluative
    # scale) ουσιαστικό: noun, substantive
    "ρήμα, μόριο, ουσιαστικό": {
        "pos": "verb",
        "tags": ["particle", "noun", "verb"],
    },
    # ρήμα, ουσιαστικό:   ρήμα: verb ουσιαστικό: noun, substantive
    "ρήμα, ουσιαστικό": {"pos": "verb", "tags": ["noun", "verb"]},
    # ρήμα:   ρήμα: verb
    "ρήμα": {"pos": "verb"},
    # ρίζα:   ρίζα: root (of a plant) // root // root
    "ρίζα": {"pos": "root", "tags": ["morpheme"]},
    # ρηματική έκφραση:   'ρηματική' ???,  έκφραση: expression
    "ρηματική έκφραση": {"pos": "verb"},
    # σουπίνο:   'σουπίνο' ???,
    "σουπίνο": {"pos": "verb", "tags": ["supine"]},
    # συντομομορφή - ουσιαστικό:   συντομομορφή: abbreviation: initialism,
    # acronym, etc '' ???,  ουσιαστικό: noun, substantive
    "συντομομορφή - ουσιαστικό": {
        "pos": "abbrev",
        "tags": ["noun", "abbreviation"],
    },
    # συντομομορφή, αρκτικόλεξο:   συντομομορφή: abbreviation: initialism,
    # acronym, etc αρκτικόλεξο: initialism
    "συντομομορφή, αρκτικόλεξο": {"pos": "abbrev", "tags": ["initialism"]},
    # συντομομορφή:   συντομομορφή: abbreviation: initialism, acronym, etc
    "συντομομορφή": {"pos": "abbrev"},
    # σχήμα του ρήματος board:   σχήμα: figure, shape του: [ο: the definite
    # masculine singular article. the] // genitive masculine singular of ο
    # (o) (the) // genitive neuter singular of ο (o) (the) του: him, it //
    # his, its ρήματος: [ρήμα: verb] // Genitive singular form of ρήμα
    # (ríma). 'board' ???,
    "σχήμα του ρήματος": {"pos": "verb", "tags": ["form-of"]},
    # σύμβολο:   σύμβολο: symbol, character, glyph
    "σύμβολο": {"pos": "symbol"},
    # σύνδεσμος (καθαρεύουσα):   σύνδεσμος: conjunction // ligament // HTML
    # link // union, relationship, contact καθαρεύουσα: Katharevousa (purist
    # variant of Modern Greek)
    "σύνδεσμος (καθαρεύουσα)": {"pos": "conj", "tags": ["Katharevousa"]},
    # σύνδεσμος:   σύνδεσμος: conjunction // ligament // HTML link // union,
    # relationship, contact
    "σύνδεσμος": {"pos": "conj"},
    # σύνθετο επίθετο:   'σύνθετο' ???,  επίθετο: adjective // surname
    "σύνθετο επίθετο": {"pos": "adj"},
    # σύνθετο επίρρημα, έκφραση:   'σύνθετο' ???,  επίρρημα: adverb (lexical
    # category) έκφραση: expression
    "σύνθετο επίρρημα, έκφραση": {"pos": "adv"},
    # σύνθετο ουσιαστικό:   'σύνθετο' ???,  ουσιαστικό: noun, substantive
    "σύνθετο ουσιαστικό": {"pos": "noun"},
    # φράση:   φράση: phrase, expression
    "φράση": {"pos": "phrase"},
    # χαρακτήρας:   χαρακτήρας: character (the qualities which identify a
    # person) // character (a person's behaviours which identify them) //
    # character, letter, symbol
    "χαρακτήρας": {"pos": "symbol"},
    "ρηματικός τύπος": {"pos": "verb"},
    # Japanese translitteration entries
    "μεταγραφή": {"pos": "romanization"},
    "συγχώνευση": {"pos": "contraction"},
    "μορφή σύνθετου όρου": {"pos": "contraction"},
}

POS_HEADINGS_RE = re.compile(
    r"("
    + r"|".join(
        re.escape(s) for s in sorted(POS_HEADINGS.keys(), key=len, reverse=True)
    )
    + r")(.*)"
)


SubSectionMap = TypedDict(
    "SubSectionMap",
    {
        "type": Heading,
        # "debug" is legacy from [en], might be implemented
        "debug": str,
        "tags": Tags,
    },
    total=False,
)


SUBSECTION_HEADINGS: dict[str, SubSectionMap] = {
    "etymology": {"type": Heading.Etym},
    "ετυμολογία": {"type": Heading.Etym},
    "πηγές": {"type": Heading.Ignored},  # Not etymology, but literary sources
    "pronunciation": {"type": Heading.Pron},
    "προφορά": {"type": Heading.Pron},
    "αναλυτική κλίση": {"type": Heading.Infl},
    "κλίση": {"type": Heading.Infl},
    "references": {"type": Heading.Ref},
    "αναφορές": {"type": Heading.Ref},
    "άλλες γραφές": {"type": Heading.Related},
    "άλλες μορφές": {"type": Heading.Related},
    "ανεπίσημα": {"type": Heading.Related},
    "συγγενικά": {"type": Heading.Related},
    "πολυλεκτικοί όροι": {"type": Heading.Related},
    "συγγενείς": {"type": Heading.Related},
    # Homonyms
    "ομώνυμα / ομόηχα": {"type": Heading.Homonym},
    "συνώνυμα": {"type": Heading.Synonym},
    # Partial synonyms
    "μερική συνωνυμία": {"type": Heading.Synonym},
    # Exact synonym
    "ταυτόσημο": {"type": Heading.Synonym},
    "εκφράσεις": {"type": Heading.Related, "tags": ["idiomatic"]},
    "σύνθετα": {"type": Heading.Related, "tags": ["compound"]},
    "μεταγραφές": {"type": Heading.Related, "tags": ["romanization"]},
    # Related words in foreign languages
    "παράγωγα": {"type": Heading.Derived},
    # Derived words
    "απόγονοι": {"type": Heading.Derived},
    "υποκοριστικά": {"type": Heading.Derived, "tags": ["diminuitive"]},
    # Anagrams
    "αλλόγλωσσα παράγωγα": {"type": Heading.Translation},
    "μεταφράσεις": {"type": Heading.Translation},
    "αναγραμματισμοί": {"type": Heading.Ignored},
    # "misspelling" as POS
    "ανορθογραφία": {"type": Heading.Ignored},
    # see also
    "δείτε επίσης": {"type": Heading.Ignored},
    # Antonyms
    "αντώνυμα": {"type": Heading.Antonym},
    "αντώνυμη έκφραση": {"type": Heading.Antonym},
    "αρχικοί χρόνοι": {"type": Heading.Notes},
    "σημειώσεις": {"type": Heading.Notes},
    "υποσημειώσεις": {"type": Heading.Notes},
    # 'answers' to a phrasebook question: see τι κάνεις
    "απαντήσεις": {"type": Heading.Ignored},
    # Proverbs
    "παροιμίες": {"type": Heading.Ignored},
    # External links
    "εξωτερικοί σύνδεσμοι": {"type": Heading.Ignored},
    # "": {"type": Heading.Err},
}

SUBSECTIONS_RE = re.compile(
    r"([ =]*"
    + r"|".join(
        re.escape(s)
        for s in sorted(SUBSECTION_HEADINGS.keys(), key=len, reverse=True)
    )
    + r")(.*)[ =]*"
)
