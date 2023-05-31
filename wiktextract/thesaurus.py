# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import importlib
import sqlite3
import tempfile

from pathlib import Path
from typing import Tuple, Optional

from wiktextract.wxr_context import WiktextractContext


def extract_thesaurus_data(wxr: WiktextractContext) -> None:
    thesaurus_extractor_mod = importlib.import_module(
        f"wiktextract.extractor/{wxr.wtp.lang_code}/thesaurus"
    )
    thesaurus_extractor_mod.extract_thesaurus_data(wxr)


def init_thesaurus_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        entry TEXT,
        pos TEXT,
        language_code TEXT,
        sense TEXT
        );
        CREATE UNIQUE INDEX IF NOT EXISTS entries_index
        ON entries(entry, pos, language_code);

        CREATE TABLE IF NOT EXISTS terms (
        term TEXT,
        entry_id INTEGER,
        relation TEXT,  -- Synonyms, Hyponyms
        tags TEXT,
        topics TEXT,
        roman TEXT,  -- Romanization
        gloss TEXT,  -- ws template has optional hovertext gloss
        language_variant TEXT,  -- Traditional/Simplified Chinese
        PRIMARY KEY(term, entry_id),
        FOREIGN KEY(entry_id) REFERENCES entries(id)
        );

        PRAGMA journal_mode = WAL;
        PRAGMA foreign_keys = ON;
        """
    )
    return conn


def insert_thesaurus_entry(
        db_conn: sqlite3.Connection,
        entry: str,
        pos: str,
        language_code: str,
        sense: str
) -> Optional[int]:
    for (entry_id,) in db_conn.execute(
        "INSERT OR IGNORE INTO entries (entry, pos, language_code, sense) "
        "VALUES(?, ?, ?, ?) RETURNING id",
        (entry, pos, language_code, sense)
    ):
        return entry_id


def insert_thesaurus_term(
        db_conn: sqlite3.Connection,
        term: str,
        entry_id: int,
        relation: str,
        tags: str,
        topics: str,
        roman: str,
        gloss: str,
        language_variant: str
) -> None:
    db_conn.execute(
        "INSERT OR IGNORE INTO terms (term, entry_id, relation, tags, topics, "
        "roman, gloss, language_variant) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        (term, entry_id, relation, tags, topics, roman, gloss, language_variant)
    )
    db_conn.commit()


def thesaurus_linkage_number(db_conn: sqlite3.Connection) -> int:
    for (r,) in db_conn.execute("SELECT count(*) FROM terms"):
        return r


def search_thesaurus(
        db_conn: sqlite3.Connection,
        entry: str,
        lang_code: str,
        pos: str
) -> Tuple[str, ...]:
    return db_conn.execute(
        "SELECT term, relation, sense, roman, tags, topics, gloss, "
        "language_variant "
        "FROM terms JOIN entries ON terms.entry_id = entries.id "
        "WHERE entry = ? AND language_code = ? AND pos = ? AND term != ?",
        (entry, lang_code, pos, entry)
    )


def close_thesaurus_db(db_path: Path, db_conn: sqlite3.Connection) -> None:
    db_conn.close()
    if db_path.parent.samefile(Path(tempfile.gettempdir())):
        db_path.unlink(True)
