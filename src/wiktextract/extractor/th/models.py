from pydantic import BaseModel, ConfigDict, Field


class ThaiBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Sound(ThaiBaseModel):
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
    enpr: str = ""


class Example(ThaiBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    literal_meaning: str = ""
    bold_literal_offsets: list[tuple[int, int]] = []
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    bold_roman_offsets: list[tuple[int, int]] = []
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = Field(default=[], exclude=True)
    sounds: list[Sound] = []


class AltForm(ThaiBaseModel):
    word: str
    roman: str = ""


class Sense(ThaiBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    classifiers: list[str] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []
    topics: list[str] = []


class Form(ThaiBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""


class Translation(ThaiBaseModel):
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


class Linkage(ThaiBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    source: str = ""
    sense: str = ""


class Descendant(ThaiBaseModel):
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Language name")
    word: str
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    descendants: list["Descendant"] = []
    sense: str = ""


class WordEntry(ThaiBaseModel):
    model_config = ConfigDict(title="Thai Wiktionary")
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
    classifiers: list[str] = []
    forms: list[Form] = []
    translations: list[Translation] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    descendants: list[Descendant] = []
    anagrams: list[Linkage] = []
    notes: list[str] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    idioms: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    sounds: list[Sound] = []
    hyphenation: list[str] = []
    abbreviations: list[Linkage] = []
    proverbs: list[Linkage] = []
    notes: list[str] = []
