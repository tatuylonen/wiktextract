# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See LICENSE and https://ylonen.org

from wiktextract.wiktionary import parse_wiktionary, PARTS_OF_SPEECH
from wiktextract import wiktlangs

__all__ = ("parse_wiktionary", "wiktlangs", "PARTS_OF_SPEECH")
