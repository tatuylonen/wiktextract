from wiktextract.tags import valid_tags

simple_tag_map: dict[str, list[str]] = {
    "no-gloss": ["no-gloss"],
}



# Check validity
# valid_tags is from the lower level, originally created for the English
# extractor but also applicable to other extractors: these are the tags
# that should be used for tagging. Can be added to when needed, but
# often there's already an equivalent tag with a slightly different name.
for tags in simple_tag_map.values():
    for tag in tags:
        if tag.islower() and tag.isalpha() and tag not in valid_tags:
            assert False, f"Invalid tag in simple_tag_map: {tag}"
