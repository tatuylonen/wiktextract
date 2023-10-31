# Export Spanish Wiktionary language data to JSON.
#
# Usage:
#
# python language_data.py de dewiktionary_dump_file [--languages languages_output_file]

import argparse
import json

from wikitextprocessor import NodeKind, WikiNode, Wtp
from wikitextprocessor.dumpparser import process_dump

from wiktextract.config import WiktionaryConfig
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export Wiktionary language data to JSON"
    )
    parser.add_argument("lang_code", type=str, help="Dump file language code")
    parser.add_argument("dump", type=str, help="Wiktionary xml dump file path")
    args = parser.parse_args()
    wxr = WiktextractContext(Wtp(lang_code=args.lang_code), WiktionaryConfig())

    wxr = WiktextractContext(
        Wtp(
            lang_code=args.lang_code, db_path="wikt-db_es_language_data_temp.db"
        ),
        WiktionaryConfig(),
    )
    appendix_ns_id = wxr.wtp.NAMESPACE_DATA["Appendix"]["id"]
    process_dump(wxr.wtp, args.dump, {appendix_ns_id})

    # https://es.wiktionary.org/wiki/Ap%C3%A9ndice:C%C3%B3digos_de_idioma
    codigos_de_idioma = wxr.wtp.get_page("Apéndice:Códigos de idioma")

    wxr.config.word = codigos_de_idioma.title
    wxr.wtp.start_page(codigos_de_idioma.title)
    tree = wxr.wtp.parse(
        codigos_de_idioma.body,
        pre_expand=True,
    )
    languages = {}
    for table in tree.find_child_recursively(NodeKind.TABLE):
        for table_row in table.find_child(NodeKind.TABLE_ROW):
            lang_code_language = []
            for table_cell in table_row.find_child(NodeKind.TABLE_CELL):
                lang_code_language.append(table_cell.children[0])

            if lang_code_language:
                languages[clean_node(wxr, None, lang_code_language[0])] = [
                    clean_node(wxr, None, lang_code_language[1])
                ]
    with open(
        f"src/wiktextract/data/{args.lang_code}/languages.json",
        "w",
        encoding="utf-8",
    ) as fout:
        json.dump(languages, fout, indent=2, ensure_ascii=False, sort_keys=True)
