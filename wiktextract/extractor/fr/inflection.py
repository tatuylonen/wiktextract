from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import filter_child_wikinodes


def extract_inflection(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
    template_name: str,
) -> None:
    extract_template_funcs = {"fr-rég": extract_fr_reg}
    extract_func = extract_template_funcs.get(template_name)
    if extract_func is not None:
        extract_func(wxr, page_data, node)


def extract_fr_reg(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    table_node = expanded_node.children[0]
    pass_first_row = False
    for table_row in filter_child_wikinodes(table_node, NodeKind.TABLE_ROW):
        if pass_first_row:
            break  # the second row is IPA
        for index, table_cell in enumerate(
            filter_child_wikinodes(table_row, NodeKind.TABLE_CELL)
        ):
            form_text = clean_node(wxr, None, table_cell)
            if form_text != page_data[-1].get("word"):
                tags = ["plural"] if index == 1 else ["singular"]
                page_data[-1]["forms"].append({"form": form_text, "tags": tags})
            pass_first_row = True
