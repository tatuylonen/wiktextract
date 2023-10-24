from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

EtymologyData = Dict[str, List[str]]


def extract_etymology(
    wxr: WiktextractContext,
    nodes: List[Union[WikiNode, str]],
) -> Optional[EtymologyData]:
    etymology_dict: EtymologyData = defaultdict(list)
    level_node_index = len(nodes)
    # find nodes after the etymology subtitle and before the next level node
    for index, node in enumerate(nodes):
        if isinstance(node, WikiNode) and node.kind in LEVEL_KINDS:
            level_node_index = index
            break

    pos_title: Optional[str] = None
    for etymology_node in nodes[:level_node_index]:
        if (
            isinstance(etymology_node, WikiNode)
            and etymology_node.kind == NodeKind.LIST
        ):
            if etymology_node.sarg == "*":
                pos_title = clean_node(wxr, None, etymology_node)
                pos_title = pos_title.removeprefix("* ").removesuffix(" :")
            elif etymology_node.sarg == ":":
                # ignore missing etymology template "ébauche-étym"
                for template_node in etymology_node.find_child_recursively(
                    NodeKind.TEMPLATE
                ):
                    if template_node.template_name == "ébauche-étym":
                        return

                for etymology_item in etymology_node.find_child(
                    NodeKind.LIST_ITEM
                ):
                    etymology_data = find_pos_in_etymology_list(
                        wxr, etymology_item
                    )
                    if etymology_data is not None:
                        new_pos_title, new_etymology_text = etymology_data
                        etymology_dict[new_pos_title].append(new_etymology_text)
                    else:
                        etymology_text = clean_node(
                            wxr, None, etymology_item.children
                        )
                        etymology_dict[pos_title].append(etymology_text)

    if len(etymology_dict) == 0:
        etymology_dict[None].append(
            clean_node(wxr, None, nodes[:level_node_index])
        )
    return etymology_dict


def find_pos_in_etymology_list(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> Optional[Tuple[str, str]]:
    """
    Return tuple of POS title and etymology text if the passed lis item node
    starts with italic POS node or POS template, otherwise return None.
    """
    child_nodes = list(list_item_node.filter_empty_str_child())
    for index, node in enumerate(child_nodes):
        if (
            index == 0
            and isinstance(node, TemplateNode)
            and node.template_name in ("lien-ancre-étym", "laé")
        ):
            return clean_node(wxr, None, node).strip("()"), clean_node(
                wxr, None, child_nodes[index + 1 :]
            )
        if (
            index == 1
            and isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and isinstance(child_nodes[0], str)
            and child_nodes[0].endswith("(")
            and isinstance(child_nodes[2], str)
            and child_nodes[2].startswith(")")
        ):
            # italic pos
            pos_title = clean_node(wxr, None, node)
            if pos_title == "Nom":
                pos_title = "Nom commun"
            return pos_title, clean_node(
                wxr, None, child_nodes[index + 1 :]
            ).removeprefix(") ")


def insert_etymology_data(
    lang_code: str, page_data: List[Dict], etymology_data: EtymologyData
) -> None:
    """
    Insert list of etymology data extracted from the level 3 node to each sense
    dictionary matches the language and POS.
    """
    sense_dict = {}  # group by pos title
    for sense_data in page_data:
        if sense_data.get("lang_code") == lang_code:
            sense_dict[sense_data.get("pos_title")] = sense_data

    for pos_title, etymology_texts in etymology_data.items():
        if pos_title is None:  # add to all sense dictionaries
            for sense_data in sense_dict.values():
                sense_data["etymology_texts"] = etymology_texts
        elif pos_title in sense_dict:
            sense_dict[pos_title]["etymology_texts"] = etymology_texts
        elif pos_title.removesuffix(" 1") in sense_dict:
            # an index number is added in the etymology section but not added in
            # POS title
            sense_dict[pos_title.removesuffix(" 1")][
                "etymology_texts"
            ] = etymology_texts
