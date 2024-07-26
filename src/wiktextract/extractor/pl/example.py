import re

from wikitextprocessor.parser import HTMLNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense, WordEntry


def extract_example_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        sense_index = ""
        example_data = Example()
        translation_start = 0
        for index, node in enumerate(list_item.children):
            if isinstance(node, str):
                m = re.search(r"\(\d+\.\d+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
                elif node.strip() == "→":
                    translation_start = index + 1
                    break
            elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
                example_data.text = clean_node(wxr, None, node)
            elif isinstance(node, HTMLNode) and node.tag == "ref":
                example_data.ref = clean_node(wxr, None, node.children)
        if translation_start != 0:
            example_data.translation = clean_node(
                wxr, None, list_item.children[translation_start:]
            )
        if example_data.text == "":
            return
        if len(page_data) == 0:
            page_data.append(base_data.model_copy(deep=True))
        find_sense = False
        for data in page_data:
            if data.lang_code != base_data.lang_code:
                continue
            if find_sense:
                break
            for sense in data.senses:
                if sense.sense_index == sense_index:
                    sense.examples.append(example_data)
                    find_sense = True
                    break
        if not find_sense:
            sense_data = Sense(
                tags=["no-gloss"],
                examples=[example_data],
                sense_index=sense_index,
            )
            if page_data[-1].lang_code != base_data.lang_code:
                page_data.append(base_data.model_copy(deep=True))
            page_data[-1].senses.append(sense_data)
