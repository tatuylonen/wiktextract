from .models import WordEntry

TAGS = {
    "男性": "masculine",
    "女性": "feminine",
    "通性": "common",
    "中性": "neuter",
    "単数": "singular",
    "複数": "plural",
    "不変": "invariable",
    "男性複数": ["masculine", "plural"],
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            add_tag(raw_tag, data)
        elif "/" in raw_tag:
            for r_tag in raw_tag.split("/"):
                r_tag = r_tag.strip()
                if r_tag in TAGS:
                    add_tag(r_tag, data)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags


def add_tag(raw_tag: str, data: WordEntry) -> None:
    tr_tag = TAGS[raw_tag]
    if isinstance(tr_tag, str) and tr_tag not in data.tags:
        data.tags.append(TAGS[raw_tag])
    elif isinstance(tr_tag, list):
        for t_tag in tr_tag:
            if t_tag not in data.tags:
                data.tags.append(t_tag)
