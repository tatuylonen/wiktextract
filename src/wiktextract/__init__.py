# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See LICENSE and https://ylonen.org

from .categories import extract_categories
from .config import WiktionaryConfig
from .page import parse_page
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
    "parse_page",
    "extract_thesaurus_data",
    "extract_namespace",
    "extract_categories",
)
