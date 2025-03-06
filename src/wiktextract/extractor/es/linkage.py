from wikitextprocessor.parser import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
    WikiNodeChildrenList,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_TITLES


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
):
    linkage_list = []
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        sense_nodes = []
        after_colon = False
        words = []
        for node in list_item_node.children:
            if after_colon:
                sense_nodes.append(node)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                words.append(clean_node(wxr, None, node))
            elif isinstance(node, TemplateNode) and node.template_name == "l":
                words.append(clean_node(wxr, None, node))
            elif isinstance(node, str) and ":" in node:
                after_colon = True
                sense_nodes.append(node[node.index(":") + 1 :])
        sense = clean_node(wxr, None, sense_nodes)
        for word in filter(None, words):
            linkage_list.append(Linkage(word=word, sense=sense))

    for data in page_data:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.etymology_text == page_data[-1].etymology_text
        ):
            getattr(data, linkage_type).extend(linkage_list)


def process_linkage_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # https://es.wiktionary.org/wiki/Plantilla:sinónimo
    linkage_type = LINKAGE_TITLES.get(
        template_node.template_name.removesuffix("s")
    )
    for index in range(1, 41):
        if index not in template_node.template_parameters:
            break
        linkage_data = Linkage(
            word=clean_node(wxr, None, template_node.template_parameters[index])
        )
        if len(word_entry.senses) > 0:
            linkage_data.sense_index = word_entry.senses[-1].sense_index
        getattr(word_entry, linkage_type).append(linkage_data)
        process_linkage_template_parameter(
            wxr, linkage_data, template_node, f"nota{index}"
        )
        process_linkage_template_parameter(
            wxr, linkage_data, template_node, f"alt{index}"
        )
        if index == 1:
            process_linkage_template_parameter(
                wxr, linkage_data, template_node, "nota"
            )
            process_linkage_template_parameter(
                wxr, linkage_data, template_node, "alt"
            )


def process_linkage_template_parameter(
    wxr: WiktextractContext,
    linkage_data: Linkage,
    template_node: TemplateNode,
    param: str,
) -> None:
    if param in template_node.template_parameters:
        value = clean_node(wxr, None, template_node.template_parameters[param])
        if param.startswith("nota"):
            linkage_data.note = value
        elif param.startswith("alt"):
            linkage_data.alternative_spelling = value


def process_linkage_list_children(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    nodes: WikiNodeChildrenList,
    linkage_type: str,
):
    # under gloss list
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if len(word) > 0:
                linkage_data = Linkage(word=word)
                if len(word_entry.senses) > 0:
                    linkage_data.sense_index = word_entry.senses[-1].sense_index
                getattr(word_entry, linkage_type).append(linkage_data)
