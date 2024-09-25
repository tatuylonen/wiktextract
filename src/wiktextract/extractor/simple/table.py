from itertools import chain
from typing import Optional, Union

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode
from wikitextprocessor.parser import print_tree
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .models import Form, WordEntry
from .simple_tags import simple_tag_map
from .tags_utils import convert_tags

Node = Union[str, WikiNode]


def cell_node_fn(
    node: WikiNode,
) -> Optional[list[Node]]:
    assert isinstance(node, WikiNode)
    if node.kind == NodeKind.ITALIC:
        # If we have italicized text 'none', like in `deviate`, turn it to "–"
        if (
            len(node.children) == 1
            and isinstance(node.children[0], str)
            and node.children[0].strip() == "none"
        ):
            return ["–"]
    # This latter bit is from the default node_handler function and really
    # unnecessary, but in case someone puts tables inside tables...
    kind = node.kind
    if kind in {
        NodeKind.TABLE_CELL,
        NodeKind.TABLE_HEADER_CELL,
    }:
        return node.children
    return None


def parse_pos_table(
    wxr: WiktextractContext, tnode: TemplateNode, data: WordEntry
) -> list[Form]:
    assert isinstance(tnode, TemplateNode)
    tree = wxr.wtp.parse(wxr.wtp.node_to_wikitext(tnode), expand_all=True)

    # Check if there are actually headers, because Simple English Wiktionary
    # doesn't use them in these POS template tables.
    # Headers and non-headers in other editions can be a real headache.
    for header in tree.find_child_recursively(NodeKind.TABLE_HEADER_CELL):
        wxr.wtp.debug(
            f"POS template table has headers! {repr(header)[:255]}",
            sortid="simple/table/45",
        )

    # A typical SEngW table has simple 2-line cells, without headers, EXCEPT
    # some have actual table structure like "did". That's why we do thing
    # row-by-row.
    column_hdrs: dict[int, str] = {}
    forms: list[Form] = []
    for row in chain(
        tree.find_child_recursively(NodeKind.TABLE_ROW),
        tree.find_html_recursively("tr"),
    ):
        row_hdr = ""
        for i, cell in chain(
            row.find_child(NodeKind.TABLE_CELL, with_index=True),
            row.find_html("td", with_index=True, attr_name="", attr_value=""),
        ):
            text = clean_node(
                wxr, data, cell, node_handler_fn=cell_node_fn
            ).strip()
            if not text:
                if i not in column_hdrs:
                    column_hdrs[i] = ""
                continue
            lines = [s.strip() for s in text.splitlines()]
            if len(lines) != 2:
                logger.debug(
                    f"{wxr.wtp.title}: A cell that's "
                    f"not exactly 2 lines: {repr(text)}"
                )
            if len(lines) == 1:
                # XXX do tag parsing instead of i == 0
                if text in simple_tag_map:
                    if i == 0:
                        row_hdr = text
                    column_hdrs[i] = text
                else:
                    tags = []
                    if column_hdrs[i]:
                        tags.append(column_hdrs[i])
                    if row_hdr:
                        tags.append(row_hdr)
                    forms.append(Form(form=text, raw_tags=tags))
                # Add a single line cell as a column header and trust it
                # will be overridden as appropriate
                # Only applicable to Simple English wiktionary!
                column_hdrs[i] = text

                continue
            if len(lines) == 2:
                column_hdrs[i] = lines[0]
                cell_content = lines[1]
                tags = []
                if column_hdrs[i]:
                    tags.append(column_hdrs[i])
                if row_hdr:
                    tags.append(row_hdr)
                forms.append(Form(form=cell_content, raw_tags=tags))

    # logger.debug(
    #     f"{wxr.wtp.title}\n{print_tree(tree, indent=2, ret_value=True)}"
    # )
    # print(forms)
    # Replace raw_tags with tags if appropriate
    for form in forms:
        legit_tags, new_raw_tags, poses = convert_tags(form.raw_tags)
        # XXX poses are strings like "adj 1", used in pronunciation data
        # to later associate sound data with the correct pos entry.
        # Not useful or common here?
        # if len(poses) > 0:  # This spams the logs
        #     wxr.wtp.warning(f"convert_tags() returned weird `poses` data for "
        #                     f"forms: {poses=}", sortid="simple/table/122")
        if legit_tags:
            form.tags = legit_tags
            form.raw_tags = new_raw_tags

    return forms


def extract_cells(wxr: WiktextractContext, table: HTMLNode) -> list[Node]:
    assert table.sarg == "table"
    return []
