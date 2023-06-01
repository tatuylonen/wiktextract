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
        "thesaurus_db_path",
        "thesaurus_db_conn",
        )

    def __init__(self, wtp: Wtp, config: WiktionaryConfig):
        from .thesaurus import init_thesaurus_db

        self.config = config
        self.wtp = wtp
        self.lang = None
        self.word = None
        self.pos = None
        self.thesaurus_db_path = wtp.db_path.with_stem(
            f"wiktextract_thesaurus_{wtp.lang_code}_db"
        )
        self.thesaurus_db_conn = init_thesaurus_db(self.thesaurus_db_path)
