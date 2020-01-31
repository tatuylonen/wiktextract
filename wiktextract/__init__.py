# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See LICENSE and https://ylonen.org

from wiktextract.wiktionary import parse_wiktionary
from wiktextract import wiktlangs
from wiktextract.page import WiktionaryConfig, PARTS_OF_SPEECH, clean_value

__all__ = (
    "WiktionaryConfig",
    "parse_wiktionary",
    "wiktlangs",
    "PARTS_OF_SPEECH",
)
