from pydantic import BaseModel, ConfigDict, Field


class IndonesianBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(IndonesianBaseModel):
    text: str
    translation: str = ""
    literal_meaning: str = ""
    roman: str = ""
    ref: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sense(IndonesianBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    topics: list[str] = []


class Translation(IndonesianBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    lit: str = Field(default="", description="Literal translation")


class Sound(IndonesianBaseModel):
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
    roman: str = ""


class Linkage(IndonesianBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    source: str = ""
    sense: str = ""


class Form(IndonesianBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(IndonesianBaseModel):
    model_config = ConfigDict(title="Indonesian Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    etymology_texts: list[str] = []
    translations: list[Translation] = []
    sounds: list[Sound] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    forms: list[Form] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    proverbs: list[Linkage] = []
