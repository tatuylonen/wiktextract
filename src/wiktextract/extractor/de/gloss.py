import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Sense, WordEntry
from .utils import match_senseid


def extract_glosses(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    sense = Sense()
    for list_node in level_node.find_child(NodeKind.LIST):
        sense = process_gloss_list_item(wxr, word_entry, list_node, sense)

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in gloss section: {non_list_node}",
            sortid="extractor/de/gloss/extract_gloss/24",
        )


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_node: WikiNode,
    parent_sense: Sense,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        item_type = list_item_node.sarg
        if item_type == "*":  # only contains modifier template
            for template in list_item_node.find_child(NodeKind.TEMPLATE):
                raw_tag = clean_node(wxr, parent_sense, template).removesuffix(
                    ":"
                )
                parent_sense = Sense()
                parent_sense.raw_tags.append(raw_tag)
        elif item_type.endswith(":"):
            sense_data = parent_sense.model_copy(deep=True)
            gloss_nodes = []
            for gloss_node in list_item_node.children:
                if isinstance(gloss_node, TemplateNode):
                    if gloss_node.template_name == "K":
                        for (
                            k_arg,
                            k_arg_value,
                        ) in gloss_node.template_parameters.items():
                            if k_arg == "ft":
                                gloss_nodes.append(
                                    clean_node(wxr, None, k_arg_value)
                                )
                                gloss_nodes.append(":")
                            elif isinstance(k_arg, int):
                                raw_tag = clean_node(wxr, None, k_arg_value)
                                sense_data.raw_tags.append(raw_tag)
                        clean_node(wxr, sense_data, gloss_node)
                    elif gloss_node.template_name in (
                        "QS Herkunft",
                        "QS Bedeutungen",
                    ):
                        continue
                elif (
                    isinstance(gloss_node, WikiNode)
                    and gloss_node.kind == NodeKind.ITALIC
                ):
                    raw_tag = clean_node(wxr, None, gloss_node).removesuffix(
                        ":"
                    )
                    sense_data.raw_tags.append(raw_tag)
                elif not (
                    isinstance(gloss_node, WikiNode)
                    and gloss_node.kind == NodeKind.LIST
                ):
                    gloss_nodes.append(gloss_node)

            gloss_text = clean_node(wxr, sense_data, gloss_nodes)
            senseid, gloss_text = match_senseid(gloss_text)
            if senseid != "":
                if (
                    not senseid[0].isnumeric()
                    and parent_sense is not None
                    and len(parent_sense.senseid) != ""
                ):
                    senseid = parent_sense.senseid + senseid
                sense_data.senseid = senseid
            elif len(gloss_text.strip()) > 0:
                wxr.wtp.debug(
                    "Failed to extract sense number from gloss node",
                    sortid="extractor/de/glosses/extract_glosses/28",
                )

            if len(gloss_text) > 0:
                sense_data.glosses.append(gloss_text)
                word_entry.senses.append(sense_data)

            for sub_list_node in list_item_node.find_child(NodeKind.LIST):
                process_gloss_list_item(
                    wxr,
                    word_entry,
                    sub_list_node,
                    sense_data,
                )

        else:
            wxr.wtp.debug(
                f"Unexpected list item in glosses: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/29",
            )
            continue
    return parent_sense


def extract_tags_from_gloss_text(sense_data: Sense, gloss_text: str) -> None:
    parts = gloss_text.split(":", 1)
    if len(parts) > 1:
        tags_part = parts[0].strip()

        categories = [c.strip() for c in re.split(",", tags_part)]
        if all(c.isalnum() for c in categories):
            sense_data.raw_tags.extend(categories)
            return parts[1].strip()

    return gloss_text
