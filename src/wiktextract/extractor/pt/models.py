from pydantic import BaseModel, ConfigDict, Field


class PortugueseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(PortugueseBaseModel):
    text: str = ""
    translation: str = ""
    ref: str = ""


class AltForm(PortugueseBaseModel):
    word: str


class Sense(PortugueseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []


class Translation(PortugueseBaseModel):
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Translation language name")
    word: str = Field(default="", description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""


class Linkage(PortugueseBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    senses: list[Sense] = []
    sense: str = ""
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )
    source: str = ""
    roman: str = ""


class Sound(PortugueseBaseModel):
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


class Form(PortugueseBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(PortugueseBaseModel):
    model_config = ConfigDict(title="Portuguese Wiktionary")
    word: str = Field(description="Word string", min_length=1)
    lang_code: str = Field(description="Wiktionary language code", min_length=1)
    lang: str = Field(description="Localized language name", min_length=1)
    pos: str = Field(description="Part of speech type", min_length=1)
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    translations: list[Translation] = []
    expressions: list[Linkage] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    derived: list[Linkage] = []
    anagrams: list[Linkage] = []
    hypernyms: list[Linkage] = []
    related: list[Linkage] = []
    hyponyms: list[Linkage] = []
    homophones: list[Linkage] = []
    homonyms: list[Linkage] = []
    paronyms: list[Linkage] = []
    phraseology: list[Linkage] = []
    etymology_texts: list[str] = []
    sounds: list[Sound] = []
    forms: list[Form] = []
    notes: list[str] = []
    cognates: list[Translation] = []
    descendants: list[Translation] = []
