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
    sense_index: str = ""
    sense: str = ""


class Translation(BaseModelWrap):
    word: str = Field(description="Translation term")
    lang_code: str = Field(
        description="Wiktionary language code of the translation term"
    )
    lang: str = Field(description="Name of the language of translation")
    sense_index: str = ""
    raw_tags: list[str] = Field(
        default=[],
        description="Tags specifying the translated term, usually gender",
    )
    tags: list[str] = []
    notes: list[str] = Field(default=[], description="A list of notes")
    roman: str = Field(
        default="", description="Transliteration in roman characters"
    )
    sense: str = ""


class Example(BaseModelWrap):
    text: str = Field(description="Example usage sentence")
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = Field(
        default="", description="Spanish translation of the example sentence"
    )
    bold_translation_offsets: list[tuple[int, int]] = []
    ref: str = ""


class AltForm(BaseModelWrap):
    word: str


class Sense(BaseModelWrap):
    glosses: list[str] = Field(
        default=[],
        description="list of gloss strings for the word sense."
        "This has been cleaned, and should be no tagging.",
    )
    raw_tags: list[str] = []
    tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = Field(
        default=[], description="Category links on the page"
    )
    examples: list[Example] = Field(default=[], description="List of examples")
    sense_index: str = Field(
        default="", description="Sense number used in Wiktionary"
    )
    form_of: list[AltForm] = []


class Sound(BaseModelWrap):
    ipa: str = Field("", description="International Phonetic Alphabet")
    audio: str = Field("", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
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
    row_span: int = Field(1, exclude=True)


class Hyphenation(BaseModelWrap):
    parts: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(BaseModelWrap):
    """
    WordEntry is a dictionary containing lexical information of a single word extracted from Wiktionary with wiktextract.
    """  # noqa:E501

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
    raw_tags: list[str] = []
    extra_sounds: dict[str, str] = {}
    forms: list[Form] = []
    hyphenations: list[Hyphenation] = []
    cognates: list[Linkage] = []
    morphologies: list[Linkage] = []
    descendants: list[Translation] = []
