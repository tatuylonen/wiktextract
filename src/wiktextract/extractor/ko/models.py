from pydantic import BaseModel, ConfigDict, Field


class KoreanBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(KoreanBaseModel):
    text: str = ""
    translation: str = ""
    ref: str = ""
    roman: str = ""
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    tags: list[str] = []
    literal_meaning: str = ""
    note: str = ""


class Sense(KoreanBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    note: str = ""


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


class Linkage(KoreanBaseModel):
    word: str
    sense: str = ""


class Translation(KoreanBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term"
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    roman: str = ""
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
    etymology_text: str = ""
    sounds: list[Sound] = []
    proverbs: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    translations: list[Translation] = []
