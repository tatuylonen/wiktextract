from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .pronunciation import is_ipa_text, insert_ipa


def extract_inflection(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
    template_name: str,
) -> None:
    # inflection templates
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_d’accord_en_français
    process_inflection_table(wxr, page_data, node)


IGNORE_TABLE_HEADERS = {
    "Terme",  # https://fr.wiktionary.org/wiki/Modèle:de-adj
    "Forme",  # https://fr.wiktionary.org/wiki/Modèle:br-flex-adj
}
IGNORE_TABLE_CELL = {
    "Déclinaisons",  # de-adj
    "—",  # https://fr.wiktionary.org/wiki/Modèle:vls-nom
}


def process_inflection_table(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    for row_num, table_row in enumerate(
        table_node.find_child(NodeKind.TABLE_ROW)
    ):
        if (
            row_num != 0
            and len(list(table_row.filter_empty_str_child()))
            == len(column_headers) + 1
        ):
            # data row has one more column then header: "fr-accord-al" template
            column_headers.insert(0, "")

        row_header = ""
        for column_num, table_cell in enumerate(
            table_row.filter_empty_str_child()
        ):
            form_data = defaultdict(list)
            if isinstance(table_cell, WikiNode):
                if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                    table_header_text = clean_node(wxr, None, table_cell)
                    if row_num == 0:
                        column_headers.append(table_header_text)
                    elif (
                        column_num == 0
                        and table_header_text not in IGNORE_TABLE_HEADERS
                    ):
                        row_header = table_header_text
                    elif table_header_text not in IGNORE_TABLE_HEADERS:
                        form_data["tags"].append(table_header_text)
                elif table_cell.kind == NodeKind.TABLE_CELL:
                    table_cell_lines = clean_node(wxr, None, table_cell)
                    for table_cell_line in table_cell_lines.splitlines():
                        if is_ipa_text(table_cell_line):
                            insert_ipa(form_data, table_cell_line)
                        elif (
                            table_cell_line != page_data[-1].get("word")
                            and table_cell_line not in IGNORE_TABLE_CELL
                        ):
                            form_data["form"] = table_cell_line
                    if (
                        len(column_headers) > column_num
                        and column_headers[column_num]
                        not in IGNORE_TABLE_HEADERS
                    ):
                        form_data["tags"].append(column_headers[column_num])

            if len(row_header) > 0:
                form_data["tags"].append(row_header)
            if "form" in form_data:
                page_data[-1]["forms"].append(form_data)
