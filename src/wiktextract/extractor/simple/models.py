from pydantic import BaseModel, ConfigDict, Field


class SimpleEnglishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        # We use pydantic mainly for the automatic validation; this
        # setting ensures the validation is done even when assigning something
        # after initialization, otherwise it doesn't check anything.
        validate_default=True,
    )

class Sense(SimpleEnglishBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    # ruby: list[tuple[str, ...]] = []

class WordEntry(SimpleEnglishBaseModel):
    model_config = ConfigDict(title="Simple English Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(default="", desription="Part of speech type")
    pos_title: str = ""
    sense: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
