import json
import os
import sqlite3
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


def get_sqlite_type_for_python_type(python_type: type) -> str:
    if python_type == str:
        return "TEXT"
    elif python_type == int:
        return "INTEGER"
    elif python_type == list:
        return "TEXT"
    elif python_type == dict:
        return "TEXT"
    elif python_type == bool:
        return "INTEGER"
    elif python_type == float:
        return "REAL"
    else:
        raise ValueError(f"Unknown python type: {python_type}")


def format_python_value_for_sqlite(value: object) -> object:
    """Formats a python value to be inserted into a sqlite database. Note: Doesn't support classes."""
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    elif isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    else:
        return value


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
            # Delete the sqlite file if it already exists
            try:
                os.remove(output_sqlite_path)
            except FileNotFoundError:
                pass
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

        # Enable foreign keys
        self._cur.execute("PRAGMA foreign_keys = ON;")

    def _load_dump_in_sqlite(self) -> None:
        """Loads the dump into a sqlite database."""
        # We have a json lines file, so we can read it line by line

        already_added_keys: set[str] = set()
        with open(self._input_dump, "r", encoding="utf-8") as f:
            # We create the table
            self._cur.execute("CREATE TABLE wiktionary (id INTEGER PRIMARY KEY);")
            # we parse the json
            for line in f:
                obj = json.loads(line)
                # Now we look at the obj. If it has keys that are not in the
                # already_added_keys set, we add them to the table
                for key in obj.keys():
                    if key not in already_added_keys:
                        # Now we detect the type of the value
                        value = obj[key]

                        sqlite_type = get_sqlite_type_for_python_type(type(value))
                        self._cur.execute(
                            f"ALTER TABLE wiktionary ADD COLUMN {key} {sqlite_type};"
                        )

                        already_added_keys.add(key)
                # Now we have to convert the values to the correct type
                for key in obj.keys():
                    obj[key] = format_python_value_for_sqlite(obj[key])

                # Now we insert the obj in the table
                self._cur.execute(
                    "INSERT INTO wiktionary ("
                    + ", ".join(obj.keys())
                    + ") VALUES ("
                    + ", ".join(["?"] * len(obj.keys()))
                    + ");",
                    tuple(obj.values()),
                )

            # We create indexes for the important columns
            self._cur.execute(
                "CREATE INDEX word_index ON wiktionary (word COLLATE NODIACRITIC);"
            )
            self._cur.execute("CREATE INDEX lang_index ON wiktionary (lang);")

            self._create_index_table_for_json_array("forms", "form")
            self._conn.commit()

    def _create_index_table_for_json_array(self, column_name: str, key: str) -> None:
        """JSON arrays cannot be indexed in sqlite. But even in database engines like postgresql, they can be indexed, but you cannot apply a collation to them.
        This separate table allows us to solve both problems."""
        # https://sqlite.org/forum/forumpost/dfd4739c57

        table_name = f"{column_name}_{key}_idx"

        self._cur.execute(
            f"""CREATE TABLE {table_name} (
            fid INTEGER NOT NULL,
            --PRIMARY key (fid, elem),
            FOREIGN KEY (fid) REFERENCES wiktionary (id)            
            );"""
        )

        self._cur.execute(f"""SELECT id, {column_name} FROM wiktionary;""")
        already_existing_columns: set[str] = set()
        for word_id, json_array in self._cur.fetchall():
            if json_array is not None:
                for elem in json.loads(json_array):
                    for elem_key in elem.keys():
                        # We have to check if the column already exists
                        if elem_key not in already_existing_columns:
                            # We get the type of the value
                            sqlite_type = get_sqlite_type_for_python_type(
                                type(elem[elem_key])
                            )
                            self._cur.execute(
                                f"""ALTER TABLE {table_name} ADD COLUMN {elem_key} {sqlite_type};"""
                            )
                            already_existing_columns.add(elem_key)
                    # Now we insert the element in the index table
                    values = [
                        format_python_value_for_sqlite(value) for value in elem.values()
                    ]

                    self._cur.execute(
                        f"""INSERT INTO {table_name} (fid, {", ".join(elem.keys())}) VALUES (?, {", ".join(["?"] * len(elem.keys()))});""",
                        (word_id, *values),
                    )

        # Create an index on the key
        self._cur.execute(
            f"""CREATE INDEX {column_name}_{key}_idx_{key} ON {table_name} ({key} COLLATE NODIACRITIC);"""
        )

    def search_word(self, word: str) -> list[dict]:
        """Searches a word in the sqlite database."""

        cursor = self._cur.execute(
            "SELECT * FROM wiktionary WHERE word=? COLLATE NODIACRITIC;", (word,)
        )
        return [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]

    def search_word_with_forms(self, word: str) -> list[dict]:
        # This searches either in the word column or in the forms table, using a join
        cursor = self._cur.execute(
            "SELECT * FROM wiktionary WHERE word=? COLLATE NODIACRITIC OR id IN (SELECT fid FROM forms_form_idx WHERE form=? COLLATE NODIACRITIC);",
            (word, word),
        )
        return [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]


if __name__ == "__main__":
    # Command line interface
    import argparse

    parser = argparse.ArgumentParser(
        description="Searches a word in the Wiktionary dump."
    )
    parser.add_argument(
        "--word",
        type=str,
        help="The word to search for.",
    )
    parser.add_argument(
        "--input-dump",
        type=str,
        help="The path to the Wiktionary dump.",
    )
    parser.add_argument(
        "--output-sqlite",
        type=str,
        help="The path to the sqlite file to create.",
    )
    parser.add_argument(
        "--input-sqlite",
        type=str,
        help="The path to the sqlite file to read.",
    )
    args = parser.parse_args()

    wikt = WiktionaryDictionary(
        input_dump=args.input_dump,
        output_sqlite_path=args.output_sqlite,
        input_sqlite_file=args.input_sqlite,
    )

    if args.word:
        res = wikt.search_word(args.word)
        for word in res:
            print(
                word["word"], word["lang"], word["pos"], word["senses"], word["forms"]
            )

    # Usage from python
    # wikt = WiktionaryDictionary(
    #    input_dump="kaikki.org-dictionary-Czech.jsonl",
    #    output_sqlite_path="czech-wikt.db"
    # )

    # wikt = WiktionaryDictionary(input_sqlite_file="czech-wikt.db")
    #
    # t0 = time.time()
    # res = wikt.search_word("Kun")
    # for word in res:
    #    print(word["word"], word["lang"], word["pos"], word["senses"])
    #    # This will also return the word kůň
    #
    # print(time.time() - t0)
