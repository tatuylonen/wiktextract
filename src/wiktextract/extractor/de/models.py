from pydantic import BaseModel, ConfigDict, Field


class GermanBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Linkage(GermanBaseModel):
    word: str
    sense_index: str = ""
    note: str = ""
    raw_tags: list[str] = []
    tags: list[str] = []
    topics: list[str] = []


class Translation(GermanBaseModel):
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
    sense_index: str = ""
    raw_tags: list[str] = []
    tags: list[str] = []
    notes: list[str] = Field(default=[], description="A list of notes")
    other: str = ""


class Example(GermanBaseModel):
    text: str = Field(description="Example usage sentence")
    bold_text_offsets: list[tuple[int, int]] = Field(
        default=[], description="Italic words"
    )
    translation: str = Field(
        default="", description="German translation of the example sentence"
    )
    bold_translation_offsets: list[tuple[int, int]] = Field(
        default=[], description="Italic words"
    )
    raw_tags: list[str] = []
    tags: list[str] = []
    ref: str = Field(default="", description="Raw reference string")


class AltForm(GermanBaseModel):
    word: str


class Sense(GermanBaseModel):
    glosses: list[str] = []
    raw_tags: list[str] = []
    tags: list[str] = []
    categories: list[str] = []
    examples: list["Example"] = Field(
        default=[], description="List of examples"
    )
    sense_index: str = Field(
        default="", description="Sense number used in Wiktionary"
    )
    topics: list[str] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []


class Sound(GermanBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = Field(default="")
    ogg_url: str = Field(default="")
    mp3_url: str = Field(default="")
    oga_url: str = Field(default="")
    flac_url: str = Field(default="")
    opus_url: str = Field(default="")
    raw_tags: list[str] = []
    tags: list[str] = []
    rhymes: str = ""
    categories: list[str] = Field(default=[], exclude=True)


class Form(GermanBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    source: str = ""
    sense_index: str = ""
    topics: list[str] = []
    pronouns: list[str] = []
    article: str = ""


class Descendant(GermanBaseModel):
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Language name")
    word: str = ""
    roman: str = ""
    sense_index: str = ""


class Hyphenation(GermanBaseModel):
    parts: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(GermanBaseModel):
    """
    WordEntry is a dictionary containing lexical information of a single word
    extracted from Wiktionary with wiktextract.
    """

    model_config = ConfigDict(title="German Wiktionary")

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
    etymology_texts: list[str] = []
    forms: list[Form] = []
    meronyms: list[Linkage] = []
    hyphenations: list[Hyphenation] = []
    notes: list[str] = []
    related: list[Linkage] = []
    descendants: list[Descendant] = []
