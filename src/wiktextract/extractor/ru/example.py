from wikitextprocessor import WikiNode

from wiktextract.extractor.ru.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


def process_example_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    pass
    # wxr.wtp.debug(str(template_node), sortid="example")
