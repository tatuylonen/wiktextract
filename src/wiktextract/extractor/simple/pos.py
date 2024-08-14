from typing import Optional

from wikitextprocessor import WikiNode
from wiktextract import WiktextractContext

from .models import WordEntry


def process_pos(
    wxr: WiktextractContext,
    child: WikiNode,
    pos_title: str,
    base_data: WordEntry,
) -> Optional[list[WordEntry]]:
    return None
