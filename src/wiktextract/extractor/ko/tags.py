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
    "드물게": "rare",
    "원래의 의미": "naturally",
    "문학적": "literary",
    "해학적": "humorous",
    "완곡적": "euphemistic",
    "가산": "countable",
    "불가산": "uncountable",
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
    "표준어/서울": ["SK-Standard", "Seoul"],
    # 틀:ja-pron
    "도쿄": "Tokyo",
    # 틀:발음 듣기, 틀:IPA
    "영국": "UK",
    "미국": "US",
    "영": "UK",
    "미": "US",
    "표준": "standard",
    "남부": "South",
    "북부": "North",
    "고대": "archaic",
    "동부": "East",
    "서부": "West",
    "포르투갈": "Portugal",
    "이집트": "Egypt",
    "시리아": "Syria",
    "브라질": "Brazil",
    "독일": "Germany",
    "현대": "modern",
    "캐나다": "Canada",
    "하노이": "Hanoi",
    "브라질 남부": "Southern-Brazil",
    "벨기에": "Belgium",
    "이란": "Iran",
    "파리": "Paris",
    "모로코": "Morocco",
    "베를린": "Berlin",
    "비격식체": "informal",
    "민난어 장저우": ["Min-Nan", "Zhangzhou"],
}

HEADER_TAGS = {
    # 틀:한국어_동사
    "활용": "infinitive",
    "연결형": "sequential",
    "명사형": "noun",
    "사동사": "causative",
    "한글": "hangeul",
    "한자": "hanja",
    # 모듈:Jpan-headword
    "연용형": "stem",
    "과거형": "past",
    "5단 활용": "godan",
    "1단 활용": "ichidan",
    "サ행 변격": "suru",
    "kuru": "kuru",
}

# also in linkage lists
TRANSLATION_TAGS = {
    "남성": "masculine",
    "여성": "feminine",
    "라틴": "Latin",
    "중성": "neuter",
    "간체": "Simplified-Chinese",
    "번체": "Traditional-Chinese",
    "번체자": "Traditional-Chinese",
    "오스트리아": "Austria",
    "표준어": "standard",
    "히브리 문자": ["Hebrew", "letter"],
    "아랍 문자": ["Arabic", "letter"],
    "복수형": "plural",
    "단수": "singular",
    "복수": "plural",
    "불완료체": "imperfect",
    "완료체": "completive",
    "양성": "masculine",
    "바이에른 방언": ["Bavarian", "dialectal"],
    "광둥어": "Cantonese",
    "오스트레일리아": "Australia",
    "글라골 문자": ["Glagolitic", "letter"],
    "속어": "slang",
    "멕시코 속어": ["Mexico", "slang"],
    "에스파냐": "Spain",
    "가타카나": "katakana",
    "고어": "archaic",
    "쯔놈": "Chu-Nom",
    "형용사": "adjective",
    "사투리": "dialectal",
    "약자": "abbreviation",
    "동사": "verb",
    "드문 단어": "rare",
}

TAGS = {
    **GLOSS_TAGS,
    **SOUND_TAGS,
    **HEADER_TAGS,
    **TRANSLATION_TAGS,
    # Template:zh-forms
    "정체": "Traditional-Chinese",
    "간체": "Simplified-Chinese",
    # Template:zh-x
    "대만 관화": "Taiwanese-Mandarin",
    "표준 중국어": "Standard-Chinese",
    "한어병음": "Pinyin",
    "광저우 광둥어": "Guangzhou-Cantonese",
    "월병": "Jyutping",
}

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
        elif hasattr(data, "topics") and raw_tag in TOPICS:
            data.topics.append(TOPICS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
