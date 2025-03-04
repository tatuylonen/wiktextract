from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


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

    gloss_list_index = len(level_node.children)
    for index, node in enumerate(level_node.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#") and node.sarg.endswith("#"):
                    extract_gloss_list_item(wxr, page_data[-1], list_item)
                    if index < gloss_list_index:
                        gloss_list_index = index


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
) -> None:
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "terim",
        ]:
            extract_terim_template(wxr, sense, node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)


def extract_terim_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:terim
    raw_tags_str = clean_node(wxr, sense, t_node).strip("() ")
    for raw_tag in raw_tags_str.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)
