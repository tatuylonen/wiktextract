from pydantic import BaseModel, ConfigDict, Field


class JapaneseBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(JapaneseBaseModel):
    text: str = ""
    bold_text_offsets: list[tuple[int, int]] = []
    translation: str = ""
    bold_translation_offsets: list[tuple[int, int]] = []
    ref: str = ""
    ruby: list[tuple[str, ...]] = []
    roman: str = ""
    bold_roman_offsets: list[tuple[int, int]] = []


class AltForm(JapaneseBaseModel):
    word: str


class Sense(JapaneseBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    ruby: list[tuple[str, ...]] = []
    examples: list[Example] = []
    form_of: list[AltForm] = []
    notes: list[str] = []


class Form(JapaneseBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""


class Sound(JapaneseBaseModel):
    zh_pron: str = Field(default="", description="Chinese word pronunciation")
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    flac_url: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    homophones: list[str] = []
    form: str = ""
    roman: str = ""


class Translation(JapaneseBaseModel):
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Translation language name")
    word: str = Field(default="", description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""


class Linkage(JapaneseBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    ruby: list[tuple[str, ...]] = []
    sense: str = ""
    roman: str = ""
    literal_meaning: str = ""


class Descendant(JapaneseBaseModel):
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Language name")
    word: str = ""
    roman: str = ""
    descendants: list["Descendant"] = []
    sense: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []


class WordEntry(JapaneseBaseModel):
    model_config = ConfigDict(title="Japanese Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = ""
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    forms: list[Form] = []
    etymology_texts: list[str] = []
    sounds: list[Sound] = []
    translations: list[Translation] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    holonyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    derived: list[Linkage] = []
    contraction: list[Linkage] = []
    abbreviations: list[Linkage] = []
    related: list[Linkage] = []
    collocations: list[Linkage] = []
    proverbs: list[Linkage] = []
    phrases: list[Linkage] = []
    coordinate_terms: list[Linkage] = []
    cognates: list[Descendant] = []
    descendants: list[Descendant] = []
    anagrams: list[Linkage] = []
    notes: list[str] = []
