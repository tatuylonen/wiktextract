from pydantic import BaseModel, ConfigDict, Field


class KurdishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Sound(KurdishBaseModel):
    ipa: str = ""
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    flac_url: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Example(KurdishBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    bold_roman_offsets: list[tuple[int, int]] = []
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    tags: list[str] = []
    raw_tags: list[str] = []
    sounds: list[Sound] = []
    categories: list[str] = Field(default=[], exclude=True)


class AltForm(KurdishBaseModel):
    word: str


class Sense(KurdishBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    topics: list[str] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []


class Form(KurdishBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    translation: str = ""
    sense: str = ""
    source: str = ""


class Translation(KurdishBaseModel):
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
    roman: str = ""
    source: str = ""


class Linkage(KurdishBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    translation: str = ""
    sense: str = ""


class Descendant(KurdishBaseModel):
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Language name")
    word: str
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    descendants: list["Descendant"] = []
    sense: str = ""


class WordEntry(KurdishBaseModel):
    model_config = ConfigDict(title="Kurdish Wiktionary")
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
    translations: list[Translation] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    hypernyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    anagrams: list[Linkage] = []
    rhymes: list[Linkage] = []
    sounds: list[Sound] = []
    hyphenation: str = ""
    notes: list[str] = []
    descendants: list[Descendant] = []
    abbreviations: list[Linkage] = []
