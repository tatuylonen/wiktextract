from wikitextprocessor import NodeKind, WikiNode

from wiktextract.extractor.ru.models import WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    level_node: WikiNode,
):
    if not linkage_type in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not defined for word entry",
            sortid="extractor/ru/linkage/extract_linkages/10",
        )
        return
    for link_node in level_node.find_child_recursively(NodeKind.LINK):
        word = clean_node(wxr, {}, link_node).strip()
        if word:
            getattr(word_entry, linkage_type).append(word)
