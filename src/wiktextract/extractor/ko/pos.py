import re

from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import Sense, WordEntry
from .section_titles import POS_DATA
from .sound import SOUND_TEMPLATES, extract_sound_template


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    if pos_title in POS_DATA:
        page_data[-1].pos_title = pos_title
        pos_data = POS_DATA[pos_title]
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))

    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in SOUND_TEMPLATES:
            extract_sound_template(wxr, page_data[-1], t_node)

    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if list_node.sarg.endswith("#"):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
            elif (
                list_node.sarg.startswith(":") and len(page_data[-1].senses) > 0
            ):
                extract_example_list_item(
                    wxr,
                    page_data[-1].senses[-1],
                    list_item,
                    base_data.lang_code,
                )
            elif list_node.sarg.endswith("*"):
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
            if node.sarg.startswith(":"):
                for e_list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(
                        wxr, sense, e_list_item, word_entry.lang_code
                    )
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
            if re.fullmatch(r"\d+\.", bold_text):
                new_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
                new_list_item.children = list_item.children[index + 1 :]
                extract_gloss_list_item(wxr, word_entry, new_list_item)
                break
        elif isinstance(node, str) and "어원:" in node:
            etymology_nodes = []
            etymology_nodes.append(node[node.index(":") + 1 :])
            etymology_nodes.extend(list_item.children[index + 1 :])
            word_entry.etymology_text = clean_node(wxr, None, etymology_nodes)
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
