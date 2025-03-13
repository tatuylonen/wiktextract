from .models import BaseModel

GLOSS_TAGS = {
    "mecaz": "metaphoric",  # "Şablon:mecaz"
    "bazen": "sometimes",
    "özellikle": "especially",
    "ender": "rare",
    "kısa": "short-form",
    "Almanya": "Germany",
    "Amerika Birleşik Devletleri": "US",
    "Asya": "Asia",
    "Avrupa": "Europe",
    "Avrupa Birliği": "European-Union",
    "Avustralya": "Australia",
    "Avusturya": "Austria",
    "Fransa": "France",
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
# https://tr.wiktionary.org/wiki/Modül:temalar/veri/grup
TOPICS = {
    "anatomi": "anatomy",
    "diller": "language",
    "akışkanlar mekaniği": "fluid-dynamics",
    "antropoloji": "anthropology",
    "arıcılık": "beekeeping",
    "aritmetik": "arithmetic",
    "arkeoloji": "archaeology",
    "askeriye": "military",
    "astroloji": "astrology",
    "aşçılık": "cooking",
    "avcılık": "hunting",
    "bakteriyoloji": "bacteriology",
    # "bale": "ballet",
    "balıkçılık": "fishing",
    "bankacılık": "banking",
    "basketbol": "basketball",
    "basın-yayın": "publishing",
    "bilardo": "billiards",
    "bilgisayar bilimi": ["computer", "science"],
    "bilgisayar dili": "computer-languages",
    "bilim": "science",
    "bilişim": "informatics",
    # "binalar": "building",
    "binicilik": "equestrianism",
    "Birleşik Krallık": "UK",
    "bitki bilimi": "botany",
    # "bitki hastalıkları": "",
    "biyokimya": "biochemistry",
    "biyoloji": "biology",
    "biyoteknoloji": "biotechnology",
    "boks": "boxing",
    "böcek bilimi": "entomology",
    "Budizm": "Buddhism",
    "budun bilimi": "ethnology",
    "cerrahi": "surgery",
    "ceza hukuku": "law",
    "cinsellik": "sexuality",
    "cinsellik bilimi": "sexology",
    "cinsiyet": "sexuality",
    "coğrafya": "geography",
    "dans": "dancing",
    "demiryolu ulaşımı": ["railways", "transport"],
    "dermatoloji": "dermatology",
    "dil bilgisi": "grammar",
    "dil bilimi": "linguistics",
    "din": "religion",
    "diplomasi": "diplomacy",
    "diş hekimliği": "dentistry",
    "doğa bilimi": "natural-sciences",
    "dokuma": "weaving",
    "drama": "drama",
    "eczacılık": "pharmacology",
    "edebiyat": "literature",
    "eğitim": "education",
    "eğlence": "entertainment",
    "ekonomi": "economics",
    "elektrik": "electricity",
    "elektrik mühendisliği": "electrical-engineering",
    "elektromanyetizm": "electromagnetism",
    "elektronik": "electronics",
    "enerji": "energy",
    "epistemoloji": "epistemology",
    "eşey": "sex",
    "etik": "ethics",
    # "evlilik": "marriage",
    # "evrim": "evolution",
    "fahişelik": "prostitution",
    "farmakoloji": "pharmacology",
    "felsefe": "philosophy",
    "filateli": "philately",
    "finans": "finance",
    "fitopatoloji": "phytopathology",
    "fizik": "physics",
    "fizyoloji": "physiology",
    "fotoğrafçılık": "photography",
    "futbol": "football",
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
            if isinstance(topic, str) and topic not in data.topics:
                data.topics.append(topic)
            elif isinstance(topic, list):
                for t in topic:
                    if t not in data.topics:
                        data.topics.append(t)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
