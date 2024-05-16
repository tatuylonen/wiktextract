from wikitextprocessor import WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    word_entry.etymology_text = clean_node(
        wxr, word_entry, level_node.children
    ).removeprefix(":")
