from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import WikiNodeChildrenList
from wiktextract.extractor.es.models import Linkage, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .section_titles import LINKAGE_TITLES


def extract_linkage(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    node: WikiNode,
    linkage_type: str,
):
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not found in pydantic model",
            sortid="extractor/es/linkage/extract_linkage/20",
        )
        return

    for link_node in node.find_child_recursively(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if len(word) > 0:
            getattr(word_entry, linkage_type).append(Linkage(word=word))

    for template_node in node.find_child_recursively(NodeKind.TEMPLATE):
        if template_node.template_name == "l":
            word = clean_node(wxr, None, template_node)
            if len(word) > 0:
                getattr(word_entry, linkage_type).append(Linkage(word=word))


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
            getattr(word_entry, linkage_type).append(Linkage(word=value))
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
                getattr(word_entry, linkage_type).append(Linkage(word=word))
