from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: TemplateNode
) -> None:
    text = clean_node(
        wxr, word_entry, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
    )
    if not text.startswith("Si puedes, incorpórala: ver cómo"):
        word_entry.etymology_text = text
