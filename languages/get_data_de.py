# Export German Wiktionary language data to JSON.
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
            lang_code=args.lang_code, db_path="wikt-db_de_language_data_temp.db"
        ),
        WiktionaryConfig(),
    )
    help_ns_id = wxr.wtp.NAMESPACE_DATA["Help"]["id"]
    template_ns_id = wxr.wtp.NAMESPACE_DATA["Template"]["id"]
    process_dump(wxr.wtp, args.dump, {help_ns_id, template_ns_id})

    # The page 'Hilfe:Sprachkürzel seems to be the only central collection of
    # language codes and their German expansions. We will use this until we find
    #  perhaps a more authoritative source.
    sprachkuerzel = wxr.wtp.get_page("Hilfe:Sprachkürzel")

    wxr.config.word = sprachkuerzel.title
    wxr.wtp.start_page(sprachkuerzel.title)
    tree = wxr.wtp.parse(
        sprachkuerzel.body,
        pre_expand=True,
    )

    languages = {}
    for node in filter(lambda n: isinstance(n, WikiNode), tree.children):
        if node.kind != NodeKind.LEVEL3:
            continue

        for table_row in node.find_child_recursively(NodeKind.TABLE_ROW):
            third_row_content = table_row.children[2].children[0]
            if (
                isinstance(third_row_content, str)
                or third_row_content.kind != NodeKind.TEMPLATE
            ):
                continue
            lang_code = third_row_content.template_name

            languages[lang_code] = [clean_node(wxr, None, third_row_content)]

    with open(
        f"src/wiktextract/data/{args.lang_code}/languages.json",
        "w",
        encoding="utf-8",
    ) as fout:
        json.dump(languages, fout, indent=2, ensure_ascii=False, sort_keys=True)
