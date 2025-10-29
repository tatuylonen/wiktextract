from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Pydantic models are basically classes that take the place of the dicts
# used in the main English extractor. They use more resources, but also do
# a lot of validation work and are easier for the type-checker.


# Search and replace Greek with `Language Name`
# Pydantic config stuff.
class GreekBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        # We use pydantic mainly for the automatic validation; this
        # setting ensures the validation is done even when assigning something
        # after initialization, otherwise it doesn't check anything.
        validate_assignment=True,
        validate_default=True,
    )


# Examples and quotations in glosses
class Example(GreekBaseModel):
    text: str = Field(default="", description="Example usage sentence")
    type: str = ""  # example or quotation etc.
    translation: str = Field(
        default="",
        description="Greek Translation of the example sentence",
    )
    # author: str = Field(default="", description="Author's name")
    # title: str = Field(default="", description="Title of the reference")
    # ref: str = Field(default="", description="Raw reference string")
    # url: str = Field(
    #     default="", description="A web link. Not necessarily well-formated."
    # )
    # date: str = Field(default="", description="Original date")
    # date_published: str = Field(default="", description="Date of publication")
    # collection: str = Field(
    #     default="",
    #     description="Name of the collection the example was taken from",
    # )
    # pages: str = Field(default="", description="Page numbers")
    # year: str = Field(default="", description="Year of publication")
    # publisher: str = Field(default="", description="Published by")
    # editor: str = Field(default="", description="Editor")
    # translator: str = Field(default="", description="Translator")
    # source: str = Field(
    #     default="",
    #     description="Source of reference",
    # )
    # collection: str = Field(
    #     default="",
    #     description="Name of collection that reference was published in",
    # )
    # volume: str = Field(default="", description="Volume number")
    # comment: str = Field(default="", description="Comment on the reference")
    # accessdate: str = Field(
    #     default="", description="Date of access of online reference"
    # )
    # date: str = Field(default="", description="Date of publication")
    # number: str = Field(default="", description="Issue number")
    # # chapter: Optional[str] = Field(default=None, description="Chapter name")
    # place: str = Field(default="", description="Place of publication")
    # edition: str = Field(default="", description="Edition number")
    # isbn: str = Field(default="", description="ISBN number")
    # literal_meaning: str = ""


class Translation(GreekBaseModel):
    sense: str = Field(
        default="", description="A gloss of the sense being translated"
    )
    word: str = Field(default="", description="Translation term")
    lang_code: str = Field(
        default="",
        description="Wiktionary language code of the translation term",
    )
    lang: str = Field(default="", description="Localized language name")
    # uncertain: bool = Field(
    #     default=False, description="Translation marked as uncertain"
    # )
    roman: str = Field(
        default="", description="Transliteration to Roman characters"
    )
    sense_index: str = ""
    # note: str = ""
    # literal_meaning: str = ""
    raw_tags: list[str] = []
    tags: list[str] = []
    # notes: list[str] = Field(default=[], description="A list of notes")


# General glass for "link to another related word", like synonym, antonym, etc.
# Instead of having classes for each, we have differnet fields of list[Linkage],
# like `synonyms: list[Linkage] = []`.
class Linkage(GreekBaseModel):
    word: str
    # translation: str
    # extra: str
    # roman: str
    # sense: str
    # sense_index: str = ""
    # note: str = ""
    raw_tags: list[str] = []
    tags: list[str] = []
    topics: list[str] = []
    # urls: list[str]
    examples: list[str] = []


class FormOf(GreekBaseModel):
    word: str
    # extra: str
    # roman: str


# Basically a line or lines of gloss, a meaning of a word. These are collected
# under the POS as a list.
class Sense(GreekBaseModel):
    glosses: list[str] = []  # ["Gloss supercategory", "Specific gloss."]
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    form_of: list[FormOf] = []
    # alt_of : list[FormOf] = []
    # compound_of: list[FormOf] = []
    # topics: list[str] = []
    categories: list[str] = []  # Wikipedia category link data; not printed.
    examples: list[Example] = []
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []
    # holonyms: list[Linkage] = []
    # hypernyms: list[Linkage] = []
    # hyponyms: list[Linkage] = []
    # instances: list[Linkage] = []
    # meronyms: list[Linkage] = []
    related: list[Linkage] = []
    # links: list[list[str]] = []
    # coordinate_terms: list[Linkage] = []
    # ruby: list[tuple[str, ...]] = []
    # sense_index: str = Field(default="", description="Sense number used in "
    #                                                  "Wiktionary")
    # head_nr: int = -1
    # wikidata: list[str] = []
    # wikipedia: list[str] = []

    def merge(self, other: "Sense") -> None:
        """Combine the fields of this Sense with another Sense"""
        self.tags = sorted(set(self.tags + other.tags))
        self.raw_tags = sorted(set(self.raw_tags + other.raw_tags))
        self.categories = sorted(set(self.categories + other.categories))
        self.examples.extend(other.examples)
        self.synonyms.extend(other.synonyms)
        self.antonyms.extend(other.antonyms)
        self.related.extend(other.related)


FormSource = Literal[
    "conjugation",
    "declension",
    "header",
    "inflection",  # Can be further narrowed to conjugation/declension
    "linkage",
    "",
]


# An inflected form of the word, like `{ form: "bats", tags: ["plural"] }`
class Form(GreekBaseModel):
    form: str = ""
    tags: list[str] = []
    raw_tags: list[str] = []
    topics: list[str] = []
    # head_nr: int = -1
    ipa: str = ""
    # roman: str = ""
    # ruby: list[tuple[str, str]] = []
    source: FormSource = ""
    # sense_index: str = ""


# A pronunciation or audio file. If you have a string of IPA or SAMPA or
# something else, that is extracted as its own Sound entry.
class Sound(GreekBaseModel):
    ipa: str = Field(default="", description="International Phonetic Alphabet")
    # enpr: str = Field(default="", description="American Heritage Dictionary")
    # sampa: str = Field(
    #     default="", description="Speech Assessment Methods Phonetic Alphabet"
    # )
    audio: str = Field(default="", description="Audio file name")
    # wav_url: str = Field(default="")
    # ogg_url: str = Field(default="")
    # mp3_url: str = Field(default="")
    # oga_url: str = Field(default="")
    # flac_url: str = Field(default="")
    lang_code: str = Field(default="", description="Wiktionary language code")
    lang: str = Field(default="", description="Localized language name")
    raw_tags: list[str] = []
    tags: list[str] = []
    # rhymes: list[str] = []
    homophones: list[str] = []
    # text: str = ""  # Use raw_tags instead
    # "Temporary" field used to sort out different sound data between POSes when
    # they are originally found in one combined pronunciation section
    poses: list[str] = []


# Sometimes we collect raw template arguments separately, like in the main
# line English extractor where we keep data from etymology templates.
class TemplateData(GreekBaseModel):
    name: str = Field(default="", description="Template's name.")
    args: dict[str, str] = Field(
        default={}, description="Arguments given to the template, if any."
    )
    expansion: str = Field(
        default="",
        description="The result of expanding the template.",
    )


# The highest level entry: This is returned from the program as a JSON object
# in the JSONL output. These are prototypically Part of Speech sections,
# like "Noun" under a higher level section like "Etymology".
class WordEntry(GreekBaseModel):
    model_config = ConfigDict(title="Greek Wiktionary")

    word: str = Field(description="Word string")
    # original_title: str = ""
    forms: list[Form] = Field(default=[], description="Inflection forms list")
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
    # For sections like "Etymology 1"
    etymology_number: int = -1
    senses: list[Sense] = []
    title: str = Field(default="", description="Redirect page source title")
    redirect: str = Field(default="", description="Redirect page target title")
    categories: list[str] = []
    sounds: list[Sound] = []
    tags: list[str] = []
    topics: list[str] = []
    raw_tags: list[str] = []
    hyphenation: str = ""  # Should be a list `hyphenations`.
    head_templates: list[TemplateData] = []
    # alt_of: list[FormOf] = []
    form_of: list[FormOf] = []
    antonyms: list[Linkage] = []
    # coordinate_terms: list[Linkage] = []
    derived: list[Linkage] = []
    # descendants: list[Linkage] = []
    # holonyms: list[Linkage] = []
    # hypernyms: list[Linkage] = []
    # hyponyms: list[Linkage] = []
    # meronyms: list[Linkage] = []
    # instances: list[Linkage] = []
    # troponyms: list[Linkage] = []
    # inflection_templates: list[TemplateData] = []
    # info_template: list[TemplateData] = []
    # literal_meaning: str = ""
    related: list[Linkage] = []
    synonyms: list[Linkage] = []
    translations: list[Translation] = []
    # wikidata: list[str] = []
    # wikipedia: list[str] = []
