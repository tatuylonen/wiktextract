from wiktextract.tags import uppercase_tags, valid_tags

simple_tag_map: dict[str, list[str]] = {
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
    "CA synth": [""],
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



# Check validity
for tags in simple_tag_map.values():
    for tag in tags:
        if tag.islower() and tag.isalpha() and tag not in valid_tags:
            assert False, f"Invalid tag in simple_tag_map: {tag}"

for k in uppercase_tags:
    if k not in simple_tag_map:
        simple_tag_map[k] = [ k.replace(" ", "-") ]
