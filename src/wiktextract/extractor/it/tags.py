from .models import WordEntry

TABLE_TAGS = {
    # https://it.wiktionary.org/wiki/Template:It-decl-agg4
    "singolare": "singular",
    "plurale": "plural",
    "positivo": "positive",
    "superlativo assoluto": ["absolute", "superlative"],
    "maschile": "masculine",
    "femminile": "feminine",
    # https://it.wiktionary.org/wiki/Template:It-decl-agg2
    "m e f": ["masculine", "feminine"],
}

FORM_LINE_TEMPLATE_TAGS = {
    # https://it.wiktionary.org/wiki/Template:A_cmp
    "comparativo": "comparative",
    "superlativo": "superlative",
}


TAGS = {**TABLE_TAGS, **FORM_LINE_TEMPLATE_TAGS}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
