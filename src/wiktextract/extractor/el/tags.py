"""TAGS

The strings in lists on the right-hand side here should be *shared* tags
between different edition implementations. `valid_tags` is a dictionary
of these tags (and can be expanded if necessary, although it is unlikely
to be needed anymore because we have a lot of them), with some metadata
in the value used in the English mainline extractor.

Otherwise, the implementation of tags is a translation effort: when this
edition of Wiktionary says 'x', what tags does that refer to?
"""

from wiktextract.extractor.el.models import Form, Linkage, Sense, WordEntry
from wiktextract.tags import uppercase_tags, valid_tags
from wiktextract.topics import valid_topics

# Tags used for modern Greek verb tables.
#
# Includes other verb related tags that may appear in headers etc.
#
# Some of the translations are from:
# * Greek: An Essential Grammar (Routledge Essential Grammars)
#
# * Reference:
#   https://el.wiktionary.org/wiki/Κατηγορία:Πρότυπα_κλίσης_ρημάτων_(νέα_ελληνικά)
#
# * Standard table:
#   https://el.wiktionary.org/wiki/ψάχνω
# * Non-standard table (relatively frequent):
#   https://el.wiktionary.org/wiki/αναφωνώ which follows
#   https://el.wiktionary.org/wiki/Πρότυπο:el-κλίσ-'λαλώ'
# * Others:
#   https://el.wiktionary.org/wiki/τρώω
# FIX:
# * Users wrongly putting noun inflections in a Κλήση section
#   https://el.wiktionary.org/wiki/δισεκατομμυριούχος
verb_table_tags_base: dict[str, list[str]] = {
    # Persons & numbers
    "α' ενικ.": ["first-person", "singular"],
    "β' ενικ.": ["second-person", "singular"],
    "γ' ενικ.": ["third-person", "singular"],
    "α' πληθ.": ["first-person", "plural"],
    "β' πληθ.": ["second-person", "plural"],
    "γ' πληθ.": ["third-person", "plural"],
    "α' πρόσωπο": ["first-person"],
    "β' πρόσωπο": ["second-person"],
    "γ' πρόσωπο": ["third-person"],
    "εγώ": ["first-person", "singular"],
    "εσύ": ["second-person", "singular"],
    "αυτός": ["third-person", "singular"],
    "εμείς": ["first-person", "plural"],
    "εσείς": ["second-person", "plural"],
    "αυτοί": ["third-person", "plural"],
    "(εσύ)": ["second-person", "singular"],
    "(εσείς)": ["second-person", "plural"],
    # Aspect groups
    # NOTE: redundant within most subcategories but needed to distinguish:
    # υποτακτική/προστακτική.
    # NOTE: The above distinction was deemed less important than being precise
    # over the main, most used forms, and so, these groups are ignored.
    # It also has the advantage of syncing standard and non-standard tables.
    "εξακολουθητικοί χρόνοι": [],  # ["imperfective"],
    "συνοπτικοί χρόνοι": [],  # ["perfective"],
    "συντελεσμένοι χρόνοι": [],  # ["perfect"],
    "συντελεσμένοι χρόνοι (β΄ τύποι)": [
        # "perfect",
        "type-b",
    ],
    "συντελεσμένοι χρόνοι β΄ (μεταβατικοί)": [
        # "perfect",
        "type-b",
        "transitive",
    ],
    "συντελεσμένοι χρόνοι β΄ (αμετάβατοι)": [
        # "perfect",
        "type-b",
        "intransitive",
    ],
    # Basic tenses / aspects
    "ενεστώτας": ["present"],
    "ενεστώτα": ["present"],
    "πρτ": ["imperfect"],
    "παρατατικός": ["imperfect"],
    "αόρ": ["aorist"],
    "αόριστος": ["aorist"],
    # Future
    "εξακολουθητικός μέλλοντας": ["future", "imperfect"],
    "εξ. μέλλ.": ["future", "imperfect"],
    "συνοπτ. μέλλ.": ["future"],
    "στιγμιαίος μέλλοντας": ["future"],  # στιγμιαίος = συνοπτικός
    "στ.μέλλ": ["future"],
    "συντελ. μέλλ.": ["future", "perfect"],
    "συντελεσμένος μέλλοντας α'": ["future", "perfect", "type-a"],
    # Perfect subtypes
    "παρακείμενος": ["perfect"],
    "παρακείμενος α'": ["perfect", "type-a"],
    "υπερσυντέλικος": ["pluperfect"],
    "υπερσυντέλικος α'": ["pluperfect", "type-a"],
    # Forms / moods
    "υποτακτική": ["subjunctive"],
    "προστακτική": ["imperative"],
    "μετοχή": ["participle"],
    "μτχ.": ["participle"],
    # παθητική μετοχή παρακειμένου
    "μτχ.π.π": ["passive", "participle"],
    "μτχ.π.ε": ["active", "participle"],
    "μετοχή (ενεστώτας)": ["participle", "present"],
    "απαρέμφατο": ["infinitive"],
    # Voices
    "ενεργ.:": ["active"],
    "παθητική φωνή": ["passive"],
    "παθ.φωνή": ["passive"],
    "στην παθητική φωνή": ["passive"],
    "παθητικό": ["passive"],
    # ["passive-normally"] not valid, maybe add it similar to plural-normally
    "συνήθως στην παθητική φωνή": [],
    "π.αόρ": ["passive", "aorist"],
    "χωρίς παθητική φωνή": [],  # passive-only is not valid (ADD IT?)
    # Others (τρώω table)
    "προσωπικές εγκλίσεις": [],  # (noise) personal-moods
    "απρόσωπες εγκλίσεις": ["impersonal"],  # impersonal-moods
    "μονολεκτικοί χρόνοι": [],  # ["simple-tenses"], # no   να/θα/έχει
    "περιφραστικοί χρόνοι": [],  # ["periphrastic"], # with να/θα/έχει
    "απαρέμφατο (αόριστος)": ["infinitive", "aorist"],
}

# https://el.wiktionary.org/wiki/free
english_tables_tags = {
    # Comparative
    # lit. "degree of comparison" but degree is a category already
    "παραθετικά": [],
    "θετικός": ["positive"],
    "συγκριτικός": ["comparative"],
    "υπερθετικός": ["superlative"],
    # Others
    "γ΄ ενικό ενεστώτα": ["third-person", "singular", "present"],
    "παθητική μετοχή": ["passive", "participle"],
    "ενεργητική μετοχή": ["active", "participle"],
    "μεταβατικό": ["transitive"],
    "αμετάβατο": ["intransitive"],
}

# https://el.wiktionary.org/wiki/balai
esperanto_tables_tags = {
    "μέλλοντας": ["future"],
    "μορφή": [],  # form is not valid
    "υποθετική": ["hypothetical"],
}

turkish_tables_tags = {
    # 1. https://el.wiktionary.org/wiki/un
    "... μου": ["first-person", "singular"],
    "... σου": ["second-person", "singular"],
    "... του": ["third-person", "singular"],
    "... μας": ["first-person", "plural"],
    "... σας": ["second-person", "plural"],
    "... τους": ["third-person", "plural"],
    "είμαι": ["first-person", "singular", "present"],
    "είσαι": ["second-person", "singular", "present"],
    "είναι": ["third-person", "singular", "plural", "present"],
    "είμαστε": ["first-person", "plural", "present"],
    "είστε": ["second-person", "plural", "present"],
    "ήμουν": ["first-person", "singular", "past"],
    "ήσουν": ["second-person", "singular", "past"],
    "ήταν": ["third-person", "singular", "plural", "past"],
    "ήμασταν": ["first-person", "plural", "past"],
    "ήσασταν": ["second-person", "plural", "past"],
    # 2. https://el.wiktionary.org/wiki/içmek
    "o": ["third-person", "singular"],
    "sen": ["second-person", "singular"],
    "ben": ["first-person", "singular"],
    "onlar": ["third-person", "plural"],
    "siz": ["second-person", "plural"],
    "biz": ["first-person", "plural"],
    "άρνηση": ["negative"],
    "θετικός - ερώτηση": ["positive", "interrogative"],
    "άρνηση - ερώτηση": ["negative", "interrogative"],
    "ενεστώς απλός": ["present"],
    "παρατατικός (i was watching)": ["imperfect"],
    "απροσδιόριστος αόριστος": ["indefinite", "past"],
    "απροσδιόριστος παρατατικός": ["indefinite", "imperfect"],
    'past future ("i was going to watch")': ["past-future"],
    'unwitnessed past future ("i was supposedly going to watch")': [
        "past-future"
    ],
    '"i used to watch" / "i would watch"': ["imperfect"],
    '"i used to watch" / "i would watch" (unwitnessed form)': ["imperfect"],
    "παθητικό απαρέμφατο": ["passive", "infinitive"],
    "ονομαστικές παράγωγες  (isim-fiil)": ["noun"],
    "παθητικές ονομαστικές παραγωγές": ["passive", "noun"],
    "επιθετικές παράγωγες  (sıfat-fiil)": ["adjective"],
    "επιρρηματικές παράγωγες  (zarf-fiil)": ["adverb"],
    # 3. https://el.wiktionary.org/wiki/yemek
    "διαρκής παροντικός (ενεστώτας)": ["present"],
    "απλός παροντικός": ["present"],
    "διαρκής παρελθοντικός (παρατατικός)": ["imperfect"],
    "καταφατικοί τύποι": ["positive"],
    "αρνητικοί τύποι": ["negative"],
    "ερωτηματικοί τύποι": ["interrogative"],
    "ερωτημ-αρνητ. τύποι": ["interrogative", "negative"],
    # 4. https://el.wiktionary.org/wiki/gitmek
    "pozitiv - izrični oblik": ["positive"],
    "pozitiv - upitni oblik": ["positive", "interrogative"],
    "negativ - izrični oblik": ["negative"],
    "negativ - upitni oblik": ["negative", "interrogative"],
}

# https://el.wiktionary.org/wiki/pompier
romanian_tables_tags = {
    "οριστική άρθρωση": ["definite"],
    "αόριστη άρθρωση": ["indefinite"],
}

# https://el.wiktionary.org/wiki/afrikanisch
german_tables_tags = {
    "με οριστικό άρθρο": ["definite"],
    "με αόριστο άρθρο": ["indefinite"],
    "ένδειξη ευγένειας": ["polite"],  # Sie
    "όλα τα γένη": ["masculine", "feminine", "neuter"],
    "ως κατηγορούμενο": ["predicative"],
}

# https://el.wiktionary.org/wiki/os
spanish_tables_tags = {
    "1ο": ["first-person"],
    "2ο": ["second-person"],
    "3ο": ["third-person"],
    # "https://el.wiktionary.org/wiki/entender"
    "υποτακτική (subjuntivo)": ["subjunctive"],
    "οριστική (indicativo)": ["indicative"],
    "αυτοπαθής": ["reflexive"],
    "τονιζόμενη": [],  # accent/accented is not valid
    # https://el.wiktionary.org/wiki/llegar
    "yo": ["first-person", "singular"],
    "tú": ["second-person", "singular"],
    "él, ella, ello, usted": ["third-person", "singular"],
    "usted": ["third-person", "singular"],
    "nosotros, nosotras": ["first-person", "plural"],
    "vosotros, vosotras": ["second-person", "plural"],
    "ellos, ellas, ustedes": ["third-person", "singular"],
    "ustedes": ["third-person", "plural"],
    "παρατατικός (ra)": ["imperfect"],
    "παρατατικός (se)": ["imperfect"],
    "καταφατικά": ["positive"],
    "δυνητική": ["potential"],
}

# https://el.wiktionary.org/wiki/biały
polish_tables_tags = {
    "αρσενικό έμψυχο": ["masculine", "animate"],
    "αρσενικό άψυχο": ["masculine", "inanimate"],
}

# https://el.wiktionary.org/wiki/любить
russian_tables_tags = {
    "α' πρόσ.": ["first-person", "singular"],
    "β' πρόσ.": ["second-person", "singular"],
    "γ' πρόσ.": ["third-person", "singular"],
    "μη συνοπτική όψη1": ["imperfective"],  # συνοπτικό perfective
}

# croître (παραδοσιακή ορθογραφία)
# croitre (ορθογραφία του 1990)
french_tags = {
    "(παραδοσιακή ορθογραφία)": [],  # normal spelling
    "παραδοσιακή ορθογραφία": [],
    "(ορθογραφία του 1990)": ["dated"],  # outdated-spelling is not valid
    "ορθογραφία του 1990": ["dated"],
    # Old French (fro)
    "cas sujet": ["subjective"],  # subjective case
    "cas régime": ["objective"],  # objective case
}

# https://el.wiktionary.org/wiki/πιστεύω
# https://el.wiktionary.org/wiki/δύω
ancient_greek_tables_tags = {
    "ἐγὼ": ["first-person", "singular"],
    "ἐγώ": ["first-person", "singular"],
    "σὺ": ["first-person", "singular"],
    "σύ": ["first-person", "singular"],
    "οὗτος": ["first-person", "singular"],
    "οὖτος": ["first-person", "singular"],  # spirit the other way
    "ἡμεῖς": ["first-person", "singular"],
    "ὑμεῖς": ["first-person", "singular"],
    "οὗτοι": ["first-person", "singular"],
    #
    "οριστική": ["indicative"],
    "ευκτική": ["optative"],
    "ονοματικοί  τύποι": [],  # EXTRA SPACES
    "ενεργητικός ενεστώτας": ["active", "present"],
    "ενεργητικός παρακείμενος": ["active", "perfect"],
    "ενεργητικός αόριστος α'": ["active", "aorist", "type-a"],
    "ενεργητικός αόριστος β'": ["active", "aorist", "type-b"],
    "ενεργητικός παρατατικός": ["active", "imperfect"],
    "ενεργητικός υπερσυντέλικος": ["active", "pluperfect"],
    "ενεργητικός μέλλοντας": ["active", "future"],
    "ονοματικοί τύποι": [],  # ?
    "2o δυϊκός": ["second-person", "dual"],
    "3o δυϊκός": ["third-person", "dual"],
    "μετοχή : αρσενικό - θηλυκό - ουδέτερο": ["participle"],  # BAD PARSING
    "στη μέση φωνή": ["middle"],  # middle voice
    "μέσος μέλλοντας": ["middle", "future"],
    "μέσος αόριστος α'": ["middle", "aorist", "type-a"],
    "μέσος αόριστος β'": ["middle", "aorist", "type-b"],
    "μέσος / παθητικός ενεστώτας": ["mediopassive", "present"],
    "μέσος / παθητικός παρακείμενος": ["mediopassive", "perfect"],
    "μέσος / παθητικός παρατατικός": ["mediopassive", "imperfect"],
    "μέσος / παθητικός υπερσυντέλικος": ["mediopassive", "pluperfect"],
    "1η συζυγία - μεσοπαθητικός ενεστώτας": ["mediopassive", "present"],
    "2η συζυγία - ενεργητικός ενεστώτας": ["active", "present"],
    "παθητικός αόριστος α'": ["passive", "aorist", "type-a"],
    "παθητικός μέλλοντας α'": ["passive", "future", "type-a"],
    # https://el.wiktionary.org/wiki/δορυφόρος
    # Dual terms
    "κλητική ὦ!": ["vocative"],
    "ονομ-αιτ-κλ": ["nominative", "accusative", "vocative"],
    "γεν-δοτ": ["genitive", "dative"],
}

ancient_greek_tags = {
    "δοτική": ["dative"],
    "αφαιρετική": ["ablative"],
    "τοπική": ["locative"],
    "δυϊκός": ["dual"],
    "γενική δοτική": ["genitive", "dative"],
    "εφελκυστικό νι": [],  # "ephelcystic nu" is not valid
}

# Tags need capitalization
transliteration_tags = {
    "λατινικοί χαρακτήρες": ["Latin", "transliteration"],
    "λατινικό αλφάβητο": ["Latin", "transliteration"],
    "αραβικό αλφάβητο": ["Arabic", "transliteration"],
    "κυριλλικοί χαρακτήρες": ["Cyrillic", "transliteration"],
    "yañalif": ["Yañalif", "transliteration"],
}

zones_tags = {
    "ηπα": ["US"],
    "ηβ": ["UK"],
    "αμερικανικά αγγλικά": ["US", "English"],
    "βρετανικά αγγλικά": ["UK", "English"],
    "αμερικανική σημασία": ["US"],  # US-meaning is not valid
    "βρετανική σημασία": ["UK"],
    "αυστραλία": ["Australia"],
    "γαλλία": ["France"],
}

# TODO: Ideally empty. Move things around.
other_tags = {
    "σπάνιο": ["rare"],
    "συνήθως": [],  # usually
    "εξαιρετικά": [],  # very; usu. εξαιρετικά σπάνιο: very rare
    "όπως ενδεικτικά": [],  # ~roughly means "for example..."
    "και τα παράγωγά του": [],  # ~roughly means related
    "αρνητικά": ["negative"],
    "συγγενικά": [],  # related
    "συνηρημένο": ["contracted"],  # "βροντάω (συνηρημένο βροντῶ)"
    "πριν από φωνήεν": ["before-vowel"],
    "μόνο πριν από το ουσιαστικό": ["before-noun"],
    "βιβλιογραφική παραπομπή": [],  # bibliographic reference
    "rōmaji": [],  # romaji is not valid
    # gia fors
    "για πράγματα": [],  # ~for things
    "για ζώα": [],  # ~for animals
    "για πρόσωπο": [],  # ~for people
    "για πρόσωπα": [],  # ~for people
    "για άνθρωπο": [],  # ~for people
    "για ανθρώπους": [],  # ~for people
    # POS
    "ουσιαστικό": ["noun"],
    "ελλειπτικό ουσιαστικό": ["noun", "defective"],
    "ρήμα": ["verb"],
    "ελλειπτικό ρήμα": ["verb", "defective"],
    "αποθετικό ρήμα": ["deponent", "verb"],
    "αποθετικό": ["deponent"],
    "απρόσωπο ρήμα": ["verb", "impersonal"],
    "απρόσωπο": ["impersonal"],
    "επίρρημα": ["adverb"],
    "τοπικό επίρρημα": ["adverb"],  # topical is not valid
    "χρονικό επίρρημα": ["adverb"],
    "τροπικό επίρρημα": ["adverb"],  # tropic/tropical are not valid
    "τροπικό": [],
    "ποσοτικό επίρρημα": ["adverb"],
    "επίθετο": ["adjective"],
    "επιτατικό επίθετο": ["adjective"],
    "σε επιθετική λειτουργία": ["adjective"],
    "λειτουργία": [],  # BAD PARSING of the above
    "επιθετική": ["adjective"],
    "ως επίθετο": ["adjective"],
    "επώνυμο": ["surname"],
    "επώνυμα": ["surname"],
    "επωνυμία": ["surname"],
    "θεωνύμιο": [],  # God's name
    "προσωπική αντωνυμία": ["pronoun"],  # really personal pronoun
    "αναφορική αντωνυμία": ["pronoun"],
    "δεικτική αντωνυμία": ["pronoun"],
    "οριστική αντωνυμία": ["pronoun", "definite"],
    "αόριστη αντωνυμία": ["pronoun", "indefinite"],
    "επιμεριστική αντωνυμία": ["pronoun", "distributive"],
    "ακρωνύμιο": ["acronym"],
    "αρκτικόλεξο": ["initialism"],
    "υποκοριστικό": ["diminutive"],
    "χαϊδευτικό": ["diminutive"],
    "σύνθετα": ["compound"],
    "συντομογραφία": ["abbreviation"],
    "γράμμα": ["letter"],
    "περιληπτικό": ["collective"],
    "οργανική": ["instrumental"],
    "γραφή": [],  # writing is not valid
    "προσφώνηση": [],  # really salutation
    #
    "άκλιτο": ["invariable"],
    "και άκλιτο": ["invariable"],
    "κτητική": ["possessive"],
    "μετρήσιμο": ["countable"],
    "μη μετρήσιμο": ["uncountable"],
    "μετρήσιμο και μη μετρήσιμο": ["countable", "uncountable"],
    "μεταβατικό και αμετάβατο": ["transitive", "intransitive"],
    "μεταβατικό & αμετάβατο": ["transitive", "intransitive"],
    "ουσιαστικοποιημένο": [],  # really nominalized
    "αστερισμός": [],  # constellation is not valid
    # Zones
    "τοπωνύμιο": ["toponymic"],  # toponym/placename are not valid
    "πατριδωνυμικό": ["demonym"],
    "πρώην ονομασία": [],  # naming is not valid (~city naming)
    # Styles / register
    "κυριολεκτικά": ["literally"],
    "μεταφορικά": ["figuratively"],  # or metaphorically
    "κυριολεκτικά και μεταφορικά": ["literally", "figuratively"],
    "συνεκδοχικά": ["figuratively"],
    "καταχρηστικά": ["figuratively"],
    "κατ’ επέκταση": ["broadly"],
    "κατ' επέκταση": ["broadly"],
    "ειδικότερα": ["especially"],
    "γενικότερα": ["general"],  # generally is not valid
    "αρχική σημασία": [],  # originally is not valid
    #
    "λόγιο": ["formal"],
    "επίσημο": ["formal"],
    "λογοτεχνικό": ["literary"],
    "ποιητικός τύπος": ["poetic"],
    "παρωχημένο": ["dated"],
    "αρχαιοπρεπές": ["archaic"],
    "απαρχαιωμένο": ["obsolete"],
    "καθομιλουμένη": ["colloquial"],
    "χυδαίο": ["vulgar"],
    "λαϊκό": ["vulgar"],
    "λαϊκότροπο": ["vulgar"],
    "αργκό": ["slang"],  # argot is not valid
    "διαδικτυακή αργκό": ["internet-slang"],
    "στρατιωτική αργκό": ["slang"],  # military-slang is not valid
    "οικείο": ["familiar"],
    "προφορικό": ["familiar"],  # oral is not valid
    "μειωτικό": ["offensive"],
    "υβριστικό": ["offensive"],
    "σκωπτικό": ["offensive"],
    "κακόσημο": ["disapproving"],
    "νεολογισμός": ["neologism"],
    "ιδιωματικό": ["idiomatic"],
    "και σήμερα σε χρήση ως ιδιωματικό": ["idiomatic"],
    "ιδιωματισμός": ["idiomatic"],  # idiom is not valid
    "ανεπίσημο": ["informal"],
    "ειρωνικό": ["ironic"],
    # Greeks
    "καθαρεύουσα": ["Katharevousa"],
    "καθαρεύουσα (κατά την αρχαία κλίση)": ["Katharevousa"],
    "ελληνιστική κοινή": ["Koine"],
    "δημοτική": ["Demotic"],
    "ελληνιστική σημασία": ["Hellenistic"],
    "κρητικά": ["Cretan"],
    "κυπριακά": ["Cypriot"],
    "ιωνικός τύπος": ["Ionic"],
    "στην ιωνική διάλεκτο": ["Ionic"],
    "επικός τύπος": ["Epic"],
    "δωρικός τύπος": ["Doric"],
    "αιολικός τύπος": ["Aeolian"],
    "αττικός τύπος": ["Attic"],
}

topic_map: dict[str, list[str]] = {
    "επάγγελμα": ["business"],  # really profession
    "οικονομία": ["business"],  # really economy
    "λογιστική": ["accounting"],
    "στατιστική": ["statistics"],
    "βιολογία": ["biology"],
    "βοτανική": ["botany"],
    "ιατρική": ["medicine"],
    "φαρμακευτική": ["medicine"],  # pharmaceutical is not valid
    "ανατομία": ["anatomy"],
    "φυσιολογία": ["physiology"],
    "χημεία": ["chemistry"],
    "βιοχημεία": ["biochemistry"],
    "θρησκεία": ["religion"],
    "χριστιανισμός": ["Christianity"],
    "ισλαμισμός": ["Islam"],
    "μυθολογία": ["mythology"],
    "ελληνική μυθολογία": ["mythology", "Greek"],
    "σκανδιναβική μυθολογία": ["mythology", "Scandinavian"],
    "γραμματική": ["grammar"],
    "ιστορία": ["history"],
    "μουσική": ["music"],
    "μουσικό όργανο": ["music"],  # music instrument
    "εργαλείο": ["tools"],
    "μαθηματικά": ["mathematics"],
    "πολιτική": ["politics"],
    "αθλητισμός": ["athletics"],
    "τεχνολογία": ["technology"],
    "φυσική": ["physics"],
    "ζωολογία": ["zoology"],
    "ιχθυολογία": ["ichthyology"],
    "γεωγραφία": ["geography"],
    "γεωμετρία": ["geometry"],
    "γεωλογία": ["geology"],
    "γεωπονία": ["agriculture"],  # agronomy is not valid
    "φιλολογία": ["philology"],
    "γλώσσα": ["language"],
    "γλωσσολογία": ["linguistics"],
    "φωνητική": ["phonetics"],
    "αστρονομία": ["astronomy"],
    "ηλεκτρολογία": ["electricity"],  # branch of physics
    "ηλεκτρονική": ["electronics"],
    "τηλεπικοινωνίες": ["telecommunications"],
    "αντικειμενοστρεφής προγραμματισμός": ["programming"],  # OOP
    "προγραμματισμός": ["programming"],
    "λογισμικό": ["software"],
    "πληροφορική": ["computing"],
    "επιστήμη υπολογιστών": ["computing"],  # computer science
    "υλικό υπολογιστή": ["computing"],  # computer material
    "βάσεις δεδομένων": ["computing"],  # database is not valid
    "δίκτυο υπολογιστών": ["computing"],  # network is not valid
    "διαδίκτυο": ["Internet"],
    "φιλοσοφία": ["philosophy"],
    "ψυχολογία": ["psychology"],
    "ψυχιατρική": ["psychiatry"],
    "αρχιτεκτονική": ["architecture"],
    "οικοδομική": ["construction"],
    "μετεωρολογία": ["meteorology"],
    "ενδυμασία": ["clothing"],
    "υπόδηση": ["clothing"],  # really footwear
    "ύφασμα": ["clothing"],  # really fabric/textile
    "αρχαιολογία": ["archeology"],
    "ορυκτολογία": ["mineralogy"],
    "εκπαίδευση": ["education"],
    "τέχνη": ["art"],
    "γλυπτική": ["art"],  # sculpting is not valid
    "ζωγραφική": ["art"],  # painting is not valid
    "λογοτεχνία": ["literature"],
    "θέατρο": ["theater"],
    "χορός": ["dance"],
    "φωτογραφία": ["photography"],
    "κινηματογράφος": ["film"],
    "λογική": ["logic"],
    "επιστήμη": ["science"],
    "μηχανολογία": ["mechanical-engineering"],
    "τυπογραφία": ["typography"],
    "επιδημιολογία": ["epidemiology"],
    "οικολογία": ["ecology"],
    "κοινωνιολογία": ["sociology"],
    "ανθρώπινο σώμα": ["body"],
    "λαογραφία": ["folklore"],
    "μέσο μεταφορών": ["transport"],
    "αστρολογία": ["astrology"],
    "εραλδική": ["heraldry"],
    "ταξινομία": ["taxonomy"],
    "μεταλλουργία": ["metallurgy"],
    #
    "εθνωνύμιο": ["countries"],  # ethnonym is not valid
    "εθνικό όνομα": ["countries"],  # ethnonym is not valid
    "χώρα": ["countries"],
    "πόλη": ["cities"],
    "χρώμα": ["color"],
    #
    "μονάδα μέτρησης": ["units-of-measure"],
    "μετρική": ["units-of-measure"],
    "παραμύθι": ["fantasy"],  # tale/fairy-tale are not valid
    "χαρτοπαίγνιο": ["card-games"],
    "παιχνίδι": ["games"],
    "σκάκι": ["board-games"],  # chess
    "κεραμική": ["ceramics"],
    "άνεμος": ["weather"],  # wind is not valid
    #
    "αξίωμα": [],  # office/rank is not valid
    "οικογένεια": [],  # family is not valid
    "νόμισμα": [],  # coin/currency are not valid
    # Time
    "ημέρα": ["time"],  # day is not valid
    "μήνας": ["time"],  # month is not valid
    # Food
    "τρόφιμο": ["food"],
    "φαγητά": ["food"],
    "ποτό": ["food"],  # drink is not valid
    "γαστρονομία": ["food"],  # gastronomy is not valid
    "φρούτο": ["food"],  # fruit is not valid
    "όσπριο": ["food"],  # legume is not valid
    "γλυκό": ["food"],  # sweet is not valid
    "τυρί": ["food"],  # cheese is not valid
    "λαχανικό": ["vegetable"],
    "αλιεία": ["fishing"],
    "ψάρι": ["fish"],
    "μαλάκιο": ["fish"],  # mollusc is not valid
    "ελληνική ποικιλία αμπέλου": ["wine"],
    "μαγειρική": ["cooking"],
    "κουζινικά": ["cooking"],  # kitchen is not valid
    #
    "δέντρο": [],  # tree is not valid
    "φυτό": [],  # really plant
    "λουλούδι": [],  # really flower
    "ζώο": [],  # animal is not valid
    "θηλαστικό ζώο": ["mammals"],
    "πτηνό": [],  # really bird
    "ερπετό": [],  # reptile is not valid
    "φίδι": ["snakes"],
    "εντομολογία": ["entomology"],
    "έντομο": ["insects"],
    #
    "στρατιωτικός βαθμός": ["military"],
    "οπλισμός": ["weapon"],
    #
    "ναυτικός όρος": ["nautical"],
    "ναυπηγικός όρος": ["nautical"],
    "νομικός όρος": ["law"],
    "στρατιωτικός όρος": ["military"],
    "αεροπορικός όρος": ["aerospace"],
    "εκκλησιαστικός όρος": ["religion"],
}

# TODO:
# This booms somewhere in the parsing
# (να, ας, αν, ίσως κλπ) γ' ενικό υποτακτικής αορίστου του ρήματος εντάσσω
#
# TO FIX LATER
DONTCARES = {
    ":": [],
    "να": [],
    "ας": [],
    "αν": [],
    "ίσως κλπ": [],
    "οι δεύτεροι άτονοι τύποι είναι εγκλιτικοί": [],
    "επική κλίση οι διαφορετικοί τύποι, με έντονα γράμματα": [],
    "ελληνιστική κοινή (αρχαία κλίση)δε μαρτυρείται δυϊκός αριθμός": [],
    "όταν ακολουθεί όνομα, η οξεία γίνεται βαρεία . • σημειώνεται η προσωδία του α εκεί που είναι μακρό": [],
    "δωρική κλίση οι διαφορετικοί τύποι, με έντονα γράμματα": [],
    "χωρίς άρθρο, συγκριτικός βαθμός με το άρθρο, σχετικός υπερθετικός βαθμός": [],
    "κλιτικοί τύποι από την αρχαία κλίση": [],  # from βπ template for grc
    "παθητικού": [],  # BAD PARSING
    "παρακειμένου": [],  # BAD PARSING
    "σημειώνεται η προσωδία του α εκεί που είναι μακρό": [],
    "1η συζυγία - μεσοπαθητικός ενεστώτας (αποθετικό ρήμα)": [],
    "κλίση -ος, -α, -ον & σπανιότερα θηλυκό σε -η": [],
    "χωρίς άρθρο": [],
    "χωρίς": [],
    "κλίση χωρίς άρθρο": [],
    "χωρίς παραθετικά": [],
    "και": [],
    "του": [],
    "δείτε": [],
    "δείτε την έκφραση": [],
    "όπως": [],
    "στο": [],
    "τη&nbsp;λέξη": [],
    "τις&nbsp;λέξεις": [],
    "με": [],
    "σε": [],
    "ή": [],
    "η": [],
    "το": [],
    "+ να": [],
    "+ θα": [],
    # Bad page: https://el.wiktionary.org/wiki/enketi
    "ρήμα {{{1}}}i": ["verb"],
    #
    # BAD TABLE PARSING
    #
    # https://el.wiktionary.org/wiki/ὁ
    "γένη πτώσεις": [],
    "τῶ": [],
    "τώς": [],
    "τάν (ᾱ)": [],
    # https://el.wiktionary.org/wiki/με
    "πρόσωπα πτώσεις": [],
}

tag_map: dict[str, list[str]] = {
    **DONTCARES,
    **verb_table_tags_base,
    **english_tables_tags,
    **esperanto_tables_tags,
    **turkish_tables_tags,
    **romanian_tables_tags,
    **german_tables_tags,
    **spanish_tables_tags,
    **polish_tables_tags,
    **russian_tables_tags,
    **french_tags,
    **ancient_greek_tables_tags,
    **ancient_greek_tags,
    **transliteration_tags,
    **zones_tags,
    **other_tags,
    # Gender
    "αρσενικό": ["masculine"],
    "θηλυκό": ["feminine"],
    "ουδέτερο": ["neuter"],
    "αρσενικό & θηλυκό": ["masculine", "feminine"],
    "αρσενικό ή θηλυκό": ["masculine", "feminine"],
    "αρσενικό ή ουδέτερο": ["masculine", "neuter"],
    "αρσενικό θηλυκό ουδέτερο": ["masculine", "feminine", "neuter"],
    "ουδέτερο στον ενικό": [],  # neuter-when-singular not valid
    "ουδέτερο στον πληθυντικό": [],  # idem, not valid
    "αρσενικό στον πληθυντικό": [],  # masculine-when-plural not valid
    "θηλυκό στον ενικό": [],  # feminine-when-singular not valid
    # Number
    "ενικός": ["singular"],
    "ενικός (singular)": ["singular"],
    "πληθυντικός": ["plural"],
    "πληθυντικός (plural)": ["plural"],
    "μόνο στον ενικό": ["singular-only"],
    "μόνο στον πληθυντικό": ["plural-only"],
    "ο αρχαίος τύπος, μόνο στον πληθυντικό": ["plural-only"],
    "μόνο πληθυντικός": ["plural-only"],
    "μόνο ενικός": ["singular-only"],
    "στον ενικό": ["singular"],
    "στον πληθυντικό": ["plural"],
    "συνήθως στον πληθυντικό": ["plural-normally"],
    "συνήθως στον ενικό": ["singular-normally"],
    "συνήθως ενικός": ["singular-normally"],
    # Case
    "ονομαστική": ["nominative"],
    "γενική": ["genitive"],
    "γενική:": ["genitive"],
    "αιτιατική": ["accusative"],
    "κλητική": ["vocative"],
    "ονομαστική αιτιατική": ["nominative", "accusative"],
    # Others
    "αόριστο": ["indefinite"],
    "οριστικό": ["definite"],
}


Taggable = WordEntry | Form | Sense | Linkage
"""An object with raw_tags, tags and topics attributes."""


def translate_raw_tags(taggable: Taggable) -> None:
    """Translate raw_tags to tags/topics, preserving raw_tags.

    This is a bit different from other extractors in order to type check.

    INVARIANT: taggable's tags/topics should **remain** unique.
    If they were not unique before, there are no guarantees.

    Use:
    # Apply to an entire WordEntry
    >>> translate_raw_tags(word_entry)

    # Apply to each Form in a WordEntry
    >>> for form in word_entry.forms:
    ...     translate_raw_tags(form)

    # Apply to a list of Form objects
    >>> for form in form_list:
    ...     translate_raw_tags(form)
    """
    for raw_tag in taggable.raw_tags:
        clean_raw_tag = raw_tag.replace("\n", " ").lower()
        tags = tag_map.get(clean_raw_tag)
        if tags is not None:
            for tag in tags:
                if tag not in taggable.tags:
                    taggable.tags.append(tag)
        else:
            topics = topic_map.get(clean_raw_tag)
            if topics is not None:
                for topic in topics:
                    if topic not in taggable.topics:
                        taggable.topics.append(topic)
