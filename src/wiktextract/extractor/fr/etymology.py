from collections import defaultdict
from typing import Optional

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import WordEntry

EtymologyData = dict[str, list[str]]


def extract_etymology(
    wxr: WiktextractContext, level_node: LevelNode, base_data: WordEntry
) -> Optional[EtymologyData]:
    etymology_dict: EtymologyData = defaultdict(list)
    pos_title = ""
    level_node_index = len(level_node.children)
    for node_index, node in level_node.find_child(
        NodeKind.LIST | LEVEL_KIND_FLAGS, True
    ):
        if node.kind in LEVEL_KIND_FLAGS:
            level_node_index = node_index
            title_text = clean_node(wxr, None, node.largs)
            if title_text == "Attestations historiques":
                extract_etymology_examples(wxr, node, base_data)
        elif node.kind == NodeKind.LIST:
            if node.sarg == "*":
                pos_title = clean_node(wxr, None, node)
                pos_title = pos_title.removeprefix("* ").removesuffix(" :")
            elif node.sarg == ":":
                # ignore missing etymology template "ébauche-étym"
                for template_node in node.find_child_recursively(
                    NodeKind.TEMPLATE
                ):
                    if template_node.template_name == "ébauche-étym":
                        return

                for etymology_item in node.find_child(NodeKind.LIST_ITEM):
                    etymology_data = find_pos_in_etymology_list(
                        wxr, etymology_item
                    )
                    if etymology_data is not None:
                        new_pos_title, new_etymology_text = etymology_data
                        if len(new_etymology_text) > 0:
                            etymology_dict[new_pos_title].append(
                                new_etymology_text
                            )
                    else:
                        etymology_text = clean_node(
                            wxr, None, etymology_item.children
                        )
                        if len(etymology_text) > 0:
                            etymology_dict[pos_title].append(etymology_text)

    if len(etymology_dict) == 0:
        etymology_text = clean_node(
            wxr, None, level_node.children[:level_node_index]
        )
        if len(etymology_text) > 0:
            etymology_dict[""].append(etymology_text)

    return etymology_dict


def find_pos_in_etymology_list(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> Optional[tuple[str, str]]:
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
    lang_code: str, page_data: list[WordEntry], etymology_data: EtymologyData
) -> None:
    """
    Insert list of etymology data extracted from the level 3 node to each sense
    dictionary matches the language and POS.
    """
    sense_dict = defaultdict(list)  # group by pos title
    for sense_data in page_data:
        if sense_data.lang_code == lang_code:
            sense_dict[sense_data.pos_title].append(sense_data)

    for pos_title, etymology_texts in etymology_data.items():
        if pos_title == "":  # add to all sense dictionaries
            for sense_data_list in sense_dict.values():
                for sense_data in sense_data_list:
                    sense_data.etymology_texts = etymology_texts
        elif pos_title in sense_dict:
            for sense_data in sense_dict[pos_title]:
                sense_data.etymology_texts = etymology_texts
        elif pos_title.removesuffix(" 1") in sense_dict:
            # an index number is added in the etymology section but not added in
            # POS title
            for sense_data in sense_dict[pos_title.removesuffix(" 1")]:
                sense_data.etymology_texts = etymology_texts


def extract_etymology_examples(
    wxr: WiktextractContext,
    level_node: LevelNode,
    base_data: WordEntry,
) -> None:
    from .gloss import process_exemple_template

    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        time = ""
        for template_node in list_item.find_child(NodeKind.TEMPLATE):
            if template_node.template_name == "siècle":
                time = clean_node(wxr, None, template_node).strip("() ")
            elif template_node.template_name == "exemple":
                example_data = process_exemple_template(
                    wxr, template_node, None, time
                )
                if example_data.text != "":
                    base_data.etymology_examples.append(example_data)
