from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


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
    elif template_name.startswith("fr-accord-"):
        extract_fr_accord(wxr, page_data, node)


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
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        if pass_first_row:
            break  # the second row is IPA
        for index, table_cell in enumerate(
            table_row.find_child(NodeKind.TABLE_CELL)
        ):
            form_text = clean_node(wxr, None, table_cell)
            if form_text != page_data[-1].get("word"):
                tags = ["singular"] if index == 0 else ["plural"]
                page_data[-1]["forms"].append({"form": form_text, "tags": tags})
            pass_first_row = True


def extract_fr_accord(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    table_node = expanded_node.children[0]
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        gender_type = ""
        for cell_index, table_cell_node in enumerate(
            table_row.filter_empty_str_child()
        ):
            if isinstance(table_cell_node, WikiNode):
                if table_cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    gender_text = clean_node(wxr, None, table_cell_node)
                    gender_types = {
                        "Masculin": "masculine",
                        "Féminin": "feminine",
                    }
                    gender_type = gender_types.get(gender_text, "")
                elif table_cell_node.kind == NodeKind.TABLE_CELL:
                    table_cell_children = list(
                        table_cell_node.filter_empty_str_child()
                    )
                    br_tag_index = len(table_cell_children)
                    for cell_child_index, table_cell_child in enumerate(
                        table_cell_children
                    ):
                        if (
                            isinstance(table_cell_child, WikiNode)
                            and table_cell_child.kind == NodeKind.HTML
                            and table_cell_child.tag == "br"
                        ):
                            br_tag_index = cell_child_index
                            break
                    form = clean_node(
                        wxr, None, table_cell_children[:br_tag_index]
                    )
                    if len(form) > 0 and form != page_data[-1].get("word"):
                        ipa = clean_node(
                            wxr, None, table_cell_children[br_tag_index + 1 :]
                        )
                        tags = ["singular"] if cell_index == 1 else ["plural"]
                        form_data = {"form": form, "tags": tags}
                        if len(ipa) > 0:
                            form_data["ipa"] = ipa
                        if len(gender_type) > 0:
                            form_data["tags"].append(gender_type)
                        page_data[-1]["forms"].append(form_data)
