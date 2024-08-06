# List of templates
# https://ja.wiktionary.org/wiki/テンプレートの一覧#品詞表記
POS_DATA = {
    "名詞": {"pos": "noun"},
    "数詞": {"pos": "num"},
    "固有名詞": {"pos": "name"},
    "代名詞": {"pos": "pron"},
    "動詞": {"pos": "verb"},
    "自動詞": {"pos": "verb", "tags": ["intransitive"]},
    "他動詞": {"pos": "verb", "tags": ["transitive"]},
    "助動詞": {"pos": "verb", "tags": ["auxiliary"]},
    "副詞": {"pos": "adv"},
    "形容詞": {"pos": "adj"},
    "形容動詞": {"pos": "adj_noun"},
    "助詞": {"pos": "particle"},
    "冠詞": {"pos": "article"},
    "前置詞": {"pos": "prep"},
    "後置詞": {"pos": "postp"},
    "間投詞": {"pos": "intj"},
    "分詞": {"pos": "verb", "tags": ["participle"]},
    "過去分詞": {"pos": "verb", "tags": ["participle", "past"]},
    "現在分詞": {"pos": "verb", "tags": ["participle", "present"]},
    "接続詞": {"pos": "conj"},
    "類別詞": {"pos": "classifier"},
    "接頭辞": {"pos": "prefix", "tags": ["morpheme"]},
    "接尾辞": {"pos": "suffix", "tags": ["morpheme"]},
    # "小詞"
    # "修飾詞"
    # "疑問詞"
    "和語の漢字表記": {"pos": "unknown", "tags": ["kanji"]},
    "成句": {"pos": "phrase", "tags": ["idiomatic"]},
    "縮約形": {"pos": "contraction"},
    "略語": {"pos": "abbrev", "tags": ["abbreviation"]},
    "頭字語": {"pos": "abbrev", "tags": ["abbreviation"]},
    "ことわざ": {"pos": "proverb"},
}

LINKAGES = {
    "類義語": "synonyms",
    "対義語": "antonyms",
    "上位語": "hypernyms",
    "下位語": "hyponyms",
    "全体語": "holonyms",
    "部分語": "meronyms",
    "複合語": "derived",
    "派生語": "derived",
    "縮約形": "contraction",
    "略語": "abbreviations",
    "関連語": "related",
    "同族語": "coordinate_terms",
    "熟語": "proverbs",
    "成句": "phrases",
    "連語": "collocations",
}
