from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    # https://it.wiktionary.org/wiki/Aiuto:Etimologia
    etymology_texts = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            e_str = clean_node(wxr, None, list_item.children)
            if e_str != "":
                etymology_texts.append(e_str)

    if len(etymology_texts) == 0:
        e_str = clean_node(
            wxr,
            None,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
        )
        if e_str != "":
            etymology_texts.append(e_str)

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.etymology_texts.extend(etymology_texts)


def extract_citation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    examples = []
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.lower() == "quote":
            example = Example()
            first_arg = wxr.wtp.parse(t_node.template_parameters.get(1, ""))
            example.text = clean_node(wxr, None, first_arg)
            example.ref = clean_node(
                wxr, None, t_node.template_parameters.get(2, "")
            )
            calculate_bold_offsets(
                wxr, first_arg, example.text, example, "bold_text_offsets"
            )
            if example.text != "":
                examples.append(example)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.etymology_examples.extend(examples)
