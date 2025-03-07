import re

from wikitextprocessor import WikiNode
from wikitextprocessor.parser import NodeKind

from wiktextract.wxr_context import WiktextractContext

from .models import Linkage, WordEntry
from .parse_utils import Heading

Node = str | WikiNode

LINK_RE = re.compile(r"(__/?L__)")


def process_linkage_section(
    wxr: WiktextractContext,
    data: WordEntry,
    rnode: WikiNode,
    linkage_type: Heading,
) -> None:
    def links_node_fn(
        node: WikiNode,
    ) -> list[Node] | None:
        """Handle nodes in the parse tree specially."""
        if node.kind == NodeKind.LINK:
            if not isinstance(node.largs[0][0], str):
                return None
            return [
                "__L__",
                # unpacking a list-comprehension, unpacking into a list
                # seems to be more performant than adding lists together.
                *(
                    wxr.wtp.node_to_text(
                        node.largs[1:2] or node.largs[0],
                    )
                    # output the "visible" half of the link.
                ),
                # XXX collect link data if it turns out to be important.
                "__/L__",
            ]
            # print(f"{node.largs=}")
        return None

    # parse nodes to get lists and list_items
    reparsed = wxr.wtp.parse(wxr.wtp.node_to_wikitext(rnode), expand_all=True)

    chained_links: list[list[str]] = [[]]

    for list_item in reparsed.find_child_recursively(NodeKind.LIST_ITEM):
        text = wxr.wtp.node_to_text(list_item, node_handler_fn=links_node_fn)

        inside_link = False
        interrupted_link = False

        for i, token in enumerate(LINK_RE.split(text)):
            token = token.strip()

            if i % 2 == 0:
                # Actual text, not __L__or __/L__
                if inside_link is False and token:
                    # There's something between two link nodes
                    interrupted_link = True
                    continue
                if inside_link is True:
                    if interrupted_link is True and len(chained_links[-1]) > 0:
                        chained_links.append([token])
                    else:
                        chained_links[-1].append(token)
                    continue
            if token == "__L__":
                inside_link = True
                continue
            else:
                inside_link = False
                interrupted_link = False
                continue

    match linkage_type:
        case Heading.Related:
            target_field = data.related
        case Heading.Synonyms:
            target_field = data.synonyms
        case Heading.Antonyms:
            target_field = data.antonyms
        case Heading.Derived:
            target_field = data.derived
        case _:
            wxr.wtp.error("process_linkage_section() given unhandled Heading: "
                          f"{linkage_type=}", sortid="linkages/83")
            return

    target_field.extend(
        Linkage(word=" ".join(parts)) for parts in chained_links
    )

    # iterate over list item lines and get links

    # if links are next to each other with only whitespace between,
    # that's part of one entry

    # if there's something that isn't a link in-between, then they're
    # separate words
