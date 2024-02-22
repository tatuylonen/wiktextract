import copy
import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode
from wiktextract.extractor.de.models import Sense, WordEntry
from wiktextract.extractor.de.utils import find_and_remove_child, match_senseid
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_glosses(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    base_sense = Sense()
    for list_node in level_node.find_child(NodeKind.LIST):
        process_gloss_list_item(wxr, word_entry, base_sense, list_node)

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in gloss section: {non_list_node}",
            sortid="extractor/de/gloss/extract_gloss/24",
        )


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    base_sense: Sense,
    list_node: WikiNode,
    parent_senseid: str = "",
    parent_gloss_data: Sense = None,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        item_type = list_item_node.sarg
        if item_type == "*":
            handle_sense_modifier(wxr, base_sense, list_item_node)
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

            sense_data = (
                copy.deepcopy(base_sense)
                if parent_gloss_data is None
                else copy.deepcopy(parent_gloss_data)
            )

            # Extract sub-glosses for later processing
            sub_glosses_list_nodes = list(
                find_and_remove_child(list_item_node, NodeKind.LIST)
            )

            raw_gloss = clean_node(wxr, {}, list_item_node.children)
            sense_data.raw_glosses = [raw_gloss]

            process_K_template(wxr, sense_data, list_item_node)

            gloss_text = clean_node(wxr, sense_data, list_item_node.children)

            senseid, gloss_text = match_senseid(gloss_text)
            if senseid != "":
                if not senseid[0].isnumeric():
                    senseid = parent_senseid + senseid
                sense_data.senseid = senseid
            elif len(gloss_text.strip()) > 0:
                wxr.wtp.debug(
                    f"Failed to extract sense number from gloss node: {list_item_node}",
                    sortid="extractor/de/glosses/extract_glosses/28",
                )

            # XXX: Extract tags from nodes instead using Italic and Template
            gloss_text = extract_tags_from_gloss_text(sense_data, gloss_text)

            if gloss_text or not sub_glosses_list_nodes:
                sense_data.glosses = [gloss_text]
                word_entry.senses.append(sense_data)

            for sub_list_node in sub_glosses_list_nodes:
                process_gloss_list_item(
                    wxr,
                    word_entry,
                    base_sense,
                    sub_list_node,
                    senseid,
                    sense_data if not gloss_text else None,
                )

        else:
            wxr.wtp.debug(
                f"Unexpected list item in glosses: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/29",
            )
            continue


def handle_sense_modifier(
    wxr: WiktextractContext, sense: Sense, list_item_node: WikiNode
):
    if len(list(list_item_node.filter_empty_str_child())) > 1:
        # XXX: Clean up sense modifier where there is more than one modifier
        wxr.wtp.debug(
            f"Found more than one child in sense modifier: {list_item_node.children}",
            sortid="extractor/de/gloss/handle_sense_modifier/114",
        )
    modifier = clean_node(wxr, {}, list_item_node.children)
    if modifier:
        sense.tags = [modifier]


def process_K_template(
    wxr: WiktextractContext,
    sense_data: Sense,
    list_item_node: NodeKind.LIST_ITEM,
) -> None:
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "K":
            categories = {"categories": []}
            text = clean_node(wxr, categories, template_node).removesuffix(":")
            sense_data.categories.extend(categories["categories"])
            tags = re.split(r";|,", text)
            sense_data.tags.extend([t.strip() for t in tags])

            # Prepositional and case information is sometimes only expanded to
            # category links and not present in cleaned node. We still want it
            # as a tag.
            prep = template_node.template_parameters.get("Prä")
            case = template_node.template_parameters.get("Kas")
            category = (prep if prep else "") + (" + " + case if case else "")
            if category:
                sense_data.tags.append(category)

            # XXX: Investigate better ways to handle free text in K template
            ft = template_node.template_parameters.get("ft")
            if ft:
                wxr.wtp.debug(
                    f"Found ft '{ft}' in K template which could be considered part of the gloss. Moved to tags for now.",
                    sortid="extractor/de/glosses/extract_glosses/63",
                )

            # Remove the template_node from the children of list_item_node
            list_item_node.children = [
                c for c in list_item_node.children if c != template_node
            ]


def extract_tags_from_gloss_text(sense_data: Sense, gloss_text: str) -> None:
    parts = gloss_text.split(":", 1)
    if len(parts) > 1:
        tags_part = parts[0].strip()

        categories = [c.strip() for c in re.split(",", tags_part)]
        if all(c.isalnum() for c in categories):
            sense_data.tags.extend(categories)
            return parts[1].strip()

    return gloss_text
