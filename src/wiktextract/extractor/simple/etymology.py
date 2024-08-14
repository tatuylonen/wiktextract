from wikitextprocessor import WikiNode

from .models import WordEntry


def process_etym(
    child: WikiNode, data: WordEntry
) -> None: ...
