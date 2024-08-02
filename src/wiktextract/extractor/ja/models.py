from pydantic import BaseModel, ConfigDict, Field


class JapaneseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(JapaneseBaseModel):
    text: str = ""
    translation: str = ""
    ref: str = ""
    ruby: list[tuple[str, ...]] = []


class Sense(JapaneseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    ruby: list[tuple[str, ...]] = []
    examples: list[Example] = []


class Form(JapaneseBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sound(JapaneseBaseModel):
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
    homophones: list[str] = []
    form: str = ""
    roman: str = ""


class WordEntry(JapaneseBaseModel):
    model_config = ConfigDict(title="Japanese Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    forms: list[Form] = []
    etymology_texts: list[str] = []
    sounds: list[Sound] = []
