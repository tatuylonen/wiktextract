from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

# https://zh.wiktionary.org/wiki/Category:日語變格表模板
JAPANESE_INFLECTION_TEMPLATE_PREFIXES = (
    "ja-i",
    "ja-adj-infl",
    "ja-conj-bungo",
    "ja-go",
    "ja-honorific",
    "ja-ichi",
    "ja-kuru",
    "ja-suru",
    "ja-verbconj",
    "ja-zuru",
)


def extract_inflections(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
) -> None:
    for child in node.find_child(NodeKind.TEMPLATE):
        template_name = child.template_name.lower()
        if template_name.startswith(JAPANESE_INFLECTION_TEMPLATE_PREFIXES):
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
                if len(list(child.filter_empty_str_child())) == 1:
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
                    page_data[-1]["forms"].append(inflection_data)
            else:
                extract_ja_i_template(wxr, page_data, child, table_header)
