from pydantic import BaseModel, ConfigDict, Field


class CzechBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Sense(CzechBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []


class WordEntry(CzechBaseModel):
    model_config = ConfigDict(title="Czech Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
