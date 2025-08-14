from pydantic import BaseModel, ConfigDict, Field


class PolishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(PolishBaseModel):
    text: str = ""
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    ref: str = ""
    roman: str = ""
    literal_meaning: str = ""


class AltForm(PolishBaseModel):
    word: str


class Attestation(PolishBaseModel):
    date: str


class Sense(PolishBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    sense_index: str = ""
    examples: list[Example] = []
    alt_of: list[AltForm] = []
    form_of: list[AltForm] = []
    notes: list[str] = []
    attestations: list[Attestation] = []


class Translation(PolishBaseModel):
    lang_code: str = ""
    lang: str = ""
    word: str = ""
    sense_index: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    ruby: list[tuple[str, ...]] = []


class Sound(PolishBaseModel):
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


class Linkage(PolishBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    sense_index: str = ""
    topics: list[str] = []
    furigana: str = ""
    translation: str = ""


class Form(PolishBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    sense_index: str = ""


class Note(PolishBaseModel):
    sense_index: str = ""
    text: str = Field(min_length=1)


class Hyphenation(PolishBaseModel):
    parts: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(PolishBaseModel):
    model_config = ConfigDict(title="Polish Wiktionary")

    word: str = Field(description="Word string", min_length=1)
    lang_code: str = Field(description="Wiktionary language code", min_length=1)
    lang: str = Field(description="Localized language name", min_length=1)
    pos: str = Field(description="Part of speech type", min_length=1)
    pos_text: str = ""
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    etymology_texts: list[str] = []
    translations: list[Translation] = []
    sounds: list[Sound] = []
    antonyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    holonyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    related: list[Linkage] = []
    proverbs: list[Linkage] = []
    synonyms: list[Linkage] = []
    derived: list[Linkage] = []
    forms: list[Form] = []
    hyphenations: list[Hyphenation] = []
