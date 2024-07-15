# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import os
import sqlite3
import tempfile
import time
import traceback
from collections.abc import Iterable
from dataclasses import dataclass, field
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Optional, TextIO

from mediawiki_langcodes import code_to_name
from wikitextprocessor import Page
from wikitextprocessor.core import CollatedErrorReturnData, NamespaceDataEntry

from .import_utils import import_extractor_module
from .wxr_context import WiktextractContext
from .wxr_logging import logger


@dataclass
class ThesaurusTerm:
    entry: str
    language_code: str
    pos: str
    linkage: str
    term: str
    tags: list[str] = field(default_factory=list)
    raw_tags: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    roman: str = ""
    entry_id: int = 0
    sense: str = ""


def worker_func(
    page: Page,
) -> tuple[bool, list[ThesaurusTerm], CollatedErrorReturnData, Optional[str]]:
    wxr: WiktextractContext = worker_func.wxr  # type:ignore[attr-defined]
    with tempfile.TemporaryDirectory(prefix="wiktextract") as tmpdirname:
        debug_path = "{}/wiktextract-{}".format(tmpdirname, os.getpid())
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(page.title + "\n")

        wxr.wtp.start_page(page.title)
        try:
            terms = extract_thesaurus_page(wxr, page)
            return True, terms, wxr.wtp.to_return(), None
        except Exception as e:
            lst = traceback.format_exception(
                type(e), value=e, tb=e.__traceback__
            )
            msg = (
                '=== EXCEPTION while parsing page "{}":\n '
                "in process {}".format(
                    page.title,
                    current_process().name,
                )
                + "".join(lst)
            )
            return False, [], {}, msg  # type:ignore[typeddict-item]


def extract_thesaurus_page(
    wxr: WiktextractContext, page: Page
) -> list[ThesaurusTerm]:
    thesaurus_extractor_mod = import_extractor_module(
        wxr.wtp.lang_code, "thesaurus"
    )
    return thesaurus_extractor_mod.extract_thesaurus_page(wxr, page)


def extract_thesaurus_data(
    wxr: WiktextractContext, num_processes: Optional[int] = None
) -> None:
    from .wiktionary import init_worker_process

    start_t = time.time()
    logger.info("Extracting thesaurus data")
    thesaurus_ns_data: NamespaceDataEntry = wxr.wtp.NAMESPACE_DATA.get(
        "Thesaurus",
        {},  # type:ignore[typeddict-item]
    )
    thesaurus_ns_id = thesaurus_ns_data.get("id", 0)

    wxr.remove_unpicklable_objects()
    with Pool(num_processes, init_worker_process, (worker_func, wxr)) as pool:
        wxr.reconnect_databases(False)
        for success, terms, stats, err in pool.imap_unordered(
            worker_func, wxr.wtp.get_all_pages([thesaurus_ns_id], False)
        ):
            if not success:
                # Print error in parent process - do not remove
                logger.error(err)
                continue
            for term in terms:
                insert_thesaurus_term(wxr.thesaurus_db_conn, term)  # type:ignore[arg-type]
            wxr.config.merge_return(stats)

    wxr.thesaurus_db_conn.commit()  # type:ignore[union-attr]
    num_pages = wxr.wtp.saved_page_nums([thesaurus_ns_id], False)
    total = thesaurus_linkage_number(wxr.thesaurus_db_conn)  # type:ignore[arg-type]
    logger.info(
        "Extracted {} linkages from {} thesaurus pages (took {:.1f}s)".format(
            total, num_pages, time.time() - start_t
        )
    )


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
        raw_tags TEXT,
        topics TEXT,
        roman TEXT,  -- Romanization
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
    return 0


def search_thesaurus(
    db_conn: sqlite3.Connection,
    entry: str,
    lang_code: str,
    pos: str,
    linkage_type: Optional[str] = None,
) -> Iterable[ThesaurusTerm]:
    query_sql = """
    SELECT term, entries.id, linkage, tags, topics, roman, sense, raw_tags
    FROM terms JOIN entries ON terms.entry_id = entries.id
    WHERE entry = ? AND language_code = ? AND pos = ?
    """
    query_value: tuple[str, ...] = (entry, lang_code, pos)
    if linkage_type is not None:
        query_sql += " AND linkage = ?"
        query_value += (linkage_type,)

    for r in db_conn.execute(query_sql, query_value):
        yield ThesaurusTerm(
            term=r[0],
            entry_id=r[1],
            linkage=r[2],
            tags=r[3].split("|") if len(r[3]) > 0 else [],
            topics=r[4].split("|") if len(r[4]) > 0 else [],
            roman=r[5],
            sense=r[6],
            entry=entry,
            pos=pos,
            language_code=lang_code,
            raw_tags=r[7].split("|") if len(r[7]) > 0 else [],
        )


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
        """
        INSERT OR IGNORE INTO terms
        (term, entry_id, linkage, tags, topics, roman, raw_tags)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
        (
            term.term,
            entry_id,
            term.linkage,
            "|".join(term.tags),
            "|".join(term.topics),
            term.roman,
            "|".join(term.raw_tags),
        ),
    )


def close_thesaurus_db(db_path: Path, db_conn: sqlite3.Connection) -> None:
    db_conn.close()
    if db_path.parent.samefile(Path(tempfile.gettempdir())):
        db_path.unlink(True)


def emit_words_in_thesaurus(
    wxr: WiktextractContext,
    emitted: set[tuple[str, str, str]],
    out_f: TextIO,
    human_readable: bool,
) -> None:
    # Emit words that occur in thesaurus as main words but for which
    # Wiktionary has no word in the main namespace. This seems to happen
    # sometimes.
    from .wiktionary import write_json_data

    logger.info("Emitting words that only occur in thesaurus")
    for entry_id, entry, pos, lang_code, sense in wxr.thesaurus_db_conn.execute(  # type:ignore[union-attr]
        "SELECT id, entry, pos, language_code, sense FROM entries "
        "WHERE pos IS NOT NULL AND language_code IS NOT NULL"
    ):
        if (entry, lang_code, pos) in emitted:
            continue

        if None in (entry, lang_code, pos):
            logger.info(
                f"'None' in entry, lang_code or"
                f" pos: {entry}, {lang_code}, {pos}"
            )
            continue

        logger.info(
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
            raw_tags,
        ) in wxr.thesaurus_db_conn.execute(  # type:ignore[union-attr]
            """
            SELECT term, linkage, tags, topics, roman, raw_tags
            FROM terms WHERE entry_id = ?
            """,
            (entry_id,),
        ):
            relation_dict = {"word": term, "source": f"Thesaurus:{entry}"}
            if len(tags) > 0:
                relation_dict["tags"] = tags.split("|")
            if len(topics) > 0:
                relation_dict["topics"] = topics.split("|")
            if len(raw_tags) > 0:
                relation_dict["raw_tags"] = raw_tags.split("|")
            if linkage not in sense_dict:
                sense_dict[linkage] = []
            sense_dict[linkage].append(relation_dict)

        if "glosses" not in sense_dict:
            sense_dict["tags"] = ["no-gloss"]

        entry = {
            "word": entry,
            "lang": code_to_name(lang_code, "en"),
            "lang_code": lang_code,
            "pos": pos,
            "senses": [sense_dict] if sense_dict else [],
            "source": "thesaurus",
        }
        entry = {k: v for k, v in entry.items() if v}
        write_json_data(entry, out_f, human_readable)
