from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
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


IGNORE_TABLE_HEADERS = frozenset(
    {
        "terme",  # https://fr.wiktionary.org/wiki/Modèle:de-adj
        "forme",  # br-flex-adj
        "temps",  # en-conj-rég,
        "cas",  # lt_décl_as, ro-nom-tab(lower case)
        "commun",  # sv-nom-c-ar
    }
)
IGNORE_TABLE_CELL = frozenset(
    {
        "Déclinaisons",  # de-adj
        "—",  # https://fr.wiktionary.org/wiki/Modèle:vls-nom
    }
)


@dataclass
class ColspanHeader:
    text: str
    index: int
    span: int


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
    colspan_headers = []
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
            and "invisible" not in row_node_child.attrs.get("class", "")
        ]
        current_row_has_data_cell = any(
            isinstance(cell, WikiNode) and cell.kind == NodeKind.TABLE_CELL
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
                    if any(
                        table_cell.find_html(
                            "span",
                            attr_name="class",
                            attr_value="ligne-de-forme",
                        )
                    ):
                        # ignore gender header in template "ro-nom-tab"
                        continue
                    table_header_text = clean_node(
                        wxr, None, table_cell
                    ).replace("\n", " ")
                    if table_header_text.lower() in IGNORE_TABLE_HEADERS:
                        continue
                    if not current_row_has_data_cell:
                        # if all cells of the row are header cells
                        # then the header cells are column headers
                        if "colspan" in table_cell.attrs:
                            colspan_headers.append(
                                ColspanHeader(
                                    table_header_text,
                                    column_cell_index,
                                    int(table_cell.attrs.get("colspan")),
                                )
                            )
                        else:
                            column_headers.append(table_header_text)
                        column_cell_index += int(
                            table_cell.attrs.get("colspan", 1)
                        )
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
                            if "form" not in form_data:
                                form_data["form"] = table_cell_line
                            else:
                                form_data["form"] += " " + table_cell_line
                    for colspan_header in colspan_headers:
                        if (
                            column_cell_index >= colspan_header.index
                            and column_cell_index
                            < colspan_header.index + colspan_header.span
                        ):
                            form_data["tags"].append(colspan_header.text)
                    if (
                        "colspan" not in table_cell.attrs
                        and len(column_headers) > column_cell_index
                        and column_headers[column_cell_index].lower()
                        not in IGNORE_TABLE_HEADERS
                    ):
                        form_data["tags"].append(
                            column_headers[column_cell_index]
                        )

                    if len(row_headers) > 0:
                        form_data["tags"].extend(row_headers)
                    if "form" in form_data:
                        for form in form_data["form"].split(" ou "):
                            new_form_data = deepcopy(form_data)
                            new_form_data["form"] = form
                            page_data[-1]["forms"].append(new_form_data)

                    column_cell_index += int(table_cell.attrs.get("colspan", 1))
