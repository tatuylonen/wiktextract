from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

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

    for node in level_node.find_child(
        NodeKind.LIST | NodeKind.TEMPLATE | LEVEL_KIND_FLAGS
    ):
        if node.kind == NodeKind.LIST and node.sarg.endswith("#"):
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
        elif node.kind in LEVEL_KIND_FLAGS:
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
