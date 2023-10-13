# Wiktextract context object
import sqlite3

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
            f"{wtp.db_path.stem}_thesaurus"
        )
        self.thesaurus_db_conn = (
            init_thesaurus_db(self.thesaurus_db_path)
            if config.extract_thesaurus_pages
            else None
        )

    def reconnect_databases(self, check_same_thread: bool = True) -> None:
        # `multiprocessing.pool.Pool.imap()` runs in another thread, if the db
        # connection is used to create iterable data for `imap`,
        # `check_same_thread` must be `False`.
        if self.config.extract_thesaurus_pages:
            self.thesaurus_db_conn = sqlite3.connect(
                self.thesaurus_db_path, check_same_thread=check_same_thread
            )
        self.wtp.db_conn = sqlite3.connect(
            self.wtp.db_path, check_same_thread=check_same_thread
        )

    def remove_unpicklable_objects(self) -> None:
        # remove these variables before passing the `WiktextractContext` object
        # to worker processes
        if self.config.extract_thesaurus_pages:
            self.thesaurus_db_conn.close()
        self.thesaurus_db_conn = None
        self.wtp.db_conn.close()
        self.wtp.db_conn = None
        self.wtp.lua = None
        self.wtp.lua_invoke = None
        self.wtp.lua_reset_env = None
        self.wtp.lua_clear_loaddata_cache = None
