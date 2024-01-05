from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Linkage(BaseModelWrap):
    word: str


class Translation(BaseModelWrap):
    sense: Optional[str] = Field(
        default=None, description="A gloss of the sense being translated"
    )
    word: Optional[str] = Field(default=None, description="Translation term")
    lang_code: Optional[str] = Field(
        default=None,
        description="Wiktionary language code of the translation term",
    )
    lang_name: Optional[str] = Field(
        default=None, description="Localized language name"
    )
    uncertain: Optional[bool] = Field(
        default=False, description="Translation marked as uncertain"
    )
    roman: Optional[str] = Field(
        default=None, description="Transliteration to Roman characters"
    )
    # senseids: list[str] = Field(
    #     default=[],
    #     description="List of senseids where this translation applies",
    # )
    tags: list[str] = Field(
        default=[],
        description="Tags specifying the translated term, usually gender information",
    )
    notes: list[str] = Field(default=[], description="A list of notes")
    roman: Optional[str] = Field(
        default=None, description="Transliteration in roman characters"
    )


class Reference(BaseModelWrap):
    raw_ref: str = Field(default=None, description="Raw reference string")
    url: Optional[str] = Field(
        default=None, description="A web link. Not necessarily well-formated."
    )
    author: Optional[str] = Field(default=None, description="Author's name")

    title: Optional[str] = Field(
        default=None, description="Title of the reference"
    )
    title_complement: Optional[str] = Field(
        default=None, description="Complement to the title"
    )
    pages: Optional[str] = Field(default=None, description="Page numbers")
    year: Optional[str] = Field(default=None, description="Year of publication")
    publisher: Optional[str] = Field(default=None, description="Published by")
    editor: Optional[str] = Field(default=None, description="Editor")
    translator: Optional[str] = Field(default=None, description="Translator")
    collection: Optional[str] = Field(
        default=None,
        description="Name of collection that reference was published in",
    )
    volume: Optional[str] = Field(default=None, description="Volume number")
    comment: Optional[str] = Field(
        default=None, description="Comment on the reference"
    )
    day: Optional[str] = Field(default=None, description="Day of publication")
    month: Optional[str] = Field(
        default=None, description="Month of publication"
    )
    accessdate: Optional[str] = Field(
        default=None, description="Date of access of online reference"
    )

    date: Optional[str] = Field(default=None, description="Date of publication")
    number: Optional[str] = Field(default=None, description="Issue number")
    # journal: Optional[str] = Field(default=None, description="Name of journal")
    # chapter: Optional[str] = Field(default=None, description="Chapter name")
    place: Optional[str] = Field(
        default=None, description="Place of publication"
    )
    # editor: Optional[str] = Field(default=None, description="Editor")
    edition: Optional[str] = Field(default=None, description="Edition number")
    isbn: Optional[str] = Field(default=None, description="ISBN number")


class Example(BaseModelWrap):
    text: str = Field(default=None, description="Example usage sentence")
    # translation: Optional[str] = Field(
    #     default=None, description="Spanish translation of the example sentence"
    # )
    ref: Optional["Reference"] = Field(default=None, description="")


class Sense(BaseModelWrap):
    glosses: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging.",
    )
    raw_glosses: list[str] = Field(
        default=[],
        description="list of uncleaned raw glosses for the word sense (usually only one).",
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
    translations: Optional[list[Translation]] = []
    antonyms: Optional[list[Linkage]] = []
    derived: Optional[list[Linkage]] = []
    hyponyms: Optional[list[Linkage]] = []
    hypernyms: Optional[list[Linkage]] = []
    holonyms: Optional[list[Linkage]] = []
    expressions: Optional[list[Linkage]] = []
    coordinate_terms: Optional[list[Linkage]] = []
    proverbs: Optional[list[Linkage]] = []
    synonyms: Optional[list[Linkage]] = []


class Sound(BaseModelWrap):
    ipa: list[str] = Field(
        default=[], description="International Phonetic Alphabet"
    )
    # phonetic_transcription: list[str] = Field(
    #     default=[], description="Phonetic transcription, less exact than IPA."
    # )
    audio: list[str] = Field(default=[], description="Audio file name")
    wav_url: list[str] = Field(default=[])
    ogg_url: list[str] = Field(default=[])
    mp3_url: list[str] = Field(default=[])
    oga_url: list[str] = Field(default=[])
    flac_url: list[str] = Field(default=[])
    lang_code: list[str] = Field(
        default=[], description="Wiktionary language code"
    )
    lang_name: list[str] = Field(
        default=[], description="Localized language name"
    )
    # roman: list[str] = Field(
    #     default=[], description="Translitaration to Roman characters"
    # )
    # syllabic: list[str] = Field(
    #     default=[], description="Syllabic transcription"
    # )
    tags: list[str] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )
    pass


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="German Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default=None, description="Part of speech type")
    # pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["es"]
    )
    lang_name: str = Field(
        description="Localized language name of the word", examples=["español"]
    )
    senses: Optional[list[Sense]] = []
    # categories: list[str] = Field(
    #     default=[],
    #     description="list of non-disambiguated categories for the word",
    # )
    translations: Optional[list[Translation]] = []
    sounds: Optional[list[Sound]] = []
    antonyms: Optional[list[Linkage]] = []
    derived: Optional[list[Linkage]] = []
    hyponyms: Optional[list[Linkage]] = []
    hypernyms: Optional[list[Linkage]] = []
    holonyms: Optional[list[Linkage]] = []
    expressions: Optional[list[Linkage]] = []
    coordinate_terms: Optional[list[Linkage]] = []
    proverbs: Optional[list[Linkage]] = []
    synonyms: Optional[list[Linkage]] = []
