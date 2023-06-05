# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import collections
import importlib
import logging
import sqlite3
import tempfile

from pathlib import Path
from typing import Tuple, Optional, Set, Callable, Any, List

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
        linkage TEXT,  -- Synonyms, Hyponyms
        tags TEXT,
        topics TEXT,
        roman TEXT,  -- Romanization
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
    language_code: str,
    pos: str,
    sense: str,
) -> Optional[int]:
    for (entry_id,) in db_conn.execute(
        "INSERT OR IGNORE INTO entries (entry, language_code, pos, sense) "
        "VALUES(?, ?, ?, ?) RETURNING id",
        (entry, language_code, pos, sense),
    ):
        return entry_id


def insert_thesaurus_term(
    db_conn: sqlite3.Connection,
    term: str,
    entry_id: int,
    linkage: str,
    tags: str,
    topics: str,
    roman: str,
    language_variant: str,
) -> None:
    db_conn.execute(
        "INSERT OR IGNORE INTO terms (term, entry_id, linkage, tags, topics, "
        "roman, language_variant) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (term, entry_id, linkage, tags, topics, roman, language_variant),
    )
    db_conn.commit()


def thesaurus_linkage_number(db_conn: sqlite3.Connection) -> int:
    for (r,) in db_conn.execute("SELECT count(*) FROM terms"):
        return r


def search_thesaurus(
    db_conn: sqlite3.Connection, entry: str, lang_code: str, pos: str
) -> Tuple[str, ...]:
    return db_conn.execute(
        "SELECT term, linkage, sense, roman, tags, topics, language_variant "
        "FROM terms JOIN entries ON terms.entry_id = entries.id "
        "WHERE entry = ? AND language_code = ? AND pos = ?",
        (entry, lang_code, pos),
    )


def get_thesaurus_entry_id(
    db_conn: sqlite3.Connection, entry: str, lang_code: str, pos: str
) -> Optional[int]:
    for (r,) in db_conn.execute(
        "SELECT id FROM entries WHERE entry = ? AND language_code = ? "
        "AND pos = ?",
        (entry, lang_code, pos),
    ):
        return r


def insert_thesaurus_entry_and_term(
    db_conn: sqlite3.Connection,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    term: str,
    tags: Optional[List[str]],
    roman: Optional[str],
    language_variant: Optional[str],
) -> None:
    entry_id = insert_thesaurus_entry(db_conn, entry, lang_code, pos, sense)
    if entry_id is None:
        entry_id = get_thesaurus_entry_id(db_conn, entry, lang_code, pos)
    insert_thesaurus_term(
        db_conn, term, entry_id, linkage, tags, None, roman, language_variant
    )


def close_thesaurus_db(db_path: Path, db_conn: sqlite3.Connection) -> None:
    db_conn.close()
    if db_path.parent.samefile(Path(tempfile.gettempdir())):
        db_path.unlink(True)


def emit_words_in_thesaurus(
    wxr: WiktextractContext,
    emitted: Set[Tuple[str, str, str]],
    word_cb: Callable[[Any], None],
) -> None:
    # Emit words that occur in thesaurus as main words but for which
    # Wiktionary has no word in the main namespace. This seems to happen
    # sometimes.
    logging.info("Emitting words that only occur in thesaurus")
    for entry_id, entry, pos, lang_code, sense in wxr.thesaurus_db_conn.execute(
        "SELECT id, entry, pos, language_code, sense FROM entries "
        "WHERE pos IS NOT NULL AND language_code IS NOT NULL"
    ):
        if (entry, lang_code, pos) in emitted:
            continue
        logging.info(
            "Emitting thesaurus entry for "
            f"{entry}/{lang_code}/{pos} (not in main)"
        )
        sense_dict = collections.defaultdict(list)
        sense_dict["glosses"] = [sense]
        for (
            term,
            linkage,
            tags,
            topics,
            roman,
            lang_variant,
        ) in wxr.thesaurus_db_conn.execute(
            "SELECT term, linkage, tags, topics, roman, language_variant "
            "FROM terms WHERE entry_id = ?",
            (entry_id,),
        ):
            relation_dict = {"word": term, "source": f"Thesaurus:{entry}"}
            if tags is not None:
                relation_dict["tags"] = tags.split("|")
            if topics is not None:
                relation_dict["topics"] = topics.split("|")
            if lang_variant is not None:
                relation_dict["language_variant"] = lang_variant
            sense_dict[linkage].append(relation_dict)

        if len(sense_dict) == 1:
            sense_dict["tags"] = ["no-gloss"]

        word_cb(
            {
                "word": entry,
                "lang": wxr.config.LANGUAGES_BY_CODE.get(lang_code),
                "lang_code": lang_code,
                "pos": pos,
                "senses": [sense_dict],
                "source": "thesaurus",
            }
        )
