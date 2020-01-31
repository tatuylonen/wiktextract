# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See LICENSE and https://ylonen.org

from .wiktionary import parse_wiktionary
from . import wiktlangs
from .config import WiktionaryConfig
from .page import clean_value
from .parts_of_speech import PARTS_OF_SPEECH

__all__ = (
    "WiktionaryConfig",
    "parse_wiktionary",
    "wiktlangs",
    "PARTS_OF_SPEECH",
)
