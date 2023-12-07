from wikitextprocessor import WikiNode

from wiktextract.extractor.ru.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    level_node: WikiNode,
):
    pass
