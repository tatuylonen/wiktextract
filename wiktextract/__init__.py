# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See LICENSE and https://ylonen.org

from .wiktionary import (parse_wiktionary, reprocess_wiktionary,
                         extract_namespace)
from .config import WiktionaryConfig
from .wxr_context import WiktextractContext
from .page import parse_page
from .parts_of_speech import PARTS_OF_SPEECH
from .thesaurus import extract_thesaurus_data
from .categories import extract_categories
from .tags import sort_tags, tag_categories
from .form_descriptions import valid_tags  # This file adds uppercase tags

__all__ = (
    "WiktextractContext",
    "WiktionaryConfig",
    "parse_wiktionary",
    "reprocess_wiktionary",
    "PARTS_OF_SPEECH",
    "parse_page",
    "extract_thesaurus_data",
    "extract_namespace",
    "extract_categories",
    "sort_tags",
    "tag_categories",
    "valid_tags",
)
