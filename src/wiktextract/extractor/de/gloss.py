import re
from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_glosses(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
    parent_senseid: str = "",
    parent_gloss_data: defaultdict(list) = None,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        item_type = list_item_node.sarg
        if item_type == "*":
            handle_sense_modifier(wxr, list_item_node)

        elif item_type in [":", "::"]:
            if any(
                [
                    template_node.template_name
                    in ["QS Herkunft", "QS Bedeutungen"]
                    for template_node in list_item_node.find_child_recursively(
                        NodeKind.TEMPLATE
                    )
                ]
            ):
                continue

            gloss_data = (
                defaultdict(list)
                if parent_gloss_data is None
                else parent_gloss_data.copy()
            )

            # Extract sub-glosses for later processing
            sub_glosses_list_nodes = list(
                find_and_remove_child(list_item_node, NodeKind.LIST)
            )

            raw_gloss = clean_node(wxr, gloss_data, list_item_node.children)
            gloss_data["raw_glosses"] = [raw_gloss]

            extract_categories_from_gloss_node(wxr, gloss_data, list_item_node)

            gloss_text = clean_node(wxr, gloss_data, list_item_node.children)

            senseid, gloss_text = get_senseid(gloss_text, parent_senseid)
            if senseid:
                gloss_data["senseid"] = senseid
            else:
                wxr.wtp.debug(
                    f"Failed to extract sense number from gloss node: {list_item_node}",
                    sortid="extractor/de/glosses/extract_glosses/28",
                )

            gloss_text = extract_categories_from_gloss_text(
                gloss_data, gloss_text
            )

            if gloss_text or not sub_glosses_list_nodes:
                gloss_data["glosses"] = [gloss_text]
                page_data[-1]["senses"].append(gloss_data)

            for sub_list_node in sub_glosses_list_nodes:
                extract_glosses(
                    wxr,
                    page_data,
                    sub_list_node,
                    senseid,
                    gloss_data if not gloss_text else None,
                )

        else:
            wxr.wtp.debug(
                f"Unexpected list item in glosses: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/29",
            )
            continue


def handle_sense_modifier(wxr, list_item_node):
    wxr.wtp.debug(
        f"Skipped a sense modifier in gloss list: {list_item_node}",
        sortid="extractor/de/glosses/extract_glosses/19",
    )
    # XXX: We should extract the modifier. However, it seems to affect
    # multiple glosses. Needs investigation.
    pass


def extract_categories_from_gloss_node(
    wxr: WiktextractContext,
    gloss_data: defaultdict(list),
    list_item_node: NodeKind.LIST_ITEM,
) -> None:
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "K":
            categories = template_node.template_parameters.values()

            categories = [clean_node(wxr, {}, [c]) for c in categories]

            list_item_node.children = [
                c for c in list_item_node.children if c != template_node
            ]

            gloss_data["categories"].extend(categories)


def extract_categories_from_gloss_text(
    gloss_data: defaultdict(list), gloss_text: str
) -> None:
    parts = gloss_text.split(":", 1)
    if len(parts) > 1:
        categories_part = parts[0].strip()

        categories = [c.strip() for c in re.split(",|and", categories_part)]
        if all(c.isalnum() for c in categories):
            gloss_data["categories"].extend(categories)
            return parts[1].strip()

    return gloss_text


def get_senseid(gloss_text: str, parent_senseid=""):
    match = re.match(r"\[(\d*[a-z]?)\]", gloss_text)

    if match:
        senseid = match.group(1)
        gloss_text = gloss_text[match.end() :].strip()

        senseid = (
            senseid if senseid[0].isnumeric() else parent_senseid + senseid
        )
    else:
        senseid = None

    return senseid, gloss_text


def find_and_remove_child(node, kind):
    children = []
    for idx, child in reversed(list(node.find_child(kind, with_index=True))):
        del node.children[idx]
        children.append(child)
    return reversed(children)
