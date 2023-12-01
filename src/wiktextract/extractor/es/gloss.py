import re
from typing import List

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import WikiNodeChildrenList

from wiktextract.extractor.es.models import Sense, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[WordEntry],
    list_node: WikiNode,
) -> None:
    for list_item in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_data = Sense(glosses=[])

        definition: WikiNodeChildrenList = []
        other: WikiNodeChildrenList = []

        for node in list_item.definition:
            if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                other.append(node)
            else:
                definition.append(node)

        list_item.definition

        gloss = clean_node(wxr, gloss_data, definition)
        gloss_data.glosses.append(gloss)

        gloss_note = clean_node(wxr, gloss_data, list_item.children)

        match = re.match(r"^(\d+)", gloss_note)

        if match:
            gloss_data.senseid = int(match.group(1))
            tag_string = gloss_note[len(match.group(1)) :].strip()
        else:
            tag_string = gloss_data.tags = gloss_note.strip()

        # split tags by comma or "y"
        tags = re.split(r",|y", tag_string)
        for tag in tags:
            tag = (
                tag.strip()
                .removesuffix(".")
                .removesuffix("Main")
                .removeprefix("Main")
            )
            if tag:
                gloss_data.tags.append(tag)

        if other:
            wxr.wtp.debug(
                f"Found nodes that are not part of definition: {other}",
                sortid="extractor/es/gloss/extract_gloss/46",
            )

        page_data[-1].senses.append(gloss_data)
