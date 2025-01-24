from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    # https://ku.wiktionary.org/wiki/Wîkîferheng:Etîmolojî
    word_entry.etymology_text = clean_node(
        wxr, word_entry, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
    )
