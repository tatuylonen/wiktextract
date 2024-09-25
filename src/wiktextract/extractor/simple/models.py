from typing import Optional

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

class Example(SimpleEnglishBaseModel):
    text: str = Field(default="", description="Example usage sentence")
    author: str = Field(default="", description="Author's name")
    title: str = Field(default="", description="Title of the reference")
    # date: str = Field(default="", description="Original date")
    # date_published: str = Field(default="", description="Date of publication")
    # collection: str = Field(
    #     default="",
    #     description="Name of the collection the example was taken from",
    # )
    # editor: str = Field(default="", description="Editor")
    # translator: str = Field(default="", description="Translator")
    # source: str = Field(
    #     default="",
    #     description="Source of reference",
    # )

class Sense(SimpleEnglishBaseModel):
    glosses: list[str] = []  # "Gloss supercategory", "Specific gloss."
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    # ruby: list[tuple[str, ...]] = []

class Form(SimpleEnglishBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    # sense_index: str = ""


class Sound(SimpleEnglishBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    enpr: str = Field(default="", description="American Heritage Dictionary")
    sampa: str = Field(
        default="", description="Speech Assessment Methods Phonetic Alphabet"
    )
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = Field(default="")
    ogg_url: str = Field(default="")
    mp3_url: str = Field(default="")
    oga_url: str = Field(default="")
    flac_url: str = Field(default="")
    lang_code: str = Field(default="en", description="Wiktionary language code")
    lang: str = Field(default="English", description="Localized language name")
    raw_tags: list[str] = []
    tags: list[str] = []
    rhymes: list[str] = []
    homophones: list[str] = []
    # text: str = ""  # Use raw_tags instead
    # Temporary field used to sort out different sound data between POSes when
    # they are originally found in one combined pronunciation section
    poses: list[str] = []

class TemplateData(SimpleEnglishBaseModel):
    name: str = Field(default="", description="Template's name.")
    args: dict[str, str] = Field(
        default={}, description="Arguments given to the template, if any."
    )
    expansion: str = Field(
        default="",
        description="The result of expanding the template.",
    )

class WordEntry(SimpleEnglishBaseModel):
    model_config = ConfigDict(title="Simple English Wiktionary")

    word: str = Field(description="Word string")
    # For Simple English, the language is always English
    forms: list[Form] = Field(default=[], description="Inflection forms list")
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Localized language name")
    pos: str = Field(default="", desription="Part of speech type")
    pos_title: str = ""
    pos_num: int = -1
    etymology_text: str = Field(
        default="", description="Etymology section as cleaned text."
    )
    etymology_templates: list[TemplateData] = Field(
        default=[],
        description="Templates and their arguments and expansions from the "
        "etymology section.",
    )
    # Simple Wiktionary doesn't have numbered etymology sections
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    sounds: list[Sound] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    hyphenation: str = ""
