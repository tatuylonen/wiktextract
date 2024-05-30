from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode, WikiNodeChildrenList

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
    linkage_type = LINKAGE_TITLES.get(
        template_node.template_name.removesuffix("s")
    )
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not found in pydantic model",
            sortid="extractor/es/linkage/process_linkage_template/51",
        )
        return

    linkage_list = getattr(word_entry, linkage_type)
    for key, value_raw in template_node.template_parameters.items():
        value = clean_node(wxr, None, value_raw)
        if isinstance(key, int):
            linkage_data = Linkage(word=value)
            if len(word_entry.senses) > 0:
                linkage_data.senseid = word_entry.senses[-1].senseid
            getattr(word_entry, linkage_type).append(linkage_data)
        elif isinstance(key, str):
            if key.startswith("nota"):
                idx = int(key[4:]) - 1 if len(key) > 4 else 0
                if len(linkage_list) > idx:
                    linkage_list[idx].note = value
            elif key.startswith("alt"):
                idx = int(key[3:]) - 1 if len(key) > 3 else 0
                if len(linkage_list) > idx:
                    linkage_list[idx].alternative_spelling = value


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
