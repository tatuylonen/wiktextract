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

SOUND_TAGS = {
    "การแผลงเป็น\nอักษรโรมัน": "romanization",  # Template:th-pron
}

LABEL_TAGS = {
    # https://th.wiktionary.org/wiki/มอดูล:labels/data
    "คำย่อ": "abbreviation",
    "อาการนาม": "abstract-noun",
    "อักษรอ่านย่อ": "acronym",
    "กรรตุวาจก": "active",
    "สกรรม, อกรรม": "ambitransitive",
    "มีชีวิต": "animate",
    "บอกเล่า": "indicative",
    "สมมุติ": "subjunctive",
    "สั่ง": "imperative",
    "คำกริยานุเคราะห์": "auxiliary",
    "จำนวนเชิงการนับ": "cardinal",
    "สมุหนาม": "collective",
    "เพศรวม": "common",
    "เปรียบเทียบได้": "comparable",
    "เชื่อม": "copulative",
    "นับได้": "countable",
    "ทวิกรรม": "ditransitive",
    "เพศหญิง": "feminine",
    "สำนวน": "idiomatic",
    "ไม่สมบูรณ์": "imperfective",
    "คำอบุรุษกริยา": "impersonal",
    "ในรูปเอกพจน์": "singular",
    "ในรูปทวิพจน์": "dual",
    "ในรูปพหูพจน์": "plural",
    "ไม่มีชีวิต": "inanimate",
    "ไม่ชี้เฉพาะ": "indefinite",
    "อักษรย่อ": "initialism",
    "อกรรม": "intransitive",
    "สัทอักษรสากล": "IPA",
    "เพศชาย": "masculine",
    "เพศกลาง": "neuter",
    "เปรียบเทียบไม่ได้": "not-comparable",
    "เลียนเสียงธรรมชาติ": "onomatopoeic",
    "จำนวนเชิงอันดับที่": "ordinal",
    "พาร์ทิซิเพิล": "partitive",
    "กรรมวาจก": "passive",
    "สมบูรณ์": "perfect",
    "พหูพจน์เท่านั้น": "plural-only",
    "แสดงความเป็นเจ้าของ": "possessive",
    "วลีภาคแสดง": "predicative",
    "สะท้อน": "reflexive",
    "เอกพจน์เท่านั้น": "singular-only",
    "สภาว": "stative",
    "สกรรม": "transitive",
    "นับไม่ได้": "uncountable",
    "โบราณ": "archaic",
    "ภาษาเด็ก": "childish",
    "ภาษาปาก": "colloquial",
    "ล้าสมัย": "dated",
    "นัยล้าสมัย": "dated",
    "ดูหมิ่น": "derogatory",
    "ภาษาถิ่น": "dialect",
    "ในเชิงเปรียบเทียบ": "metaphoric",
    "ทางการ": "formal",
    "ขำขัน": "humorous",
    "อติพจน์": "excessive",
    "ไม่ทางการ": "informal",
    "สแลงอินเทอร์เน็ต": ["Internet", "slang"],
    "ไออาร์ซี": "IRC",
    "ภาษาข่าว": "journalistic",
    "ภาษาหนังสือ": "literary",
    "คำสร้างใหม่": "neologism",
    "ภาษาไม่มาตรฐาน": "nonstandard",
    "เลิกใช้": "obsolete",
    "ล่วงเกิน": "offensive",
    "ร้อยกรอง": "poetic",
    "สุภาพ": "polite",
    "ไม่ควรใช้": "proscribed",
    "พบได้ยาก": "rare",
    # "ราชาศัพท์": "",
    "สแลง": "slang",
    # "ศัพท์เฉพาะ": "",
    "หยาบคาย": "vulgar",
}


TAGS = {**EXAMPLE_TAGS, **TRANSLATION_TAGS, **SOUND_TAGS, **LABEL_TAGS}


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
