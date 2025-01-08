from .models import WordEntry

EXAMPLE_TAGS = {
    # แม่แบบ:zh-x, มอดูล:zh-usex/data
    "MSC": "Modern Standard Chinese",
    "Pinyin": "Pinyin",
    "trad.": "Traditional Chinese",
    "simp.": "Simplified Chinese",
}


TAGS = {**EXAMPLE_TAGS}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
