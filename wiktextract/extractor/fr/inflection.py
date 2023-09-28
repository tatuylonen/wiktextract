from collections import defaultdict, deque
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .pronunciation import insert_ipa, is_ipa_text


def extract_inflection(
    wxr: WiktextractContext,
    page_data: List[Dict],
    template_node: TemplateNode,
) -> None:
    # inflection templates
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_d’accord_en_français
    process_inflection_table(wxr, page_data, template_node)


IGNORE_TABLE_HEADERS = {
    "Terme",  # https://fr.wiktionary.org/wiki/Modèle:de-adj
    "Forme",  # br-flex-adj
    "Temps",  # en-conj-rég,
    "Cas",  # lt_décl_as
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
    rowspan_headers = deque()
    first_row_has_data_cell = False
    for row_num, table_row in enumerate(
        table_node.find_child(NodeKind.TABLE_ROW)
    ):
        # filter empty table cells
        table_row_nodes = [
            row_node_child
            for row_node_child in table_row.children
            if isinstance(row_node_child, WikiNode)
            and (
                row_node_child.kind == NodeKind.TABLE_HEADER_CELL
                or (
                    row_node_child.kind == NodeKind.TABLE_CELL
                    and len(list(row_node_child.filter_empty_str_child())) > 0
                )
            )
            and row_node_child.attrs.get("style") != "display:none"
        ]
        if row_num == 0:
            first_row_has_data_cell = any(
                isinstance(cell, WikiNode)
                and cell.kind == NodeKind.TABLE_CELL
                and "invisible" not in cell.attrs.get("class", "")
                for cell in table_row_nodes
            )
        row_headers = []
        for index, (rowspan_text, rowspan_count) in enumerate(
            rowspan_headers.copy()
        ):
            row_headers.append(rowspan_text)
            if rowspan_count - 1 == 0:
                del rowspan_headers[index]
            else:
                rowspan_headers[index] = (rowspan_text, rowspan_count - 1)

        column_cell_index = 0
        for column_num, table_cell in enumerate(table_row_nodes):
            form_data = defaultdict(list)
            if isinstance(table_cell, WikiNode):
                if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                    table_header_text = clean_node(wxr, None, table_cell)
                    if table_header_text in IGNORE_TABLE_HEADERS:
                        continue
                    elif row_num == 0 and not first_row_has_data_cell:
                        # if cells of the first row are not all header cells
                        # then the header cells are row headers but not column
                        # headers
                        column_headers.append(table_header_text)
                    elif row_num > 0:
                        row_headers.append(table_header_text)
                        if "rowspan" in table_cell.attrs:
                            rowspan_headers.append(
                                (
                                    table_header_text,
                                    int(table_cell.attrs.get("rowspan")) - 1,
                                )
                            )
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
                        len(column_headers) > column_cell_index
                        and column_headers[column_cell_index]
                        not in IGNORE_TABLE_HEADERS
                    ):
                        form_data["tags"].append(
                            column_headers[column_cell_index]
                        )

                    if len(row_headers) > 0:
                        form_data["tags"].extend(row_headers)
                    if "form" in form_data:
                        page_data[-1]["forms"].append(form_data)
                    column_cell_index += 1
