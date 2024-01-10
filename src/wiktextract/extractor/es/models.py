from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Linkage(BaseModelWrap):
    word: str
    note: Optional[str] = Field(default=None)
    alternative_spelling: Optional[str] = Field(
        default=None, description="Alternative spelling of the word"
    )


class Translation(BaseModelWrap):
    word: str = Field(description="Translation term")
    lang_code: str = Field(
        description="Wiktionary language code of the translation term"
    )
    senseids: list[str] = Field(
        default=[],
        description="List of senseids where this translation applies",
    )
    tags: list[str] = Field(
        default=[],
        description="Tags specifying the translated term, usually gender information",
    )
    notes: list[str] = Field(default=[], description="A list of notes")
    roman: Optional[str] = Field(
        default=None, description="Transliteration in roman characters"
    )


class EtymologyTemplate(BaseModelWrap):
    name: str = Field(default="", description="Template's name.")
    args: Optional[dict[str, str]] = Field(
        default=None, description="Arguments given to the template, if any."
    )
    expansion: str = Field(
        default="",
        description="The result of expanding the template, the final text it outputs.",
    )


class Reference(BaseModelWrap):
    url: Optional[str] = Field(default=None, description="A web link")
    first_name: Optional[str] = Field(
        default=None, description="Author's first name"
    )
    last_name: Optional[str] = Field(
        default=None, description="Author's last name"
    )
    title: Optional[str] = Field(
        default=None, description="Title of the reference"
    )
    pages: Optional[str] = Field(default=None, description="Page numbers")
    year: Optional[str] = Field(default=None, description="Year of publication")
    date: Optional[str] = Field(default=None, description="Date of publication")
    journal: Optional[str] = Field(default=None, description="Name of journal")
    chapter: Optional[str] = Field(default=None, description="Chapter name")
    place: Optional[str] = Field(
        default=None, description="Place of publication"
    )
    editor: Optional[str] = Field(default=None, description="Editor")


class Example(BaseModelWrap):
    text: str = Field(description="Example usage sentence")
    translation: Optional[str] = Field(
        default=None, description="Spanish translation of the example sentence"
    )
    ref: Optional["Reference"] = Field(default=None, description="")


class Sense(BaseModelWrap):
    glosses: list[str] = Field(
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging."
    )
    tags: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging.",
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
    senseid: Optional[str] = Field(
        default=None, description="Sense number used in Wiktionary"
    )
    antonyms: Optional[list[Linkage]] = []
    compounds: Optional[list[Linkage]] = []
    derived: Optional[list[Linkage]] = []
    hyponyms: Optional[list[Linkage]] = []
    hypernyms: Optional[list[Linkage]] = []
    idioms: Optional[list[Linkage]] = []
    meronyms: Optional[list[Linkage]] = []
    related: Optional[list[Linkage]] = []
    synonyms: Optional[list[Linkage]] = []


class Spelling(BaseModelWrap):
    alternative: Optional[str] = Field(
        default=None, description="Alternative spelling with same pronunciation"
    )
    note: Optional[str] = Field(
        default=None, description="Note regarding alternative spelling"
    )
    same_pronunciation: Optional[bool] = Field(
        default=None,
        description="Whether the alternative spelling has the same pronunciation as the default spelling",
    )


class Sound(BaseModelWrap):
    ipa: Optional[str] = Field(
        default=None, description="International Phonetic Alphabet"
    )
    phonetic_transcription: Optional[str] = Field(
        default=None, description="Phonetic transcription, less exact than IPA."
    )
    audio: Optional[str] = Field(default=None, description="Audio file name")
    wav_url: Optional[str] = Field(default=None)
    ogg_url: Optional[str] = Field(default=None)
    mp3_url: Optional[str] = Field(default=None)
    flac_url: Optional[str] = Field(default=None)
    roman: Optional[str] = Field(
        default=None, description="Translitaration to Roman characters"
    )
    syllabic: Optional[str] = Field(
        default=None, description="Syllabic transcription"
    )
    tags: list[str] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="Spanish Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default=None, description="Part of speech type")
    pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["es"]
    )
    lang: str = Field(
        description="Localized language name of the word", examples=["español"]
    )
    senses: Optional[list[Sense]] = []
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )
    sounds: Optional[list[Sound]] = []
    spellings: Optional[list[Spelling]] = []
    translations: Optional[list[Translation]] = []
    etymology_text: Optional[str] = Field(
        default=None, description="Etymology section as cleaned text."
    )
    etymology_templates: Optional[list[EtymologyTemplate]] = Field(
        default=None,
        description="Templates and their arguments and expansions from the etymology section.",
    )
    etymology_number: Optional[int] = Field(
        default=None,
        description="For words with multiple numbered etymologies, this contains the number of the etymology under which this entry appeared.",
    )
    antonyms: Optional[list[Linkage]] = []
    compounds: Optional[list[Linkage]] = []
    derived: Optional[list[Linkage]] = []
    hyponyms: Optional[list[Linkage]] = []
    hypernyms: Optional[list[Linkage]] = []
    idioms: Optional[list[Linkage]] = []
    meronyms: Optional[list[Linkage]] = []
    related: Optional[list[Linkage]] = []
    synonyms: Optional[list[Linkage]] = []
