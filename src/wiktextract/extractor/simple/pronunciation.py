from wikitextprocessor import WikiNode

from .models import WordEntry


def process_pron(
    child: WikiNode, data: WordEntry
) -> None: ...
