from pydantic import BaseModel, ConfigDict, Field


class VietnameseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(VietnameseBaseModel):
    text: str
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    literal_meaning: str = ""
    bold_literal_offsets: list[tuple[int, int]] = []
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    bold_roman_offsets: list[tuple[int, int]] = []
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = Field(default=[], exclude=True)


class AltForm(VietnameseBaseModel):
    word: str
    roman: str = ""


class Classifier(VietnameseBaseModel):
    classifier: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class Sense(VietnameseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    categories: list[str] = []
    topics: list[str] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []
    alt_of: list[AltForm] = []
    classifiers: list[Classifier] = []


class Linkage(VietnameseBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    sense: str = ""
    other: str = ""
    translation: str = ""
    senses: list[str] = []
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    categories: list[str] = Field(default=[], exclude=True)


class Form(VietnameseBaseModel):
    form: str
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    sense: str = ""
    ruby: list[tuple[str, ...]] = []


class Translation(VietnameseBaseModel):
    lang_code: str = Field(
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(description="Translation language name")
    word: str = Field(description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    lit: str = Field(default="", description="Literal translation")
    source: str = ""
    other: str = ""


class Sound(VietnameseBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    tags: list[str] = []
    raw_tags: list[str] = []
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    flac_url: str = ""
    rhymes: str = ""
    homophone: str = ""
    zh_pron: str = ""
    roman: str = ""
    other: str = ""


class Hyphenation(VietnameseBaseModel):
    parts: list[str] = []


class Descendant(VietnameseBaseModel):
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Language name")
    word: str = ""
    roman: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    descendants: list["Descendant"] = []
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )
    sense: str = ""


class WordEntry(VietnameseBaseModel):
    model_config = ConfigDict(title="Vietnamese Wiktionary")
    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    derived: list[Linkage] = []
    related: list[Linkage] = []
    holonyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    forms: list[Form] = []
    translations: list[Translation] = []
    sounds: list[Sound] = []
    etymology_text: str = ""
    hyphenations: list[Hyphenation] = []
    notes: list[str] = []
    anagrams: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    reduplicatives: list[Linkage] = []
    literal_meaning: str = ""
    redirects: list[str] = []
    descendants: list[Descendant] = []
