from pydantic import BaseModel, ConfigDict, Field


class KurdishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(KurdishBaseModel):
    text: str
    translation: str = ""
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    tags: list[str] = []
    raw_tags: list[str] = []


class Sense(KurdishBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []


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
