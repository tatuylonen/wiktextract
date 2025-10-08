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

base_tag_map: dict[str, list[str]] = {
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
