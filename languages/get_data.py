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
from wikitextprocessor.dumpparser import process_dump
from pathlib import Path
import json

def get_lang_data(lang_code, dump_file):
    ctx = Wtp(lang_code=lang_code)
    module = ctx.NAMESPACE_DATA["Module"]["name"] + ":"

    def page_handler(model, title, text):
        if title.startswith(module):
            ctx.add_page(model, title, text)

    process_dump(ctx, dump_file, page_handler=page_handler)

    with open(f"languages/lua/json.lua", "r") as lua_json_file:
        lua_json_mod = lua_json_file.read()
    ctx.add_page("Scribunto", f"{module}wiktextract-json", lua_json_mod, transient=True)
    with open(f"languages/lua/{lang_code}.lua", "r") as lua_lang_file:
        lua_lang_mod = lua_lang_file.read()
    ctx.add_page("Scribunto", f"{module}wiktextract-lang-data", lua_lang_mod, transient=True)
    ctx.start_page("wiktextract lang data")
    data = ctx.expand("{{#invoke:wiktextract-lang-data|languages}}")

    data = json.loads(data)

    data_folder = Path(f"wiktextract/data/{lang_code}")
    if not data_folder.exists():
        data_folder.mkdir()
    with data_folder.joinpath("languages.json").open("w", encoding="utf-8") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description="Export Wiktionary language codes and names to JSON")
    parser.add_argument("lang_code", type=str, help="Language code")
    parser.add_argument("dump_file", type=str, help="Wiktionary xml dump file path")
    args = parser.parse_args()
    get_lang_data(args.lang_code, args.dump_file)
