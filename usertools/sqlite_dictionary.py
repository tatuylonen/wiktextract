import json
import sqlite3
import time
import unicodedata


def strip_accents(s: str):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def collate_unicode_no_diacritic_no_case(str1: str, str2: str):
    # By default sqlite has no unicode case insensitive collation. This additionally removes all accents.
    # Standard SQLite is not even to search for cyrillic strings without case sensitivity.

    s1 = strip_accents(str1).lower()
    s2 = strip_accents(str2).lower()
    if s1 < s2:
        return -1
    elif s1 > s2:
        return 1
    else:
        return 0


class WiktionaryDictionary:
    """This class is a wrapper around a sqlite database containing the Wiktionary dump.
    It can be used to query the database."""
    def __init__(
        self,
        input_dump: str | None = None,
        input_sqlite_file: str | None = None,
        output_sqlite_path: str | None = None,
    ) -> None:
        # if input dump and output sqlite path are given, load the dump into the sqlite file
        self._input_dump = input_dump
        if input_dump and output_sqlite_path:
            self._sqlite_file = output_sqlite_path
            # Open the sqlite file
            self._set_up_db()
            self._load_dump_in_sqlite()
        # if input sqlite file is given, use that
        elif input_sqlite_file:
            self._sqlite_file = input_sqlite_file
            self._set_up_db()
            self._cur = self._conn.cursor()
        else:
            raise ValueError(
                "Either input_dump and output_sqlite_path or input_sqlite_file must be given"
            )
        
        self._conn.commit()

    def _set_up_db(self):
        # Open the sqlite file
        self._conn = sqlite3.connect(self._sqlite_file)
        self._cur = self._conn.cursor()

        # This collation has to be created every time the SQLITE file is opened because
        # SQLITE does not save collations in the file (but indexes on the collation are saved - they don't have to be recreated)
        self._conn.create_collation("NODIACRITIC", collate_unicode_no_diacritic_no_case)


    def _load_dump_in_sqlite(self) -> None:
        """Loads the dump into a sqlite database."""
        # We have a json lines file, so we can read it line by line

        already_added_keys: set[str] = set()
        with open(self._input_dump, "r", encoding="utf-8") as f:
            # We create the table
            self._cur.execute(
                "CREATE TABLE wiktionary (id INTEGER PRIMARY KEY) STRICT;"
            )
            # we parse the json
            for line in f:
                obj = json.loads(line)
                # Now we look at the obj. If it has keys that are not in the
                # already_added_keys set, we add them to the table
                for key in obj.keys():
                    if key not in already_added_keys:
                        # Now we detect the type of the value
                        value = obj[key]
                        if isinstance(value, str):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} TEXT;"
                            )
                        elif isinstance(value, int):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} INTEGER;"
                            )
                        elif isinstance(value, list):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} TEXT;"
                            )
                        elif isinstance(value, dict):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} TEXT;"
                            )
                        elif isinstance(value, bool):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} INTEGER;"
                            )
                        elif isinstance(value, float):
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} REAL;"
                            )
                        else:
                            # We have an unknown type, so we add a text column
                            print(f"Unknown type for key {key}: {type(value)}")
                            self._cur.execute(
                                f"ALTER TABLE wiktionary ADD COLUMN {key} TEXT;"
                            )
                        already_added_keys.add(key)
                # Now we have to convert the values to the correct type
                for key in obj.keys():
                    value = obj[key]
                    if isinstance(value, list) or isinstance(value, dict):
                        # We have a list or a dict, so we convert it to a string
                        obj[key] = json.dumps(value, ensure_ascii=False)
                # Now we insert the obj in the table
                self._cur.execute(
                    "INSERT INTO wiktionary ("
                    + ", ".join(obj.keys())
                    + ") VALUES ("
                    + ", ".join(["?"] * len(obj.keys()))
                    + ");",
                    tuple(obj.values()),
                )

                # We commit the changes

            # We create indexes for the 
            self._cur.execute("CREATE INDEX word_index ON wiktionary (word COLLATE NODIACRITIC);")
            self._cur.execute("CREATE INDEX lemma_index ON wiktionary (lang);")
            self._conn.commit()

    def search_word(self, word: str) -> list[dict]:
        """Searches a word in the sqlite database."""

        cursor = self._cur.execute("SELECT * FROM wiktionary WHERE word=? COLLATE NODIACRITIC;", (word,))
        return [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]


if __name__ == "__main__":
    # wikt = WiktionaryDictionary(
    #     input_dump="kaikki.org-dictionary-Czech.jsonl",
    #     output_sqlite_path="czech-wikt.db"
    # )

    wikt = WiktionaryDictionary(input_sqlite_file="czech-wikt.db")

    t0 = time.time()
    res = wikt.search_word("Kun")
    for word in res:
        print(word["word"], word["lang"], word["pos"], word["senses"])
        # This will also return the word kůň

    print(time.time() - t0)