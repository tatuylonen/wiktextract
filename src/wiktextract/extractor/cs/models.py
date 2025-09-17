from pydantic import BaseModel, ConfigDict, Field


class CzechBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(CzechBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )


class AltForm(CzechBaseModel):
    word: str


class Sense(CzechBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []


class Sound(CzechBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    tags: list[str] = []
    raw_tags: list[str] = []
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    flac_url: str = ""


class Hyphenation(CzechBaseModel):
    parts: list[str] = []


class Form(CzechBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class Translation(CzechBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )
    tags: list[str] = []
    raw_tags: list[str] = []


class Linkage(CzechBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )


class WordEntry(CzechBaseModel):
    model_config = ConfigDict(title="Czech Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    sounds: list[Sound] = []
    hyphenations: list[Hyphenation] = []
    etymology_texts: list[str] = []
    forms: list[Form] = []
    translations: list[Translation] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    related: list[Linkage] = []
    phrases: list[Linkage] = []
    proverbs: list[Linkage] = []
