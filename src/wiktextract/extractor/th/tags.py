from .models import WordEntry

EXAMPLE_TAGS = {
    # แม่แบบ:zh-x, มอดูล:zh-usex/data
    "MSC": "Modern Standard Chinese",
    "Pinyin": "Pinyin",
    "trad.": "Traditional Chinese",
    "simp.": "Simplified Chinese",
}

TRANSLATION_TAGS = {
    # แม่แบบ:t
    # https://th.wiktionary.org/wiki/มอดูล:gender_and_number/data
    "ญ.": "feminine",
    "ช.": "masculine",
    "ก.": "neuter",
    "ร.": "common",
    "ชีว.": "animate",
    "อชีว.": "inanimate",
    "สัต.": "animal-not-person",
    "บุค.": "personal",
    "อบุค.": "impersonal",
    "เอก.": "singular",
    "ทวิ.": "dual",
    "พหู.": "plural",
    "ไม่สมบูรณ์": "imperfective",
    "สมบูรณ์": "perfective",
}


TAGS = {**EXAMPLE_TAGS, **TRANSLATION_TAGS}


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
