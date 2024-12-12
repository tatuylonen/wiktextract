from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import Sense, WordEntry
from .section_titles import POS_DATA


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(wxr, page_data[-1], link_node)

    for list_node in level_node.find_child(NodeKind.LIST):
        if list_node.sarg.startswith("#") and list_node.sarg.endswith("#"):
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    gloss_nodes = []
    sense = Sense()
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            match node.template_name:
                case "Term":
                    raw_tag = clean_node(wxr, sense, node).strip("() \n")
                    if raw_tag != "":
                        sense.raw_tags.append(raw_tag)
                case _:
                    gloss_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            if node.sarg.endswith("*"):
                for example_list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(
                        wxr, sense, example_list_item, word_entry.lang_code
                    )
            elif (
                node.sarg.endswith(":")
                and len(sense.examples) > 0
                and sense.examples[-1].translation == ""
            ):
                for tr_list_item in node.find_child(NodeKind.LIST_ITEM):
                    sense.examples[-1].translation = clean_node(
                        wxr, sense, tr_list_item.children
                    )
        else:
            gloss_nodes.append(node)
    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        word_entry.senses.append(sense)
