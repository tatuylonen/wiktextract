import re
from collections import defaultdict

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense, WordEntry


def extract_example_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    examples = defaultdict(list)
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_example_list_item(wxr, list_item, examples)

    for data in page_data:
        if data.lang_code != base_data.lang_code:
            continue
        for sense in data.senses:
            if sense.sense_index in examples:
                sense.examples.extend(examples[sense.sense_index])
                del examples[sense.sense_index]
            sense.examples.extend(examples[""])

    if "" in examples:
        del examples[""]
    if len(page_data) == 0 or page_data[-1].lang_code != base_data.lang_code:
        page_data.append(base_data.model_copy(deep=True))
    for sense_index, example_list in examples.items():
        sense_data = Sense(
            tags=["no-gloss"],
            examples=example_list,
            sense_index=sense_index,
        )
        page_data[-1].senses.append(sense_data)


def process_example_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    examples: dict[str, list[Example]],
) -> None:
    sense_index = ""
    example_data = Example()
    translation_start = 0
    example_start = 0
    for index, node in enumerate(list_item.children):
        if isinstance(node, str):
            m = re.search(r"\(\d+\.\d+\)", node)
            if m is not None:
                sense_index = m.group(0).strip("()")
                example_start = index + 1
            elif "→" in node:
                translation_start = index + 1
                break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            example_data.text = clean_node(wxr, None, node)
            calculate_bold_link_offsets(
                wxr, node, example_data.text, example_data
            )
        elif isinstance(node, HTMLNode) and node.tag == "ref":
            example_data.ref = clean_node(wxr, None, node.children)
    if translation_start != 0:
        lit_start = len(list_item.children)
        for t_index, node in enumerate(
            list_item.children[translation_start:], translation_start
        ):
            if isinstance(node, TemplateNode) and node.template_name == "dosł":
                example_data.literal_meaning = clean_node(
                    wxr, None, list_item.children[t_index + 1 :]
                ).strip("() ")
                lit_start = t_index
                break
        example_data.translation = clean_node(
            wxr, None, list_item.children[translation_start:lit_start]
        ).strip("() ")
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(
                    list_item.children[translation_start:lit_start]
                )
            ),
            example_data.translation,
            example_data,
            "bold_translation_offsets",
        )
        if len(example_data.text) == 0:
            example_data.text = clean_node(
                wxr, None, list_item.children[example_start:translation_start]
            ).strip("→ ")
            calculate_bold_link_offsets(
                wxr,
                wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(
                        list_item.children[example_start:translation_start]
                    )
                ),
                example_data.text,
                example_data,
            )
    if "(" in example_data.text and example_data.text.endswith(")"):
        roman_start = example_data.text.rindex("(")
        example_data.roman = example_data.text[roman_start:].strip("() ")
        example_data.text = example_data.text[:roman_start].strip()
    if len(example_data.text) > 0:
        examples[sense_index].append(example_data)


def calculate_bold_link_offsets(
    wxr: WiktextractContext, node: WikiNode, text: str, example: Example
):
    bold_words = []
    for link_node in node.find_child(NodeKind.LINK):
        if len(link_node.largs) > 0:
            link_dest = clean_node(wxr, None, link_node.largs[0])
            if link_dest == wxr.wtp.title:
                link_text = clean_node(wxr, None, link_node)
                if link_text not in bold_words:
                    bold_words.append(link_text)

    for bold_word in bold_words:
        for m in re.finditer(re.escape(bold_word), text):
            example.bold_text_offsets.append((m.start(), m.end()))
