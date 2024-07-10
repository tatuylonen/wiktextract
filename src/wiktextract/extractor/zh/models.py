from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChineseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(ChineseBaseModel):
    text: str = Field(
        default="",
        description="Example usage sentences, some might have have both "
        "Simplified and Traditional Chinese forms",
    )
    translation: str = Field(
        default="", description="Chinese translation of the example sentence"
    )
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    tags: list[str] = []
    raw_tags: list[str] = []


class AltForm(ChineseBaseModel):
    word: str


class Sense(ChineseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    alt_of: list[AltForm] = []
    form_of: list[AltForm] = []


class Form(ChineseBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    source: str = ""
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    hiragana: str = ""
    roman: str = ""


class Sound(ChineseBaseModel):
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
    enpr: str = Field(default="", description="English pronunciation")


class Translation(ChineseBaseModel):
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Translation language name")
    word: str = Field(description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = Field(default="", description="Roman script")
    alt: str = Field(default="", description="Alternative form")
    lit: str = Field(default="", description="Literal translation for the term")


class Linkage(ChineseBaseModel):
    word: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    sense: str = ""
    language_variant: Literal["", "zh-Hant", "zh-Hans"] = Field(
        default="", description="Chinese character variant"
    )
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )


class Descendant(ChineseBaseModel):
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Language name")
    word: str = ""
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    descendants: list["Descendant"] = []
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )


class WordEntry(ChineseBaseModel):
    model_config = ConfigDict(title="Chinese Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    etymology_text: str = ""
    etymology_examples: list[Example] = []
    senses: list[Sense] = Field(default=[], description="Sense list")
    forms: list[Form] = Field(default=[], description="Inflection forms list")
    sounds: list[Sound] = []
    translations: list[Translation] = []
    synonyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    holonyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    derived: list[Linkage] = []
    troponyms: list[Linkage] = []
    paronyms: list[Linkage] = []
    related: list[Linkage] = []
    abbreviation: list[Linkage] = []
    proverbs: list[Linkage] = []
    antonyms: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    various: list[Linkage] = []
    compounds: list[Linkage] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    notes: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    descendants: list[Descendant] = []
    redirects: list[str] = Field(
        default=[],
        description="Soft redirect page, extracted from template zh-see ja-see",
    )
    literal_meaning: str = ""
