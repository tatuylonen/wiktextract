from pydantic import BaseModel, ConfigDict, Field


class BaseModelWrap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Translation(BaseModelWrap):
    word: str = Field(description="Translation term")
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(
        description="Localized language name of the translation term"
    )
    sense: str = Field(
        default="",
        description="An optional gloss describing the sense translated",
    )
    roman: str = Field(default="", description="Romanization of the word")
    tags: list[str] = []
    raw_tags: list[str] = []


class Linkage(BaseModelWrap):
    word: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sound(BaseModelWrap):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    ogg_url: str = ""
    oga_url: str = ""
    mp3_url: str = ""
    flac_url: str = ""
    tags: list[str] = Field(
        default=[], description="Specifying the variant of the pronunciation"
    )
    raw_tags: list[str] = []
    homophones: list[str] = Field(
        default=[], description="Words with same pronunciation"
    )


class Example(BaseModelWrap):
    text: str = Field(default="", description="Example usage sentence")
    translation: str = Field(
        default="", description="Spanish translation of the example sentence"
    )
    author: str = Field(default="", description="Author's name")
    title: str = Field(default="", description="Title of the reference")
    date: str = Field(default="", description="Original date")
    date_published: str = Field(default="", description="Date of publication")
    collection: str = Field(
        default="",
        description="Name of the collection the example was taken from",
    )
    editor: str = Field(default="", description="Editor")
    translator: str = Field(default="", description="Translator")
    source: str = Field(
        default="",
        description="Source of reference, corresponds to template parameter 'источник'",
    )


class AltForm(BaseModelWrap):
    word: str


class Sense(BaseModelWrap):
    raw_glosses: list[str] = Field(
        default=[],
        description="Raw gloss string for the word sense. This might contain tags and other markup.",
    )
    glosses: list[str] = Field(
        default=[],
        description="Gloss string for the word sense. This has been cleaned, and should be straightforward text with no tags.",
    )
    tags: list[str] = Field(
        default=[],
        description="List of tags affecting the word sense.",
    )
    raw_tags: list[str] = []
    topics: list[str] = []
    notes: list[str] = Field(
        default=[],
        description="List of notes for the word sense. Usually describing usage.",
    )
    categories: list[str] = Field(
        default=[],
        description="list of sense-disambiguated category names extracted from (a subset) of the Category links on the page",
    )
    examples: list[Example] = Field(default=[], description="List of examples")
    form_of: list[AltForm] = []


class Form(BaseModelWrap):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word
    extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="Russian Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = Field(default="", description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["ru"]
    )
    lang: str = Field(
        description="Localized language name of the word", examples=["Русский"]
    )
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )
    sounds: list[Sound] = []
    senses: list[Sense] = []
    translations: list[Translation] = []
    forms: list[Form] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    antonyms: list[Linkage] = Field(default=[], description="List of antonyms")
    anagrams: list[Linkage] = Field(default=[], description="List of anagrams")
    variants: list[Linkage] = Field(default=[], description="List of variants")
    hypernyms: list[Linkage] = Field(
        default=[], description="List of hypernyms"
    )
    hyponyms: list[Linkage] = Field(default=[], description="List of hyponyms")
    derived: list[Linkage] = Field(
        default=[], description="List of derived terms"
    )
    meronyms: list[Linkage] = Field(default=[], description="List of meronyms")
    synonyms: list[Linkage] = Field(default=[], description="List of synonyms")
    coordinate_terms: list[Linkage] = Field(
        default=[], description="List of coordinate terms"
    )
    holonyms: list[Linkage] = Field(default=[], description="List of holonyms")
    etymology_text: str = ""
