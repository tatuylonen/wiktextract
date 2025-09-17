from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    e_str = clean_node(
        wxr,
        base_data,
        list(
            level_node.invert_find_child(
                LEVEL_KIND_FLAGS, include_empty_str=True
            )
        ),
    )
    if e_str != "":
        base_data.etymology_text = e_str
