from wikitextprocessor.parser import (
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
    word_entry: WordEntry,
    title_node: WikiNode,
    linkage_type: str,
):
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not found in pydantic model",
            sortid="extractor/es/linkage/extract_linkage/20",
        )
        return
    for list_item_node in title_node.find_child_recursively(NodeKind.LIST_ITEM):
        data = Linkage(word="")
        sense_nodes = []
        for node in list_item_node.children:
            if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                data.word = clean_node(wxr, None, node)
            elif isinstance(node, TemplateNode) and node.template_name == "l":
                data.word = clean_node(wxr, None, node)
            else:
                sense_nodes.append(node)
        data.sense = clean_node(wxr, None, sense_nodes).strip(": ")
        if len(data.word) > 0:
            getattr(word_entry, linkage_type).append(data)


def process_linkage_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # https://es.wiktionary.org/wiki/Plantilla:sinónimo
    linkage_type = LINKAGE_TITLES.get(
        template_node.template_name.removesuffix("s")
    )
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not found in pydantic model",
            sortid="extractor/es/linkage/process_linkage_template/51",
        )
        return

    for index in range(1, 41):
        if index not in template_node.template_parameters:
            break
        linkage_data = Linkage(
            word=clean_node(wxr, None, template_node.template_parameters[index])
        )
        if len(word_entry.senses) > 0:
            linkage_data.senseid = word_entry.senses[-1].senseid
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
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not found in pydantic model",
            sortid="extractor/es/linkage/process_linkage_list_children/89",
        )
        return
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if len(word) > 0:
                linkage_data = Linkage(word=word)
                if len(word_entry.senses) > 0:
                    linkage_data.senseid = word_entry.senses[-1].senseid
                getattr(word_entry, linkage_type).append(linkage_data)
