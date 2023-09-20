from collections import defaultdict
from typing import Dict, List

import re

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_glosses(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        item_type = list_item_node.sarg
        if item_type == "*":
            wxr.wtp.debug(
                f"Skipped a sense modifier in gloss list: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/19",
            )
            # XXX: We should extract the modifier. However, it seems to affect
            # multiple glosses. Needs investigation.
            pass
        elif item_type == ":":
            gloss_data = defaultdict(list)
            for sub_list_node in list_item_node.find_child(NodeKind.LIST):
                wxr.wtp.debug(
                    f"Skipped a sub-list in gloss list: {sub_list_node}",
                    sortid="extractor/de/glosses/extract_glosses/27",
                )
                # XXX: We should extract the subglosses as subsenses.
                pass

            gloss_text = clean_node(wxr, gloss_data, list_item_node.children)

            match = re.match(r"\[(\d+[a-z]?)\]", gloss_text)
            if match:
                sense_number = match.group(1)
                gloss_text = gloss_text[match.end() :].strip()
            else:
                sense_number = None

            if not sense_number:
                wxr.wtp.debug(
                    f"Failed to extract sense number from gloss: {gloss_text}",
                    sortid="extractor/de/glosses/extract_glosses/28",
                )

            gloss_data["glosses"] = [gloss_text]

            page_data[-1]["senses"].append(gloss_data)

        else:
            wxr.wtp.debug(
                f"Unexpected list item in glosses: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/29",
            )
            continue
