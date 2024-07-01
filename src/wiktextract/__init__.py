# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See LICENSE and https://ylonen.org

from .categories import extract_categories
from .config import WiktionaryConfig
from .form_descriptions import valid_tags  # This file adds uppercase tags
from .page import parse_page
from .parts_of_speech import PARTS_OF_SPEECH
from .tags import sort_tags, tag_categories
from .thesaurus import extract_thesaurus_data
from .wiktionary import (
                         extract_namespace,
                         parse_wiktionary,
                         reprocess_wiktionary,
)
from .wxr_context import WiktextractContext

__all__ = (
    "WiktionaryConfig",
    "WiktextractContext",
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
