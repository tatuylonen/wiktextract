# Export Wiktionary language codes and names to JSON, saving this data to
# wiktextract/data/lang_code/languages.json. This script directly uses the
# language data in the relevant lua module(s) of a language's wiktionary dump.
#
# Should be called from the root directory of the wiktextract repo. This script
# expects that a lua module with the filename lang_code.lua exists in
# languages/lua, and that this module exports a function called languages()
# which returns a string of JSON data. The JSON data should be an object with
# keys of lang_codes whose values are arrays of the corresponding language
# names, with the canonical name first.
#
# Usage:
#
# python languages/get_data.py lang_code dump_file
#
# E.g.:
#
# python languages/get_data.py en enwiktionary-20230420-pages-articles.xml.bz2

import argparse
from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor.dumpparser import process_dump
from pathlib import Path
import json


def get_lang_data(lang_code: str, dump_file: str) -> None:
    wxr = WiktextractContext(Wtp(lang_code=lang_code), WiktionaryConfig())
    module_ns_id = wxr.wtp.NAMESPACE_DATA["Module"]["id"]
    module_ns_name = wxr.wtp.NAMESPACE_DATA["Module"]["name"]
    process_dump(wxr.wtp, dump_file, {module_ns_id})

    with open("languages/lua/json.lua", encoding="utf-8") as f:
        lua_json_code = f.read()
        wxr.wtp.add_page(
            f"{module_ns_name}:Wiktextract-json"
            if lang_code == "zh"
            else f"{module_ns_name}:wiktextract-json",
            module_ns_id,
            body=lua_json_code,
            model="Scribunto",
        )
    with open(f"languages/lua/{lang_code}.lua", encoding="utf-8") as f:
        lua_lang_code = f.read()
        wxr.wtp.add_page(
            f"{module_ns_name}:Wiktextract-lang-data"
            if lang_code == "zh"
            else f"{module_ns_name}:wiktextract-lang-data",
            module_ns_id,
            body=lua_lang_code,
            model="Scribunto",
        )
    wxr.wtp.db_conn.commit()
    wxr.wtp.start_page("wiktextract lang data")
    data = wxr.wtp.expand("{{#invoke:wiktextract-lang-data|languages}}")
    data = json.loads(data)
    data_folder = Path(f"wiktextract/data/{lang_code}")
    if not data_folder.exists():
        data_folder.mkdir()
    with data_folder.joinpath("languages.json").open(
        "w", encoding="utf-8"
    ) as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)
    wxr.wtp.close_db_conn()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Wiktionary language codes and names to JSON"
    )
    parser.add_argument("lang_code", type=str, help="Dump file language code")
    parser.add_argument(
        "dump_file", type=str, help="Wiktionary xml dump file path"
    )
    args = parser.parse_args()
    get_lang_data(args.lang_code, args.dump_file)
