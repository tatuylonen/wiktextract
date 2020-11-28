# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See LICENSE and https://ylonen.org

from .wiktionary import parse_wiktionary, reprocess_wiktionary
from .config import WiktionaryConfig
from .page import clean_value, parse_page
from .parts_of_speech import PARTS_OF_SPEECH

__all__ = (
    "WiktionaryConfig",
    "parse_wiktionary",
    "reprocess_wiktionary",
    "PARTS_OF_SPEECH",
    "parse_page",
)
