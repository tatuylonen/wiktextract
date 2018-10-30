# This file defines the public exports from the wiktextract module.
#
# Copyright (c) 2018 Tatu Ylonen.  See LICENSE.

from wiktextract.wiktionary import parse_wiktionary
from wiktextract import wiktlangs

__all__ = ["parse_wiktionary", "wiktlangs"]
