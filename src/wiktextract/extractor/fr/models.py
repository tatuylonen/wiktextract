from pydantic import BaseModel, ConfigDict, Field


class FrenchBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )


class Example(FrenchBaseModel):
    text: str = Field("", description="Example usage sentence")
    translation: str = Field(
        "", description="French translation of the example sentence"
    )
    roman: str = Field("", description="Romanization of the example sentence")
    ref: str = Field(
        "",
        description="Source of the sentence, like book title and page number",
    )


class Form(FrenchBaseModel):
    form: str = ""
    tags: list[str] = []
    ipas: list[str] = []
    source: str = Field(
        "", description="Form line template name or Conjugaison page title"
    )
    hiragana: str = ""
    roman: str = ""


class Sound(FrenchBaseModel):
    zh_pron: str = Field("", description="Chinese word pronunciation")
    ipa: str = Field("", description="International Phonetic Alphabet")
    audio: str = Field("", description="Audio file name")
    wav_url: str = ""
    oga_url: str = ""
    ogg_url: str = ""
    mp3_url: str = ""
    opus_url: str = ""
    tags: list[str] = []


class Translation(FrenchBaseModel):
    lang_code: str = Field(
        "", description="Wiktionary language code of the translation term"
    )
    lang: str = Field("", description="Translation language name")
    word: str = Field("", description="Translation term")
    sense: str = Field("", description="Translation gloss")
    sense_index: int = Field(
        0, ge=0, description="Number of the definition, start from 1"
    )
    tags: list[str] = []
    roman: str = ""
    traditional_writing: str = Field(
        "", description="Alternative writting for Chinese, Korean and Mongolian"
    )


class Linkage(FrenchBaseModel):
    word: str
    tags: list[str] = []
    roman: str = ""
    alt: str = Field("", description="Alternative form")
    translation: str = Field("", description="French translation")
    sense: str = Field("", description="Definition of the word")
    sense_index: int = Field(
        0, ge=0, description="Number of the definition, start from 1"
    )
    lang: str = Field("", description="Localized language name")
    lang_code: str = Field("", description="Wiktionary language code")


class AltForm(FrenchBaseModel):
    word: str


class Sense(FrenchBaseModel):
    glosses: list[str] = []
    tags: list[str] = []
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
    pos: str = Field("", description="Part of speech type")
    pos_title: str = Field(
        "", description="Original POS title for matching etymology texts"
    )
    etymology_texts: list[str] = Field([], description="Etymology list")
    senses: list[Sense] = Field([], description="Sense list")
    forms: list[Form] = Field([], description="Inflection forms list")
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
    title: str = Field("", description="Redirect page source title")
    redirect: str = Field("", description="Redirect page target title")
    categories: list[str] = []
    notes: list[str] = []
    tags: list[str] = []
