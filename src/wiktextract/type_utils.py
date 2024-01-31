from typing import (
    Sequence,
    TypedDict,
)


class AltOf(TypedDict, total=False):
    word: str
    extra: str


class LinkageData(TypedDict, total=False):
    alt: str
    english: str
    extra: str
    qualifier: str
    roman: str
    ruby: list[Sequence[str]]
    sense: str
    source: str
    tags: list[str]
    taxonomic: str
    topics: list[str]
    urls: list[str]
    word: str


class ExampleData(TypedDict, total=False):
    english: str
    note: str
    ref: str
    roman: str
    ruby: list[Sequence[str]]
    text: str
    type: str


class FormOf(TypedDict, total=False):
    word: str
    extra: str
    roman: str


LinkData = list[Sequence[str]]


class TemplateData(TypedDict, total=False):
    args: dict[str, str]
    expansion: str
    name: str


class DescendantData(TypedDict, total=False):
    depth: int
    tags: list[str]
    templates: TemplateData
    text: str


class FormData(TypedDict, total=False):
    form: str
    head_nr: int
    ipa: str
    roman: str
    ruby: list[Sequence[str]]
    source: str
    tags: list[str]
    topics: list[str]


SoundData = TypedDict(
    "SoundData",
    {
        "audio": str,
        "audio-ipa": str,
        "enpr": str,
        "form": str,
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
    related: list[LinkageData]
    senseid: list[str]
    synonyms: list[LinkageData]
    tags: list[str]
    topics: list[str]
    wikidata: list[str]
    wikipedia: list[str]


class WordData(TypedDict, total=False):
    abbreviations: list[LinkageData]
    alt_of: list[AltOf]
    antonyms: list[LinkageData]
    categories: list[str]
    coordinate_terms: list[LinkageData]
    derived: list[LinkageData]
    descendants: list[DescendantData]
    etymology_number: int
    etymology_templates: list[TemplateData]
    etymology_text: str
    form_of: list[FormOf]
    forms: list[FormData]
    head_templates: list[TemplateData]
    holonyms: list[LinkageData]
    hyphenation: list[str]
    hypernyms: list[LinkageData]
    hyponyms: list[LinkageData]
    inflection_templates: list[TemplateData]
    instances: list[LinkageData]
    lang: str
    lang_code: str
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
