import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .linkage import (
    LINKAGE_TEMPLATES,
    extract_linkage_list_item,
    extract_linkage_template,
)
from .models import Sense, WordEntry
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .sound import SOUND_TEMPLATES, extract_sound_template
from .translation import extract_translation_template


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    orig_title = pos_title
    pos_title = pos_title.removeprefix("보조 ").strip()
    if pos_title in POS_DATA:
        page_data[-1].pos_title = orig_title
        pos_data = POS_DATA[pos_title]
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))
        if (
            orig_title.startswith("보조 ")
            and "auxiliary" not in page_data[-1].tags
        ):
            page_data[-1].tags.append("auxiliary")

    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if isinstance(node, TemplateNode):
            if node.template_name in SOUND_TEMPLATES:
                extract_sound_template(wxr, page_data[-1], node)
            elif node.template_name in LINKAGE_TEMPLATES:
                extract_linkage_template(wxr, page_data[-1], node)
            elif node.template_name == "외국어":
                extract_translation_template(
                    wxr,
                    page_data[-1],
                    node,
                    page_data[-1].senses[-1].glosses[-1]
                    if len(page_data[-1].senses) > 0
                    else "",
                )
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#"):
                    extract_gloss_list_item(wxr, page_data[-1], list_item)
                else:
                    extract_unorderd_list_item(wxr, page_data[-1], list_item)

    if len(page_data[-1].senses) == 0:
        page_data.pop()


def extract_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    gloss_nodes = []
    sense = Sense()
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            gloss_text = clean_node(wxr, sense, gloss_nodes)
            if len(gloss_text) > 0:
                sense.glosses.append(gloss_text)
                word_entry.senses.append(sense)
                gloss_nodes.clear()
            for nested_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_unorderd_list_item(wxr, word_entry, nested_list_item)
            continue
        else:
            gloss_nodes.append(node)

    gloss_text = clean_node(wxr, sense, gloss_nodes)
    if len(gloss_text) > 0:
        sense.glosses.append(gloss_text)
        word_entry.senses.append(sense)


def extract_unorderd_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    is_first_bold = True
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.BOLD
            and is_first_bold
        ):
            # `* '''1.''' gloss text`, terrible obsolete layout
            is_first_bold = False
            bold_text = clean_node(wxr, None, node)
            if re.fullmatch(r"\d+(?:-\d+)?\.?", bold_text):
                new_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
                new_list_item.children = list_item.children[index + 1 :]
                extract_gloss_list_item(wxr, word_entry, new_list_item)
                break
        elif isinstance(node, str) and "어원:" in node:
            etymology_nodes = []
            etymology_nodes.append(node[node.index(":") + 1 :])
            etymology_nodes.extend(list_item.children[index + 1 :])
            e_text = clean_node(wxr, None, etymology_nodes)
            if len(e_text) > 0:
                word_entry.etymology_texts.append(e_text)
            break
        elif (
            isinstance(node, str)
            and ("참고:" in node or "참조:" in node)
            and len(word_entry.senses) > 0
        ):
            sense = word_entry.senses[-1]
            sense.note = node[node.index(":") + 1 :].strip()
            sense.note += clean_node(
                wxr, sense, list_item.children[index + 1 :]
            )
            break
        elif (
            isinstance(node, str)
            and ":" in node
            and node[: node.index(":")].strip() in LINKAGE_SECTIONS
        ):
            extract_linkage_list_item(wxr, word_entry, list_item, "")
            break
    else:
        if len(word_entry.senses) > 0:
            extract_example_list_item(
                wxr, word_entry.senses[-1], list_item, word_entry.lang_code
            )
