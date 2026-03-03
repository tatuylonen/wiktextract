import re

from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense, WordEntry
from .tags import translate_raw_tags
from .utils import extract_sense_index


def extract_examples(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    last_example = None
    raw_tags = []
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        if not list_item_node.sarg.endswith(":"):
            raw_tags.clear()
            raw_tag = clean_node(wxr, None, list_item_node.children)
            raw_tag = raw_tag.strip(": ")
            if raw_tag != "":
                raw_tags.append(raw_tag)
        else:
            example_data = Example(text="", raw_tags=raw_tags)
            for ref_tag in list_item_node.find_html("ref"):
                example_data.ref = clean_node(wxr, None, ref_tag.children)
            example_text_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(
                    list(
                        list_item_node.invert_find_child(
                            NodeKind.LIST, include_empty_str=True
                        )
                    )
                )
            )
            example_text = clean_node(wxr, None, example_text_node)
            sense_idx, example_text = extract_sense_index(example_text)
            if len(example_text) > 0:
                translate_raw_tags(example_data)
                example_data.text = example_text
                calculate_bold_offsets(
                    wxr,
                    example_text_node,
                    example_text,
                    example_data,
                    "bold_text_offsets",
                    extra_node_kind=NodeKind.ITALIC,
                )
                if len(sense_idx) > 0:
                    find_sense = False
                    for sense in word_entry.senses:
                        if match_sense_index(sense_idx, sense):
                            sense.examples.append(example_data)
                            find_sense = True
                    if not find_sense:
                        new_sense = Sense(
                            sense_index=sense_idx, tags=["no-gloss"]
                        )
                        new_sense.examples.append(example_data)
                        word_entry.senses.append(new_sense)
                    last_example = example_data
                elif last_example is not None:
                    last_example.translation = example_text
                    calculate_bold_offsets(
                        wxr,
                        example_text_node,
                        example_text,
                        example_data,
                        "bold_translation_offsets",
                        extra_node_kind=NodeKind.ITALIC,
                    )
                else:
                    wxr.wtp.debug(
                        f"Found example data without senseid: {example_data}",
                        sortid="extractor/de/examples/extract_examples/28",
                    )
                    last_example = None

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in examples: {non_list_node}",
            sortid="extractor/de/examples/extract_examples/33",
        )


def extract_reference(
    wxr: WiktextractContext, example_data: Example, ref_node: WikiNode
):
    example_data.ref = clean_node(wxr, None, ref_node.children)


def match_sense_index(sense_idx: str, sense: Sense) -> bool:
    exact_match = not (
        "," in sense_idx or "-" in sense_idx or "." not in sense_idx
    )
    if exact_match:
        return sense_idx == sense.sense_index

    if sense_idx == sense.sense_index:
        return True
    first_number_str = re.split(r",|\.|-|–", sense.sense_index, maxsplit=1)[0]
    first_number = 0
    if first_number_str.isdigit():
        first_number = int(first_number_str)
    else:
        return False

    for try_idx in sense_idx.split(","):
        try_idx = try_idx.strip()
        if try_idx == sense.sense_index:
            return True
        elif re.fullmatch(r"\d+[\-–]\d+", try_idx):
            start_str, end_str = re.split(r"-|–", try_idx, maxsplit=1)
            if int(start_str) <= first_number and first_number <= int(end_str):
                return True

    return False
