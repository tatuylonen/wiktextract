from pydantic import BaseModel, ConfigDict, Field


class FrenchBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(FrenchBaseModel):
    text: str = Field(default="", description="Example usage sentence")
    translation: str = Field(
        default="", description="French translation of the example sentence"
    )
    roman: str = Field(
        default="", description="Romanization of the example sentence"
    )
    ref: str = Field(
        default="",
        description="Source of the sentence, like book title and page number",
    )
    time: str = Field(
        default="",
        description="For examples in 'Attestations historiques' section",
    )


class Form(FrenchBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    ipas: list[str] = []
    source: str = Field(
        default="",
        description="Form line template name or Conjugaison page title",
    )
    hiragana: str = ""
    roman: str = ""


class Sound(FrenchBaseModel):
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
    rhymes: str = ""
    categories: list[str] = Field(default=[], exclude=True)


class Translation(FrenchBaseModel):
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Translation language name")
    word: str = Field(default="", description="Translation term")
    sense: str = Field(default="", description="Translation gloss")
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )
    tags: list[str] = []
    raw_tags: list[str] = []
    roman: str = ""
    traditional_writing: str = Field(
        default="",
        description="Alternative writting for Chinese, Korean and Mongolian",
    )
    ruby: list[tuple[str, ...]] = Field(
        default=[], description="Japanese Kanji and furigana"
    )


class Linkage(FrenchBaseModel):
    word: str
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    roman: str = ""
    alt: str = Field(default="", description="Alternative form")
    translation: str = Field(default="", description="French translation")
    sense: str = Field(default="", description="Definition of the word")
    sense_index: int = Field(
        default=0, ge=0, description="Number of the definition, start from 1"
    )
    lang: str = Field(default="", description="Localized language name")
    lang_code: str = Field(default="", description="Wiktionary language code")


class AltForm(FrenchBaseModel):
    word: str


class Sense(FrenchBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    categories: list[str] = []
    examples: list[Example] = []
    note: str = ""
    alt_of: list[AltForm] = []
    form_of: list[AltForm] = []


class WordEntry(FrenchBaseModel):
    model_config = ConfigDict(title="French Wiktionary")

    word: str = Field(description="Word string")
    lang_code: str = Field(description="Wiktionary language code")
    lang: str = Field(description="Localized language name")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = Field(
        default="",
        description="Original POS title for matching etymology texts",
    )
    pos_id: str = Field(
        default="",
        description="POS id for matching etymology texts",
        exclude=True,
    )
    etymology_texts: list[str] = Field(default=[], description="Etymology list")
    etymology_examples: list[Example] = Field(
        default=[], description="Data in 'Attestations historiques' section"
    )
    senses: list[Sense] = Field(default=[], description="Sense list")
    forms: list[Form] = Field(default=[], description="Inflection forms list")
    sounds: list[Sound] = []
    translations: list[Translation] = []
    antonyms: list[Linkage] = []
    synonyms: list[Linkage] = []
    hyponyms: list[Linkage] = []
    hypernyms: list[Linkage] = []
    holonyms: list[Linkage] = []
    meronyms: list[Linkage] = []
    derived: list[Linkage] = []
    troponyms: list[Linkage] = []
    paronyms: list[Linkage] = []
    related: list[Linkage] = []
    abbreviation: list[Linkage] = []
    proverbs: list[Linkage] = []
    anagrams: list[Linkage] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    notes: list[str] = []
    tags: list[str] = []
    raw_tags: list[str] = []
