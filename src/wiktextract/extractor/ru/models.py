from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Sound(BaseModelWrap):
    ipa: Optional[str] = Field(
        default=None, description="International Phonetic Alphabet"
    )
    audio: Optional[str] = Field(default=None, description="Audio file name")
    wav_url: Optional[str] = Field(default=None)
    ogg_url: Optional[str] = Field(default=None)
    oga_url: Optional[str] = Field(default=None)
    mp3_url: Optional[str] = Field(default=None)
    flac_url: Optional[str] = Field(default=None)
    tags: Optional[list[str]] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )
    homophones: Optional[list[str]] = Field(
        default=[], description="Words with same pronunciation"
    )


class Sense(BaseModelWrap):
    raw_gloss: Optional[str] = Field(
        default=None,
        description="Raw gloss string for the word sense. This might contain tags and other markup.",
    )
    gloss: Optional[str] = Field(
        default=None,
        description="Gloss string for the word sense. This has been cleaned, and should be straightforward text with no tags.",
    )
    tags: list[str] = Field(
        default=[],
        description="List of tags affecting the word sense.",
    )
    notes: list[str] = Field(
        default=[],
        description="List of notes for the word sense. Usually describing usage.",
    )
    categories: list[str] = Field(
        default=[],
        description="list of sense-disambiguated category names extracted from (a subset) of the Category links on the page",
    )
    examples: list["Example"] = Field(
        default=[], description="List of examples"
    )
    # subsenses: list["Sense"] = Field(
    #     default=[], description="List of subsenses"
    # )
    # senseid: Optional[int] = Field(
    #     default=None, description="Sense number used in Wiktionary"
    # )


class Reference(BaseModelWrap):
    author: Optional[str] = Field(default=None, description="Author's name")
    title: Optional[str] = Field(
        default=None, description="Title of the reference"
    )
    date: Optional[str] = Field(default=None, description="Original date")
    date_published: Optional[str] = Field(
        default=None, description="Date of publication"
    )

    collection: Optional[str] = Field(
        default=None,
        description="Name of the collection the example was taken from",
    )
    editor: Optional[str] = Field(default=None, description="Editor")
    translator: Optional[str] = Field(default=None, description="Translator")
    source: Optional[str] = Field(
        default=None,
        description="Source of reference, corresponds to template parameter 'источник'",
    )


class Example(BaseModelWrap):
    text: Optional[str] = Field(
        default=None, description="Example usage sentence"
    )
    translation: Optional[str] = Field(
        default=None, description="Spanish translation of the example sentence"
    )
    ref: Optional["Reference"] = Field(default=None, description="")


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="Russian Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default=None, description="Part of speech type")
    pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["ru"]
    )
    lang_name: str = Field(
        description="Localized language name of the word", examples=["Русский"]
    )
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )
    sounds: Optional[list[Sound]] = []
    senses: Optional[list[Sense]] = []
