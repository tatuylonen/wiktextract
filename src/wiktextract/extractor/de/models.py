from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Linkage(BaseModelWrap):
    word: str
    sense_id: str = ""


class Translation(BaseModelWrap):
    sense: str = Field(
        default="", description="A gloss of the sense being translated"
    )
    word: str = Field(default="", description="Translation term")
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Localized language name")
    uncertain: bool = Field(
        default=False, description="Translation marked as uncertain"
    )
    roman: str = Field(
        default="", description="Transliteration to Roman characters"
    )
    sense_id: str = ""
    raw_tags: list[str] = Field(
        default=[],
        description="Tags specifying the translated term, usually gender information",
    )
    tags: list[str] = []
    notes: list[str] = Field(default=[], description="A list of notes")


class Example(BaseModelWrap):
    text: str = Field(default="", description="Example usage sentence")
    # translation: Optional[str] = Field(
    #     default=None, description="Spanish translation of the example sentence"
    # )
    raw_ref: str = Field(default="", description="Raw reference string")
    url: str = Field(
        default="", description="A web link. Not necessarily well-formated."
    )
    author: str = Field(default="", description="Author's name")
    title: str = Field(default="", description="Title of the reference")
    title_complement: str = Field(
        default="", description="Complement to the title"
    )
    pages: str = Field(default="", description="Page numbers")
    year: str = Field(default="", description="Year of publication")
    publisher: str = Field(default="", description="Published by")
    editor: str = Field(default="", description="Editor")
    translator: str = Field(default="", description="Translator")
    collection: str = Field(
        default="",
        description="Name of collection that reference was published in",
    )
    volume: str = Field(default="", description="Volume number")
    comment: str = Field(default="", description="Comment on the reference")
    day: str = Field(default="", description="Day of publication")
    month: str = Field(default="", description="Month of publication")
    accessdate: str = Field(
        default="", description="Date of access of online reference"
    )
    date: str = Field(default="", description="Date of publication")
    number: str = Field(default="", description="Issue number")
    # journal: Optional[str] = Field(default=None, description="Name of journal")
    # chapter: Optional[str] = Field(default=None, description="Chapter name")
    place: str = Field(default="", description="Place of publication")
    # editor: Optional[str] = Field(default=None, description="Editor")
    edition: str = Field(default="", description="Edition number")
    isbn: str = Field(default="", description="ISBN number")


class Sense(BaseModelWrap):
    glosses: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging.",
    )
    raw_tags: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense (usually only one). This has been cleaned, and should be straightforward text with no tagging.",
    )
    tags: list[str] = []
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
    senseid: str = Field(
        default="", description="Sense number used in Wiktionary"
    )


class Sound(BaseModelWrap):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    # phonetic_transcription: list[str] = Field(
    #     default=[], description="Phonetic transcription, less exact than IPA."
    # )
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = Field(default="")
    ogg_url: str = Field(default="")
    mp3_url: str = Field(default="")
    oga_url: str = Field(default="")
    flac_url: str = Field(default="")
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Localized language name")
    # roman: list[str] = Field(
    #     default=[], description="Translitaration to Roman characters"
    # )
    # syllabic: list[str] = Field(
    #     default=[], description="Syllabic transcription"
    # )
    raw_tags: list[str] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )
    tags: list[str] = []


class Form(BaseModelWrap):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    source: str = ""


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word
    extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="German Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default="", description="Part of speech type")
    other_pos: list[str] = []
    # pos_title: str = Field(default=None, description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["es"]
    )
    lang: str = Field(
        description="Localized language name of the word", examples=["español"]
    )
    senses: list[Sense] = []
    # categories: list[str] = Field(
    #     default=[],
    #     description="list of non-disambiguated categories for the word",
    # )
    translations: list[Translation] = []
    sounds: list[Sound] = []
    antonyms: list[Linkage] = []
    derived: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    holonyms: list[Linkage] = []
    expressions: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    proverbs: list[Linkage] = []
    synonyms: list[Linkage] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    redirects: list[str] = []
    etymology_text: str = ""
    forms: list[Form] = []
