from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Linkage, WordEntry


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    sense = ""
    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "rel-top"
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child_recursively(NodeKind.LIST_ITEM):
                process_linkage_list_item(
                    wxr, word_entry, list_item, linkage_type, sense
                )


def process_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    sense: str,
) -> None:
    for node in list_item.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            ("おくりがな", "ふりがな", "xlink")
        ):
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node), expand_all=True
            )
            ruby, no_ruby = extract_ruby(wxr, expanded_node.children)
            if node.template_name == "xlink":
                ruby.clear()
            word = clean_node(wxr, None, no_ruby)
            if len(word) > 0:
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, ruby=ruby, sense=sense)
                )
        elif node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if len(word) > 0:
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, sense=sense)
                )
