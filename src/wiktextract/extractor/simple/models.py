from pydantic import BaseModel, ConfigDict, Field

# Pydantic models are basically classes that take the place of the dicts
# used in the main English extractor. They use more resources, but also do
# a lot of validation work and are easier for the type-checker.

# Pydantic config stuff.
class SimpleEnglishBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        # We use pydantic mainly for the automatic validation; this
        # setting ensures the validation is done even when assigning something
        # after initialization, otherwise it doesn't check anything.
        validate_default=True,
    )

# Not an example, this is for example entries next to glosses.
class Example(SimpleEnglishBaseModel):
    text: str = Field(default="", description="Example usage sentence")
    author: str = Field(default="", description="Author's name")
    title: str = Field(default="", description="Title of the reference")
    # SEW example templates are simple and don't seem to have these
    # latter datas.
    # date: str = Field(default="", description="Original date")
    # date_published: str = Field(default="", description="Date of publication")
    # collection: str = Field(
    #     default="",
    #     description="Name of the collection the example was taken from",
    # )
    # editor: str = Field(default="", description="Editor")
    # translator: str = Field(default="", description="Translator")
    # source: str = Field(
    #     default="",
    #     description="Source of reference",
    # )

# General glass for "link to another related word", like synonym, antonym, etc.
# Instead of having classes for each, we have differnet fields of list[Linkage],
# like `synonyms: list[Linkage] = []`.
class Linkage(SimpleEnglishBaseModel):
    word: str
    # sense_index: str = ""
    # note: str = ""
    # raw_tags: list[str] = []
    # tags: list[str] = []

# Basically a line or lines of gloss, a meaning of a word. These are collected
# under the POS as a list.
class Sense(SimpleEnglishBaseModel):
    glosses: list[str] = []  # ["Gloss supercategory", "Specific gloss."]
    tags: list[str] = []
    raw_tags: list[str] = []
    # topics: list[str] = []  # XXX do these.
    categories: list[str] = []  # Wikipedia category link data; not printed.
    examples: list[Example] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    # ruby: list[tuple[str, ...]] = []

# An inflected form of the word, like `{ form: "bats", tags: ["plural"] }`
class Form(SimpleEnglishBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    # sense_index: str = ""


# A pronunciation or audio file. If you have a string of IPA or SAMPA or
# something else, that is extracted as its own Sound entry.
class Sound(SimpleEnglishBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    enpr: str = Field(default="", description="American Heritage Dictionary")
    sampa: str = Field(
        default="", description="Speech Assessment Methods Phonetic Alphabet"
    )
    audio: str = Field(default="", description="Audio file name")
    wav_url: str = Field(default="")
    ogg_url: str = Field(default="")
    mp3_url: str = Field(default="")
    oga_url: str = Field(default="")
    flac_url: str = Field(default="")
    lang_code: str = Field(default="en", description="Wiktionary language code")
    lang: str = Field(default="English", description="Localized language name")
    raw_tags: list[str] = []
    tags: list[str] = []
    rhymes: list[str] = []
    homophones: list[str] = []
    # text: str = ""  # Use raw_tags instead
    # "Temporary" field used to sort out different sound data between POSes when
    # they are originally found in one combined pronunciation section
    poses: list[str] = []

# Sometimes we collect raw template arguments separately, like in the main
# line English extractor where we keep data from etymology templates.
class TemplateData(SimpleEnglishBaseModel):
    name: str = Field(default="", description="Template's name.")
    args: dict[str, str] = Field(
        default={}, description="Arguments given to the template, if any."
    )
    expansion: str = Field(
        default="",
        description="The result of expanding the template.",
    )

# The highest level entry: This is returned from the program as a JSON object
# in the JSONL output.
class WordEntry(SimpleEnglishBaseModel):
    model_config = ConfigDict(title="Simple English Wiktionary")

    word: str = Field(description="Word string")
    # For Simple English, the language is always English
    forms: list[Form] = Field(default=[], description="Inflection forms list")
    # We do not use "en" as the default value here, because we also
    # remove all default values so that we don't have empty or meaningless
    # fields in the output.
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Localized language name")
    pos: str = Field(default="", description="Part of speech type")
    pos_title: str = ""  # `==Noun==`
    pos_num: int = -1  # `==Noun 2==` Default -1 gets removed.
    etymology_text: str = Field(
        default="", description="Etymology section as cleaned text."
    )
    etymology_templates: list[TemplateData] = Field(
        default=[],
        description="Templates and their arguments and expansions from the "
        "etymology section.",
    )
    # Simple Wiktionary doesn't have numbered etymology sections
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    sounds: list[Sound] = []
    tags: list[str] = []
    raw_tags: list[str] = []
    hyphenation: str = ""  # Should be a list `hyphenations`.
