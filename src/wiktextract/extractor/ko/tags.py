from .models import WordEntry

# https://ko.wiktionary.org/wiki/모듈:labels/data/topical
# https://ko.wiktionary.org/wiki/모듈:labels/data
GLOSS_TAGS = {
    "인명": "name",
    "고어": "archaic",
    "구식": "archaic",
    # "대명동사": "",
    # "말고름": "",
    "비유": "metaphoric",
    "사어": "obsolete",  # dead language
    "유아어": "baby-talk",
    "자동사": "intransitive",
    "직역": "literally",
    "타동사": "transitive",
}

SOUND_TAGS = {
    # 틀:ko-IPA
    "Revised Romanization": ["revised", "romanization"],
    "Revised Romanization (translit.)": [
        "revised",
        "romanization",
        "transliteration",
    ],
    "McCune-Reischauer": "McCune-Reischauer",
    "Yale Romanization": ["Yale", "romanization"],
}

TAGS = {**GLOSS_TAGS, **SOUND_TAGS}

TOPICS = {
    "금융": "finance",
    "광고": "advertising",
    "군사": "military",
    "어류": "fish",
    "물리": "physics",
    "법률": "law",
    "식물": "botany",
    "역사": "history",
    "의류": "clothing",
    "의학": "medicine",
    "전기": "electricity",
    # "조류": "birds",
    "지리": "geography",
    "프로그래밍": "programming",
    "컴퓨터": "computer",
    "해부학": "anatomy",
    "정치": "politics",
    "종교": "religion",
    "가톨릭": "Catholicism",
    "축구": "football",
    # "체육": "physical-education",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag in TOPICS:
            data.topics.append(TOPICS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
