from .models import BaseModel

GLOSS_TAGS = {
    "mecaz": "metaphoric",  # "Şablon:mecaz"
    "bazen": "sometimes",
    "özellikle": "especially",
    "ender": "rare",
    "kısa": "short-form",
}

POS_HEADER_TAGS = {
    # Şablon:tr-ad
    "belirtme hâli": "accusative",
    "çoğulu": "plural",
    # Şablon:en-ad
    "üçüncü tekil kişi geniş zaman": ["third-person", "singular", "present"],
    "şimdiki zaman": "present",
    "geçmiş zaman ve yakın geçmiş zaman": "past",
    # Şablon:de-ad
    "tamlayan hâli": "genitive",
    "dişil": "feminine",
    "d": "feminine",
    "e": "masculine",
    "eril": "masculine",
    "sahiplik şekli": "possessive",  # Şablon:sahiplik
}

TRANSLATION_TAGS = {
    # Modül:cinsiyet_ve_numara
    "n": "neutral",
    "g": "general",
    "anim": "animate",
    "cansız": "inanimate",
    "pers": "personal",
    "npers": "impersonal",
    "te": "singular",
    "ik": "dual",
    "ç": "plural",
    "impf": "imperfective",
    "pf": "perfective",
}

LINKAGE_TAGS = {
    "eskimiş": "obsolete",
}

TABLE_TAGS = {
    # Şablon:tr-ad-tablo
    "tekil": "singular",
    "çoğul": "plural",
    "yalın": "nominative",
    "belirtme": "accusative",
    "yönelme": "dative",
    "bulunma": "locative",
    "ayrılma": "ablative",
    "tamlayan": "genitive",
    "iyelik": "possessive",
    "1. tekil": ["first-person", "singular"],
    "2. tekil": ["second-person", "singular"],
    "3. tekil": ["third-person", "singular"],
    "1. çoğul": ["first-person", "plural"],
    "2. çoğul": ["second-person", "plural"],
    "3. çoğul": ["third-person", "plural"],
    # Şablon:tr-eylem-tablo
    "olumlu çekimler": "positive",
    "belirli geçmiş": ["definite", "past"],
    "belirsiz geçmiş": ["indefinite", "past"],
    "şimdiki": "present",
    "gelecek": "future",
    # "basit": "simple",
    # "hikaye": "",
    # "rivayet": "",
    "şart": "conditional",
    "gereklilik": "necessitative",
    "olumsuz çekimler": "negative",
}


TAGS = {
    **GLOSS_TAGS,
    **POS_HEADER_TAGS,
    **TRANSLATION_TAGS,
    **LINKAGE_TAGS,
    **TABLE_TAGS,
}

# https://tr.wiktionary.org/wiki/Modül:temalar/veri/konu
TOPICS = {
    "anatomi": "anatomy",
    "bilişim": "informatics",
    "diller": "language",
    "eğitim": "education",
}


def translate_raw_tags(data: BaseModel) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str) and tr_tag not in data.tags:
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                for t in tr_tag:
                    if t not in data.tags:
                        data.tags.append(t)
        elif raw_tag in TOPICS and hasattr(data, "topics"):
            topic = TOPICS[raw_tag]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, list):
                data.topics.extend(topic)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
