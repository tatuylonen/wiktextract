from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Linkage, WordEntry


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    level_node: WikiNode,
):
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not defined for word entry",
            sortid="extractor/ru/linkage/extract_linkages/10",
        )
        return
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        linkage = Linkage()
        for node in list_item.children:
            if isinstance(node, WikiNode):
                if node.kind == NodeKind.LINK:
                    linkage.word = clean_node(wxr, None, node)
                elif isinstance(node, TemplateNode):
                    find_linkage_tag(wxr, linkage, node)
            elif isinstance(node, str) and node.strip() in (";", ","):
                if len(linkage.word) > 0:
                    getattr(word_entry, linkage_type).append(linkage)
                    tags = linkage.tags
                    linkage = Linkage()
                    if node.strip() == ",":
                        linkage.tags = tags

        if len(linkage.word) > 0:
            getattr(word_entry, linkage_type).append(linkage)
            linkage = Linkage()


def find_linkage_tag(
    wxr: WiktextractContext,
    linkage: Linkage,
    template_node: TemplateNode,
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for span_node in expanded_template.find_html_recursively("span"):
        if "title" in span_node.attrs:
            tag = span_node.attrs["title"]
        else:
            tag = clean_node(wxr, None, span_node)
        if len(tag) > 0:
            linkage.tags.append(tag)
