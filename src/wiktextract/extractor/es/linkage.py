from wikitextprocessor.parser import WikiNodeChildrenList

from wiktextract.extractor.es.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


def extract_linkage(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    nodes: WikiNodeChildrenList,
):
    pass


def process_linkage_list_children(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    nodes: WikiNodeChildrenList,
):
    pass
