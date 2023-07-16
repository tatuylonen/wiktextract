from typing import List, Dict

from wikitextprocessor import WikiNode, NodeKind

from wiktextract.datautils import data_append
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import strip_nodes


def extract_inflections(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
) -> None:
    for child in node.children:
        if isinstance(child, WikiNode) and child.kind == NodeKind.TEMPLATE:
            template_name = child.args[0][0].lower()
            if template_name == "ja-i":
                expanded_table = wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(node), expand_all=True
                )
                extract_ja_i_template(wxr, page_data, expanded_table, "")


def extract_ja_i_template(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
    table_header: str,
) -> None:
    for child in node.children:
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TABLE_ROW:
                if len(list(strip_nodes(child.children))) == 1:
                    table_header = clean_node(wxr, None, child.children)
                else:
                    inflection_data = {
                        "tags": [table_header],
                        "source": "inflection",
                    }
                    cell_node_index = 0
                    keys = ["form", "hiragana", "roman"]
                    for row_child in child.children:
                        if isinstance(row_child, WikiNode):
                            if row_child.kind == NodeKind.TABLE_HEADER_CELL:
                                inflection_data["tags"].append(
                                    clean_node(wxr, None, row_child)
                                )
                            elif row_child.kind == NodeKind.TABLE_CELL:
                                cell_text = clean_node(wxr, None, row_child)
                                if len(cell_text) == 0:
                                    continue
                                if cell_node_index < len(keys):
                                    key = keys[cell_node_index]
                                    cell_node_index += 1
                                    inflection_data[key] = clean_node(
                                        wxr, None, row_child
                                    )
                                else:
                                    break
                    data_append(wxr, page_data[-1], "forms", inflection_data)
            else:
                extract_ja_i_template(wxr, page_data, child, table_header)
