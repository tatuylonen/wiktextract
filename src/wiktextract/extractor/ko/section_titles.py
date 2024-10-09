POS_DATA = {
    "명사": {"pos": "noun"},
    "형용사": {"pos": "adj"},
    "대명사": {"pos": "pron"},
    "수사": {"pos": "num"},
    "동사": {"pos": "verb"},
    "관용구": {"pos": "phrase", "tags": ["idiomatic"]},
    "기호": {"pos": "symbol"},
    "접미사": {"pos": "suffix", "tags": ["morpheme"]},
    "접두사": {"pos": "prefix", "tags": ["morpheme"]},
    "의미": {"pos": "unknown"},
    "타동사": {"pos": "verb", "tags": ["transitive"]},
    "종별사": {"pos": "counter"},
}

LINKAGE_SECTIONS = {
    "속담": "proverbs",
    "합성어": "derived",
    "파생어": "derived",
    "관련 어휘": "related",
    "유의어": "synonyms",
    "반의어": "antonyms",
}
