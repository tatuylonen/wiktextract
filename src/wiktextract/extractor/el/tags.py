from wiktextract.extractor.el.models import Form, WordEntry
from wiktextract.tags import uppercase_tags, valid_tags

# ======
#  TAGS
# ======

# The strings in lists on the right-hand side here should be *shared* tags
# between different edition implementations. `valid_tags` is a dictionary
# of these tags (and can be expanded if necessary, although it is unlikely
# to be needed anymore because we have a lot of them), with some metadata
# in the value used in the English mainline extractor.

# Just as an example, this file is basically the simple implementation from
# the Simple English extractor, which uses basically the same tags and
# mappings as the mainline English extractor (which makes things simple).

# Otherwise, the implementation of tags is a translation effort: when this
# edition of Wiktionary says 'x', what tags does that refer to?


# Tags used for modern Greek verb tables.
#
# Includes other verb related tags that may appear in headers etc.
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
    "Α' πρόσωπο": ["first-person"],
    "Β' πρόσωπο": ["second-person"],
    "Γ' πρόσωπο": ["third-person"],
    "α' πρόσωπο": ["first-person"],
    "β' πρόσωπο": ["second-person"],
    "γ' πρόσωπο": ["third-person"],
    "ενικός": ["singular"],
    "πληθυντικός": ["plural"],
    "εγώ": ["first-person", "singular"],
    "εσύ": ["second-person", "singular"],
    "αυτός": ["third-person", "singular"],
    "εμείς": ["first-person", "plural"],
    "εσείς": ["second-person", "plural"],
    "αυτοί": ["third-person", "plural"],
    "(εσύ)": ["second-person", "singular"],
    "(εσείς)": ["second-person", "plural"],
    # Aspect groups
    # These following three are from:
    # Greek: An Essential Grammar (Routledge Essential Grammars)
    "εξακολουθητικοί χρόνοι": ["imperfective"],
    "συνοπτικοί χρόνοι": ["perfective"],
    "συντελεσμένοι χρόνοι": ["perfect"],
    "συντελεσμένοι χρόνοι (β΄ τύποι)": ["perfect", "type-b"],
    "συντελεσμένοι χρόνοι β΄ (μεταβατικοί)": [
        "perfect",
        "type-b",
        "transitive",
    ],
    "συντελεσμένοι χρόνοι β΄ (αμετάβατοι)": [
        "perfect",
        "type-b",
        "intransitive",
    ],
    # Basic tenses / aspects
    "ενεστώτας": ["present"],
    "παρατατικός": ["imperfect"],
    "αόρ": ["aorist"],
    "αόριστος": ["aorist"],
    # Forms / moods
    "υποτακτική": ["subjunctive"],
    "προστακτική": ["imperative"],
    "μετοχή": ["participle"],
    "μτχ.": ["participle"],
    "απαρέμφατο": ["infinitive"],
    # Future & perfect subtypes
    "εξακολουθητικός μέλλοντας": ["future", "imperfect"],
    "εξ. μέλλ.": ["future", "imperfect"],
    "συνοπτ. μέλλ.": ["future"],
    "στιγμιαίος μέλλοντας": ["future"],  # στιγμιαίος = συνοπτικός
    "στ.μέλλ": ["future"],
    "συντελ. μέλλ.": ["future", "perfect"],
    "συντελεσμένος μέλλοντας α'": ["future", "perfect", "type-a"],
    "παρακείμενος": ["present", "perfect"],
    "παρακείμενος α'": ["present", "perfect", "type-a"],
    "υπερσυντέλικος": ["past", "perfect"],
    "υπερσυντέλικος α'": ["past", "perfect", "type-a"],
    # Voices
    "παθητική φωνή": ["passive"],
    "παθ.φωνή": ["passive"],
    # Others
    "προσωπικές εγκλίσεις": ["personal"],  # ["personal-moods"],
    "απρόσωπες εγκλίσεις": ["impersonal"],  # ["impersonal-moods"],
    "μονολεκτικοί χρόνοι": [],  # ["simple-tenses"], # no   να/θα/έχει
    "περιφραστικοί χρόνοι": [],  # ["periphrastic"], # with να/θα/έχει
    "απαρέμφατο (αόριστος)": ["infinitive", "aorist"],
    "μετοχή (ενεστώτας)": ["participle", "present"],
}

base_tag_map: dict[str, list[str]] = {
    **verb_table_tags_base,
    "ονομαστική": ["nominative"],
    "γενική": ["genitive"],
    "αιτιατική": ["accusative"],
    "κλητική": ["vocative"],
    "αρσενικό": ["masculine"],
    "θηλυκό": ["feminine"],
    "ουδέτερο": ["neuter"],
    # ------ Ancient Greek --------------------------
    "δοτική": ["dative"],
    "αφαιρετική": ["ablative"],
    "τοπική": ["locative"],
    # ------ English --------------------------------
    "no-gloss": ["no-gloss"],
    "comparative": ["comparative"],
    "Comparative": ["comparative"],
    "determiner": ["determiner"],
    "Negative": ["negative"],
    "Past": ["past"],
    "Past participle": ["past", "participle"],
    "Past tense": ["past"],
    "Plain form": ["canonical"],
    "Plain present": ["present"],
    "plural": ["plural"],
    "Plural": ["plural"],
    "Positive": ["positive"],
    "Present": ["present"],
    "Present participle": ["present", "participle"],
    "Proper noun": ["proper-noun"],
    "singular": ["singular"],
    "superlative": ["superlative"],
    "Superlative": ["superlative"],
    "Third person singular": ["third-person", "singular"],
    "Third-person singular": ["third-person", "singular"],
    "stressed": ["stressed"],
    "unstressed": ["unstressed"],
    "UK": ["UK"],
    "US": ["US"],
    "United Kingdom": ["UK"],
    "United States": ["US"],
    "before a vowel": ["before-vowel"],
    "before a consonant": ["before-consonant"],
    "CA": ["Canada"],
    "AU": ["Australia"],
    "Australian": ["Australia"],
    "California": ["California"],
    "Canadian": ["Canada"],
    "CA synth": [],
    "GB": ["UK"],
    "India": ["India"],
    "Indian English": ["Indian-English"],
    "Kenya": ["Kenya"],
    "Limbu": ["Limbu"],
    "Massachusetts": ["Massachusetts"],
    "Mid-Atlantic": ["Mid-Atlantic"],
    "New York accent": ["New-York"],
    "Northen England": ["Northern-England"],
    "NZ": ["New-Zealand"],
    "Rhode Island": ["Rhode-Island"],
    "Southern England": ["Southern-England"],
    "uk": ["UK"],
    "Uk": ["UK"],
    "UK male": ["UK"],
    "US female": ["US"],
    "US Inland North": ["Inland-Northern-American"],
    "US-Inland North": ["Inland-Northern-American"],
    "American": ["US"],
    "Audio US": ["US"],
}


tag_map = {}

# uppercase_tags are specific tags with uppercase names that are for stuff
# like locations and dialect and language names.
for k in uppercase_tags:
    if k not in base_tag_map:
        tag_map[k] = [k.replace(" ", "-")]

Taggable = WordEntry | Form
"""An object with raw_tags and tags attributes."""


def translate_raw_tags(taggable: Taggable) -> None:
    """Translate raw_tags to tags, preserving raw_tags.

    This is a bit different from other extractors in order to type check.

    INVARIANT: taggable's tags should **remain** unique.
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
        tags = base_tag_map.get(clean_raw_tag)
        if tags is not None:
            for tag in tags:
                if tag not in taggable.tags:
                    taggable.tags.append(tag)
