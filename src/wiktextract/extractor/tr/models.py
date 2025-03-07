from pydantic import BaseModel, ConfigDict, Field


class TurkishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(TurkishBaseModel):
    text: str
    translation: str = ""
    ref: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class AltForm(TurkishBaseModel):
    word: str


class Sense(TurkishBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []


class Form(TurkishBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class Sound(TurkishBaseModel):
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
    roman: str = ""


class WordEntry(TurkishBaseModel):
    model_config = ConfigDict(title="Turkish Wiktionary")
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
    etymology_texts: list[str] = []
    sounds: list[Sound] = []
    hyphenation: str = ""
