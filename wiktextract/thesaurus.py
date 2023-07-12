# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import logging
import sqlite3
import tempfile

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, Set, Callable, Any, List
from collections.abc import Iterable

from .wxr_context import WiktextractContext
from .import_utils import import_extractor_module


@dataclass
class ThesaurusTerm:
    entry: str
    language_code: str
    pos: str
    linkage: str
    term: str
    tags: Optional[str] = None
    topics: Optional[str] = None
    roman: Optional[str] = None
    language_variant: Optional[str] = None
    entry_id: Optional[int] = None
    sense: Optional[str] = None


def extract_thesaurus_data(wxr: WiktextractContext) -> None:
    thesaurus_extractor_mod = import_extractor_module(
        wxr.wtp.lang_code, "thesaurus"
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


def thesaurus_linkage_number(db_conn: sqlite3.Connection) -> int:
    for (r,) in db_conn.execute("SELECT count(*) FROM terms"):
        return r


def search_thesaurus(
    db_conn: sqlite3.Connection,
    entry: str,
    lang_code: str,
    pos: str,
    linkage_type: Optional[str] = None
) -> Iterable[ThesaurusTerm]:
    query_sql = """
    SELECT term, entries.id, linkage, tags, topics, roman,
    language_variant, sense
    FROM terms JOIN entries ON terms.entry_id = entries.id
    WHERE entry = ? AND language_code = ? AND pos = ?
    """
    query_value = (entry, lang_code, pos)
    if linkage_type is not None:
        query_sql += " AND linkage = ?"
        query_value += (linkage_type,)

    for r in db_conn.execute(query_sql, query_value):
        yield ThesaurusTerm(
            term=r[0],
            entry_id=r[1],
            linkage=r[2],
            tags=r[3],
            topics=r[4],
            roman=r[5],
            language_variant=r[6],
            sense=r[7],
            entry=entry,
            pos=pos,
            language_code=lang_code,
        )


def insert_thesaurus_terms(
    db_conn: sqlite3.Connection, terms: List[ThesaurusTerm]
) -> None:
    for term in terms:
        insert_thesaurus_term(db_conn, term)


def insert_thesaurus_term(
    db_conn: sqlite3.Connection, term: ThesaurusTerm
) -> None:
    entry_id = None
    for (new_entry_id,) in db_conn.execute(
        "INSERT OR IGNORE INTO entries (entry, language_code, pos, sense) "
        "VALUES(?, ?, ?, ?) RETURNING id",
        (term.entry, term.language_code, term.pos, term.sense),
    ):
        entry_id = new_entry_id
    if entry_id is None:
        for (old_entry_id,) in db_conn.execute(
            "SELECT id FROM entries WHERE entry = ? AND language_code = ? "
            "AND pos = ?",
            (term.entry, term.language_code, term.pos),
        ):
            entry_id = old_entry_id
    db_conn.execute(
        "INSERT OR IGNORE INTO terms (term, entry_id, linkage, tags, topics, "
        "roman, language_variant) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (
            term.term,
            entry_id,
            term.linkage,
            term.tags,
            term.topics,
            term.roman,
            term.language_variant,
        ),
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

        if None in (entry, lang_code, pos):
            logging.info(f"'None' in entry, lang_code or"
                         f" pos: {entry}, {lang_code}, {pos}")
            continue

        logging.info(
            "Emitting thesaurus entry for "
            f"{entry}/{lang_code}/{pos} (not in main)"
        )

        sense_dict = dict()

        if sense:
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
            if linkage not in sense_dict:
                sense_dict[linkage] = []
            sense_dict[linkage].append(relation_dict)

        if "glosses" not in sense_dict:
            sense_dict["tags"] = ["no-gloss"]

        entry = {
                "word": entry,
                "lang": wxr.config.LANGUAGES_BY_CODE.get(lang_code)[0],
                "lang_code": lang_code,
                "pos": pos,
                "senses": [sense_dict] if sense_dict else [],
                "source": "thesaurus",
                }
        entry = {k: v for k, v in entry.items() if v}
        word_cb(entry)
