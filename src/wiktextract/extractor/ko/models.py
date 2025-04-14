from pydantic import BaseModel, ConfigDict, Field


class KoreanBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Sound(KoreanBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    flac_url: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    hangul: str = ""
    roman: str = ""
    other: str = ""


class Example(KoreanBaseModel):
    text: str = ""
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    ref: str = ""
    roman: str = ""
    bold_roman_offsets: list[tuple[int, int]] = []
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    tags: list[str] = []
    literal_meaning: str = ""
    bold_literal_offsets: list[tuple[int, int]] = []
    note: str = ""
    sounds: list[Sound] = []


class AltForm(KoreanBaseModel):
    word: str


class Sense(KoreanBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    note: str = ""
    form_of: list[AltForm] = []
    pattern: str = Field(default="", description="Sentence structure, 문형")


class Linkage(KoreanBaseModel):
    word: str
    sense: str = ""
    roman: str = ""
    raw_tags: list[str] = []
    tags: list[str] = []
    sense_index: str = ""


class Translation(KoreanBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term"
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    sense: str = ""


class Form(KoreanBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(KoreanBaseModel):
    model_config = ConfigDict(title="Korean Wiktionary")
    word: str = Field(description="Word string", min_length=1)
    lang_code: str = Field(description="Wiktionary language code", min_length=1)
    lang: str = Field(description="Localized language name", min_length=1)
    pos: str = Field(description="Part of speech type", min_length=1)
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    sounds: list[Sound] = []
    proverbs: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    translations: list[Translation] = []
    etymology_texts: list[str] = []
    note: str = ""
    forms: list[Form] = []
    pattern: str = Field(
        default="", description="Sentence structure, 문형", exclude=True
    )
    idioms: list[Translation] = []
    hyponyms: list[Translation] = []
