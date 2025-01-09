from pydantic import BaseModel, ConfigDict, Field


class ThaiBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(ThaiBaseModel):
    text: str
    translation: str = ""
    literal_meaning: str = ""
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


class Sense(ThaiBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    classifiers: list[str] = []


class Form(ThaiBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


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
