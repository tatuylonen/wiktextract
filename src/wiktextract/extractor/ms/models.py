from pydantic import BaseModel, ConfigDict, Field


class MalayBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(MalayBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    roman: str = ""
    bold_roman_offsets: list[tuple[int, int]] = []
    ref: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    literal_meaning: str = ""
    bold_literal_offsets: list[tuple[int, int]] = []


class AltForm(MalayBaseModel):
    word: str


class Sense(MalayBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []


class Form(MalayBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class Linkage(MalayBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    sense: str = ""


class Translation(MalayBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    categories: list[str] = Field(default=[], exclude=True)


class Sound(MalayBaseModel):
    zh_pron: str = Field(default="", description="Chinese word pronunciation")
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
    homophone: str = ""
    other: str = ""
    roman: str = ""
    rhymes: str = ""
    categories: list[str] = Field(default=[], exclude=True)
    hyphenation: str = Field(default="", exclude=True)


class WordEntry(MalayBaseModel):
    model_config = ConfigDict(title="Malay Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    forms: list[Form] = []
    etymology_text: str = ""
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    translations: list[Translation] = []
    hypernyms: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hyphenation: str = ""
    sounds: list[Sound] = []
    derived: list[Linkage] = []
    anagrams: list[Linkage] = []
    proverbs: list[Linkage] = []
    related: list[Linkage] = []
    notes: list[str] = []
