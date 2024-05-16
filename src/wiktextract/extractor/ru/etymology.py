from wikitextprocessor import WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    etymology_nodes = []
    for node in level_node.invert_find_child(LEVEL_KIND_FLAGS):
        if isinstance(node, TemplateNode) and node.template_name == "improve":
            # ignore this template
            continue
        etymology_nodes.append(node)
    word_entry.etymology_text = clean_node(wxr, word_entry, etymology_nodes)
