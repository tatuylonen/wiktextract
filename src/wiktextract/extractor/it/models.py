from pydantic import BaseModel, ConfigDict, Field


class ItalianBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(ItalianBaseModel):
    text: str = ""
    translation: str = ""
    ref: str = ""
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sense(ItalianBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []


class WordEntry(ItalianBaseModel):
    model_config = ConfigDict(title="Italian Wiktionary")
    word: str = Field(description="Word string", min_length=1)
    lang_code: str = Field(description="Wiktionary language code", min_length=1)
    lang: str = Field(description="Localized language name", min_length=1)
    pos: str = Field(description="Part of speech type", min_length=1)
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
