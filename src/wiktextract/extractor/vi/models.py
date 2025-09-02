from pydantic import BaseModel, ConfigDict, Field


class VietnameseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(VietnameseBaseModel):
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


class AltForm(VietnameseBaseModel):
    word: str
    roman: str = ""


class Sense(VietnameseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []


class Linkage(VietnameseBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    sense: str = ""


class Form(VietnameseBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    sense: str = ""


class WordEntry(VietnameseBaseModel):
    model_config = ConfigDict(title="Vietnamese Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    holonyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    forms: list[Form] = []
