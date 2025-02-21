from pydantic import BaseModel, ConfigDict, Field


class IndonesianBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(IndonesianBaseModel):
    text: str
    translation: str = ""
    literal_meaning: str = ""
    roman: str = ""
    ref: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sense(IndonesianBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []


class WordEntry(IndonesianBaseModel):
    model_config = ConfigDict(title="Indonesian Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
