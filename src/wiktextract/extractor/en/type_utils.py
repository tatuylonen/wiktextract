from typing import (
    Sequence,
    TypedDict,
    Union,
)

from wikitextprocessor.core import TemplateArgs


class AltOf(TypedDict, total=False):
    word: str
    extra: str


class LinkageData(TypedDict, total=False):
    alt: str
    english: str
    extra: str
    qualifier: str
    roman: str
    ruby: Union[list[Sequence[str]], list[tuple[str, str]]]
    sense: str
    source: str
    tags: list[str]
    taxonomic: str
    topics: list[str]
    urls: list[str]
    word: str


class ExampleData(TypedDict, total=False):
    english: str
    bold_english_offsets: list[tuple[int, int]]
    note: str
    ref: str
    roman: str
    bold_roman_offsets: list[tuple[int, int]]
    ruby: Union[list[tuple[str, str]], list[Sequence[str]]]
    text: str
    bold_text_offsets: list[tuple[int, int]]
    type: str
    literal_meaning: str
    bold_literal_offsets: list[tuple[int, int]]
    tags: list[str]
    raw_tags: list[str]


class FormOf(TypedDict, total=False):
    word: str
    extra: str
    roman: str


LinkData = list[Sequence[str]]


class PlusObjTemplateData(TypedDict, total=False):
    tags: list[str]
    words: list[str]
    meaning: str


ExtraTemplateData = Union[PlusObjTemplateData]


class TemplateData(TypedDict, total=False):
    args: TemplateArgs
    expansion: str
    name: str
    extra_data: ExtraTemplateData


class DescendantData(TypedDict, total=False):
    depth: int
    tags: list[str]
    templates: list[TemplateData]
    text: str


class FormData(TypedDict, total=False):
    form: str
    head_nr: int
    ipa: str
    roman: str
    ruby: Union[list[tuple[str, str]], list[Sequence[str]]]
    source: str
    tags: list[str]
    raw_tags: list[str]
    topics: list[str]


class Hyphenation(TypedDict, total=False):
    parts: list[str]
    tags: list[str]


SoundData = TypedDict(
    "SoundData",
    {
        "audio": str,
        "audio-ipa": str,
        "enpr": str,
        "form": str,
        "hangeul": str,
        "homophone": str,
        "ipa": str,
        "mp3_url": str,
        "note": str,
        "ogg_url": str,
        "other": str,
        "rhymes": str,
        "tags": list[str],
        "text": str,
        "topics": list[str],
        "zh-pron": str,
    },
    total=False,
)


class TranslationData(TypedDict, total=False):
    alt: str
    code: str
    english: str
    lang: str
    note: str
    roman: str
    sense: str
    tags: list[str]
    taxonomic: str
    topics: list[str]
    word: str


# Xxyzz's East Asian etymology example data
class EtymologyExample(TypedDict, total=False):
    english: str
    raw_tags: list[str]
    ref: str
    roman: str
    tags: list[str]
    text: str
    type: str


class ReferenceData(TypedDict, total=False):
    text: str
    refn: str


class AttestationData(TypedDict, total=False):
    date: str
    references: list[ReferenceData]


class SenseData(TypedDict, total=False):
    alt_of: list[AltOf]
    antonyms: list[LinkageData]
    categories: list[str]
    compound_of: list[AltOf]
    coordinate_terms: list[LinkageData]
    examples: list[ExampleData]
    form_of: list[FormOf]
    glosses: list[str]
    head_nr: int
    holonyms: list[LinkageData]
    hypernyms: list[LinkageData]
    hyponyms: list[LinkageData]
    instances: list[LinkageData]
    links: list[LinkData]
    meronyms: list[LinkageData]
    qualifier: str
    raw_glosses: list[str]
    related: list[LinkageData]  # also used for "alternative forms"
    senseid: list[str]
    synonyms: list[LinkageData]
    tags: list[str]
    taxonomic: str
    topics: list[str]
    wikidata: list[str]
    wikipedia: list[str]
    attestations: list[AttestationData]


class WordData(TypedDict, total=False):
    abbreviations: list[LinkageData]
    alt_of: list[AltOf]
    antonyms: list[LinkageData]
    categories: list[str]
    coordinate_terms: list[LinkageData]
    derived: list[LinkageData]
    descendants: list[DescendantData]
    etymology_examples: list[EtymologyExample]
    etymology_number: int
    etymology_templates: list[TemplateData]
    etymology_text: str
    form_of: list[FormOf]
    forms: list[FormData]
    head_templates: list[TemplateData]
    holonyms: list[LinkageData]
    hyphenation: list[str]  # Being deprecated
    hyphenations: list[Hyphenation]
    hypernyms: list[LinkageData]
    hyponyms: list[LinkageData]
    inflection_templates: list[TemplateData]
    info_templates: list[TemplateData]
    instances: list[LinkageData]
    lang: str
    lang_code: str
    literal_meaning: str
    meronyms: list[LinkageData]
    original_title: str
    pos: str
    proverbs: list[LinkageData]
    redirects: list[str]
    related: list[LinkageData]
    senses: list[SenseData]
    sounds: list[SoundData]
    synonyms: list[LinkageData]
    translations: list[TranslationData]
    troponyms: list[LinkageData]
    wikidata: list[str]
    wikipedia: list[str]
    word: str
    anagrams: list[LinkageData] = []
