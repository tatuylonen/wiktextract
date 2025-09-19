from .models import WordEntry

# https://vi.wiktionary.org/wiki/Mô_đun:labels/data
LABEL_TAGS = {
    "viết tắt": "abbreviation",
    "trừu tượng": "abstract-noun",
    "acronym": "acronym",
    "ngoại động từ, nội động từ": "ambitransitive",
    "archaic": "archaic",
    "thuộc ngữ": "attributive",
    "attributively": "attributively",
    "trợ động từ": "auxiliary",
    "giống chung": "common",
    "đếm được": "countable",
    "ngoại động từ kép": "ditransitive",
    "khiển cách": "ergative",
    "nghĩa mở rộng": "broadly",
    "thành ngữ tính": "idiomatic",
    "ở dạng số nhiều": "plural",
    "viết tắt từ chữ đầu với cách đọc ghép âm": "initialism",
    "nội động từ": "intransitive",
    "không so sánh được": "not-comparable",
    "tượng thanh": "onomatopoeic",
    "chỉ có số nhiều": "plural-only",
    "tính từ quan hệ": "relational",
    "động từ tĩnh": "stative",
    "ngoại động từ": "transitive",
    "từ láy": "reduplication",
    "không đếm được": "uncountable",
    "cổ xưa": "archaic",
    "ngôn ngữ trẻ con": "childish",
    "vietnamese chữ Nôm": "Chữ-Nôm",
    "từ lóng có vần điệu của người Luân Đôn": ["Cockney", "slang"],
    "thông tục": "colloquial",
    "lỗi thời": "dated",
    "nghĩa xấu": "derogatory",
    "phương ngữ": "dialectal",
    "thuộc phương ngữ": "dialectal",
    "xúc phạm dân tộc": ["ethnic", "slang"],
    "uyển ngữ": "euphemistic",
    "thân mật": "familiar",
    "nghĩa bóng": "figuratively",
    "trang trọng": "formal",
    "từ lóng người đồng tính": "slang",
    "từ ngữ lịch sử": "historical",
    "kính ngữ": "honorific",
    "hài hước": "humorous",
    "không trang trọng": "informal",
    "từ lóng internet": ["Internet", "slang"],
    "trớ trêu": "ironic",
    "nghĩa đen": "literally",
    "ăn chương": "literary",
    "hoán dụ": "metonymically",
    "từ lóng quân sự": "slang",
    "từ mới": "neologism",
    "không còn phát sinh từ mới": "idiomatic",
    "từ tạo ra cho trường hợp cụ thể": "nonce-word",
    "không tiêu chuẩn": "nonstandard",
    "không còn dùng": "obsolete",
    "thuật ngữ không còn dùng": "obsolete",
    "xúc phạm": "offensive",
    "thơ ca": "poetic",
    "lịch sự": "polite",
    "hiếm": "rare",
    "từ lóng": "slang",
    "nhắn tin": "Internet",
    "không phổ biến": "uncommon",
    "thô tục": "vulgar",
    "anh": "UK",
    "biệt ngữ": "jargon",
    "cũ": "obsolete",
    "cổ": "archaic",
    "không dịch": "not-translated",
    "khẩu ngữ": "colloquial",
    "lóng": "slang",
    "mỉa mai": "ironic",
    "nghĩa rộng": "broadly",
    "số nhiều": "plural",
    "nói trại": "euphemistic",
    "tục tĩu": "vulgar",
    "ít dùng": "rare",
    "địa phương": "regional",
    "định ngữ": "attributive",
    "ấn độ": "India",
    "động từ và ngoại động từ": "ambitransitive",
    "châu mỹ": "US",
    "hoa kỳ": "US",
    "phát âm mỹ": "US",
    "hoạt hình": "animate",
    "phương ngữ mắt": "pronunciation-spelling",
}

# https://vi.wiktionary.org/wiki/Mô_đun:gender_and_number/data
GENDER_NUMBER_TAGS = {
    "giống đực": "masculine",
    "giống cái": "feminine",
    "giống trung": "neuter",
    "giống chung": "common-gender",
    "gender-neutral": "neuter",
    "động vật": "animate",
    "bất động vật": "inanimate",
    "chỉ loài vật": "animal-not-person",
    "từ chỉ cá nhân": "person",
    "nonpersonal": "impersonal",
    "virile (= masculine personal)": "virile",
    "nonvirile (= other than masculine personal)": "nonvirile",
    "số ít": "singular",
    "số kép": "dual",
    "số nhiều": "plural",
    "thể chưa hoàn thành": "imperfective",
    "thể hoàn thành": "perfective",
}

LOCATIONS = {
    "hà nội": "Hà-Nội",
    "huế": "Huế",
    "sài gòn": "Saigon",
    "vinh": "Vinh",
    "thanh chương": "Thanh-Chương",
    "hà tĩnh": "Hà-Tĩnh",
}

SOUND_TAGS = {
    "phát âm giọng anh chuẩn": "Received-Pronunciation",
    "anh mỹ thông dụng": "General-American",
}

TAGS = {**LABEL_TAGS, **GENDER_NUMBER_TAGS, **LOCATIONS, **SOUND_TAGS}

# https://vi.wiktionary.org/wiki/Mô_đun:labels/data/topical
TOPICS = {
    "địa chấn học": "seismology",
    "thực vật học": "botany",
    "hóa học": "chemistry",
    "từ lóng người đồng tính": "LGBT",
    "từ lóng quân sự": "military",
    "bóng chày": "baseball",
    "bóng rổ": "basketball",
    "băng cầu": "ice-hockey",
    "bắn cung": "archery",
    "chính trị": "politics",
    "cơ khí": "mechanical",
    "cử tạ": "weightlifting",
    "dược học": "pharmaceuticals",
    "giải phẫu học": "anatomy",
    "hàng hải": "shipping",
    "hàng không": "aviation",
    "in ấn": "printing",
    "khoa đo lường": "metrology",
    "khoáng vật học": "mineralogy",
    "khúc côn cầu": "hockey",
    "khảo cổ học": "archeology",
    "kinh doanh": "business",
    "kinh tế học": "economics",
    "kiến trúc": "architecture",
    "kiểu cách": "manner",
    "kế toán": "accounting",
    "kỹ thuật": "technology",
    "luật pháp": "law",
    "lâm nghiệp": "forestry",
    "lôgic": "logic",
    "lập trình": "programming",
    "máy tính": "computer",
    "nghệ thuật": "arts",
    "ngoại giao": "diplomacy",
    "ngành mỏ": "mining",
    "nhân khẩu học": "demographics",
    "nhãn khoa": "ophthalmology",
    "nấu nướng": "cooking",
    "sinh thái học": "ecology",
    "sinh vật học": "biology",
    "sân khấu": "theater",
    "săn bắn": "hunting",
    "thương nghiệp": "commerce",
    "thần học": "theology",
    "thần thoại": "mythology",
    "thể dục": "exercise",
    "thể thao": "sports",
    "tin học": "computer-sciences",
    "tài chính": "finance",
    "tôn giáo": "religion",
    "văn học": "literature",
    "vật lý học": "physics",
    "xã hội học": "sociology",
    "y học": "medicine",
    "đạo giáo": "Taoism",
    "điện học": "electricity",
    "điện tử học": "electronics",
    "điện ảnh": "film",
    "đánh bài": "gambling",
    "đường sắt": "railways",
    "đại số": "algebra",
    "động vật học": "zoology",
    "nông nghiệp": "agriculture",
    "phi cơ": "airplane",
    "đại số học": "algebra",
    "bóng đá mỹ": "American-football",
    "lưỡng cư": "amphibian",
    "bài tập": "exercise",
    "đấu kiếm": "fencing",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        found_tag = False
        if raw_tag.lower() in TAGS and hasattr(data, "tags"):
            found_tag = True
            tr_tag = TAGS[raw_tag.lower()]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        if raw_tag.lower() in TOPICS and hasattr(data, "topics"):
            found_tag = True
            topic = TOPICS[raw_tag.lower()]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, list):
                data.topics.extend(topic)
        if not found_tag:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
