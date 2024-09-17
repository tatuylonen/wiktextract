from typing import Union

from wikitextprocessor import LevelNode, WikiNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .etymology import process_etym
from .models import WordEntry
from .pronunciation import process_pron

Node = Union[str, WikiNode]

def separate_subsections(node: WikiNode) -> tuple[list[Node], list[WikiNode]]:
    i = 0  # needed if for loop doesn't run
    for i, child in enumerate(node.children):
        if isinstance(child, LevelNode):
            break
    else:  # when ending for loop, if there was no break:
        i += 1
    # We are pretty much guaranteed that the second half of children is only
    # level kinds
    return node.children[:i], node.children[i:]  # type: ignore[return-value]


def recurse_base_data_sections(
    wxr: WiktextractContext, node: WikiNode, target_data: WordEntry
) -> None:
    # Parse a section recursively; a heading node with contents and possible
    # subsections (always following the non-subsection content)
    content, subsections = separate_subsections(node)
    # clean_node; usually, when cleaning node text we'd want to collect
    # category link data into a WordEntry or similar data object, but
    # Simple English Wiktionary headings don't have any of that so we can skip.
    heading_title = clean_node(wxr, None, node.largs[0]).lower()

    # We ignore all other sections other than pronunciation currently,
    # because it's the only one that ends up appearing as a subsection
    if heading_title.startswith("pronunciation"):
        # Replace sound data in target_data with new data, if applicable
        process_pron(wxr, content, target_data)
    elif heading_title.startswith("etymology") or heading_title.startswith(
        "word parts"
    ):
        # Replace etymology data in target_data with new data, if applicable
        process_etym(wxr, content, target_data)

    # recurse into subsections to find other data
    for subsection in subsections:
        assert isinstance(subsection, LevelNode)
        recurse_base_data_sections(wxr, subsection, target_data)
