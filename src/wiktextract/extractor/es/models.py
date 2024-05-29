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
    note: str = ""
    alternative_spelling: str = Field(
        default="", description="Alternative spelling of the word"
    )
    senseid: str = ""


class Translation(BaseModelWrap):
    word: str = Field(description="Translation term")
    lang_code: str = Field(
        description="Wiktionary language code of the translation term"
    )
    lang: str = Field(description="Name of the language of translation")
    senseids: list[str] = Field(
        default=[],
        description="List of senseids where this translation applies",
    )
    raw_tags: list[str] = Field(
        default=[],
        description="Tags specifying the translated term, usually gender information",
    )
    tags: list[str] = []
    notes: list[str] = Field(default=[], description="A list of notes")
    roman: str = Field(
        default="", description="Transliteration in roman characters"
    )


class TemplateData(BaseModelWrap):
    name: str = Field(default="", description="Template's name.")
    args: dict[str, str] = Field(
        default={}, description="Arguments given to the template, if any."
    )
    expansion: str = Field(
        default="",
        description="The result of expanding the template, the final text it outputs.",
    )


class Example(BaseModelWrap):
    text: str = Field(description="Example usage sentence")
    translation: str = Field(
        default="", description="Spanish translation of the example sentence"
    )
    ref: str = ""
    example_templates: list[TemplateData] = []


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
    topics: list[str] = []
    categories: list[str] = Field(
        default=[],
        description="list of sense-disambiguated category names extracted from (a subset) of the Category links on the page",
    )
    examples: list[Example] = Field(default=[], description="List of examples")
    # subsenses: list["Sense"] = Field(
    #     default=[], description="List of subsenses"
    # )
    senseid: str = Field(
        default="", description="Sense number used in Wiktionary"
    )


class Sound(BaseModelWrap):
    ipa: str = Field("", description="International Phonetic Alphabet")
    audio: str = Field("", description="Audio file name")
    wav_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    flac_url: str = ""
    roman: str = Field("", description="Translitaration to Roman characters")
    syllabic: str = Field("", description="Syllabic transcription")
    raw_tags: list[str] = Field(
        [], description="Specifying the variant of the pronunciation"
    )
    tags: list[str] = []
    alternative: str = Field(
        "", description="Alternative spelling with same pronunciation"
    )
    note: str = ""
    not_same_pronunciation: bool = Field(
        False, description="This is `True` for the 'Variantes' row"
    )
    rhymes: str = ""
    homophone: str = ""


class Form(BaseModelWrap):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="Spanish Wiktionary")

    word: str = Field(description="word string")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = Field(default="", description="Original POS title")
    lang_code: str = Field(
        description="Wiktionary language code", examples=["es"]
    )
    lang: str = Field(
        description="Localized language name of the word", examples=["español"]
    )
    senses: list[Sense] = []
    categories: list[str] = Field(
        default=[],
        description="list of non-disambiguated categories for the word",
    )
    sounds: list[Sound] = []
    translations: list[Translation] = []
    etymology_text: str = Field(
        default="", description="Etymology section as cleaned text."
    )
    etymology_templates: list[TemplateData] = Field(
        default=[],
        description="Templates and their arguments and expansions from the etymology section.",
    )
    etymology_number: int = Field(
        default=0,
        description="For words with multiple numbered etymologies, this contains the number of the etymology under which this entry appeared.",
    )
    antonyms: list[Linkage] = []
    compounds: list[Linkage] = []
    derived: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    idioms: list[Linkage] = []
    meronyms: list[Linkage] = []
    related: list[Linkage] = []
    synonyms: list[Linkage] = []
    proverbs: list[Linkage] = []
    tags: list[str] = []
    extra_sounds: dict[str, str] = {}
    forms: list[Form] = []
