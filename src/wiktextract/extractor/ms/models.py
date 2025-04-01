from pydantic import BaseModel, ConfigDict, Field


class MalayBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(MalayBaseModel):
    text: str
    translation: str = ""
    roman: str = ""
    ref: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    literal_meaning: str = ""


class AltForm(MalayBaseModel):
    word: str


class Sense(MalayBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []


class Form(MalayBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class Linkage(MalayBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(MalayBaseModel):
    model_config = ConfigDict(title="Malay Wiktionary")
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
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
