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

    def __init__(self, config, wtp):
        assert isinstance(config, WiktionaryConfig)
        assert isinstance(wtp, Wtp)
        self.config = config
        self.wtp = wtp
        self.lang = None
        self.word = None
        self.pos = None
