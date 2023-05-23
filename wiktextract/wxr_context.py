# Wiktextract context object
from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig


class WiktextractContext:
    __slots__ = (
        "wtp",
        "config",
        "lang",
        "word",
        "pos",
        )

    def __init__(self, wtp: Wtp, config: WiktionaryConfig):
        self.config = config
        self.wtp = wtp
        self.lang = None
        self.word = None
        self.pos = None
