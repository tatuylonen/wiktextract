import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import (
    EXAMPLE_TEMPLATES,
    extract_example_list_item,
    extract_example_template,
)
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

    gloss_list_start = 0
    for index, node in enumerate(level_node.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LIST
            and node.sarg.endswith("#")
        ):
            if gloss_list_start == 0:
                gloss_list_start = index
                extract_pos_header_line_nodes(
                    wxr, page_data[-1], level_node.children[:index]
                )
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
        elif isinstance(node, LevelNode):
            break
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in EXAMPLE_TEMPLATES
            and len(page_data[-1].senses) > 0
        ):
            extract_example_template(wxr, page_data[-1].senses[-1], node)


def extract_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    sense = Sense()
    gloss_text = clean_node(
        wxr, sense, list(list_item.invert_find_child(NodeKind.LIST))
    )
    for next_list in list_item.find_child(NodeKind.LIST):
        if next_list.sarg.endswith("*"):
            for next_list_item in next_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, sense, next_list_item)

    if len(gloss_text) > 0:
        sense.glosses.append(gloss_text)
        word_entry.senses.append(sense)


def extract_pos_header_line_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    for node in nodes:
        if isinstance(node, str) and word_entry.sense_index == "":
            m = re.search(r"\[(.+)\]", node.strip())
            if m is not None:
                word_entry.sense_index = m.group(1).strip()
        elif isinstance(node, TemplateNode) and node.template_name == "-l-":
            extract_l_template(wxr, word_entry, node)


def extract_l_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-l-
    first_arg = clean_node(wxr, None, node.template_parameters.get(1, ""))
    gender_args = {
        "n": "neuter",
        "m": "masculine",
        "fm": ["feminine", "masculine"],
        "p": "plural",
    }
    tag = gender_args.get(first_arg, [])
    if isinstance(tag, str):
        word_entry.tags.append(tag)
    elif isinstance(tag, list):
        word_entry.tags.extend(tag)
