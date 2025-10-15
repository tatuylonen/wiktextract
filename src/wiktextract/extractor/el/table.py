import re
from typing import TypeAlias
from unicodedata import name as unicode_name

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from wiktextract.clean import clean_value
from wiktextract.extractor.el.tags import translate_raw_tags
from wiktextract.wxr_context import WiktextractContext

from .models import Form, WordEntry
from .parse_utils import GREEK_LANGCODES, remove_duplicate_forms

# from .simple_tags import simple_tag_map
# from .tags_utils import convert_tags

# Shorthand for this file. Could be an import, but it's so simple...
Node = str | WikiNode


# GREEK TABLE HEURISTICS:
# If it's a table for a Greek language entry, if it's in a header or is in
# italics, it's a header.
# If it's NOT a Greek entry and has Greek text, it's a header.


# node_fns are different from template_fns. template_fns are functions that
# are used to handle how to expand (and otherwise process) templates, while
# node functions are used when turning any parsed "abstract" nodes into strings.
def cell_node_fn(
    node: WikiNode,
) -> list[Node] | None:
    """Handle nodes in the parse tree specially."""
    assert isinstance(node, WikiNode)
    if node.kind == NodeKind.ITALIC:
        return ["__I__", *node.children, "__/I__"]
    if node.kind == NodeKind.BOLD:
        return ["__B__", *node.children, "__/B__"]
    # In case someone puts tables inside tables...
    kind = node.kind
    if kind in {
        NodeKind.TABLE_CELL,
        NodeKind.TABLE_HEADER_CELL,
    }:
        return node.children
    return None


BOLD_RE = re.compile(r"(__/?[BI]__)")

ARTICLES: set[str] = {
    "ο",
    "η",
    "το",
    "την",
    "της",
    "τον",
    "τη",
    "το",
    "οι",
    "οι",
    "τα",
    "των",
    "τους",
    "του",
    "τις",
    "τα",
}

UNEXPECTED_ARTICLES = {
    "αι",
    "ένα",
    "ένας",
    "στα",
    "στη",
    "στην",
    "στης",
    "στις",
    "στο",
    "στον",
    "στου",
    "στους",
    "στων",
    "τ'",
    "ταις",
    "τας",
    "τες",
    "τη",
    "τοις",
    "τω",
}
"""Includes contractions, Ancient Greek articles etc."""


def process_inflection_section(
    wxr: WiktextractContext, data: WordEntry, snode: WikiNode
) -> None:
    table_nodes: list[tuple[str | None, WikiNode]] = []
    # template_depth is used as a nonlocal variable in bold_node_handler
    # to gauge how deep inside a top-level template we are; we want to
    # collect template data only for the top-level templates that are
    # visible in the wikitext, not templates inside templates.
    template_depth = 0
    top_template_name: str | None = None

    def table_node_handler_fn(
        node: WikiNode,
    ) -> list[str | WikiNode] | None:
        """Insert special markers `__*__` and `__/*__` around bold nodes so
        that the strings can later be split into "head-word" and "tag-words"
        parts. Collect incidental stuff, like side-tables, that are often
        put around the head."""
        assert isinstance(node, WikiNode)
        kind = node.kind
        nonlocal template_depth
        nonlocal top_template_name
        if isinstance(node, TemplateNode):
            # Recursively expand templates so that even nodes inside the
            # the templates are handled with bold_node_handler.
            # Argh. Don't use "node_to_text", that causes bad output...
            expanded = wxr.wtp.expand(wxr.wtp.node_to_wikitext(node))
            if template_depth == 0:
                # We are looking at a top-level template in the original
                # wikitext.
                top_template_name = node.template_name
            new_node = wxr.wtp.parse(expanded)

            template_depth += 1
            ret = wxr.wtp.node_to_text(
                new_node, node_handler_fn=table_node_handler_fn
            )
            template_depth -= 1
            if template_depth == 0:
                top_template_name = None
            return ret

        if kind in {
            NodeKind.TABLE,
        }:
            # XXX Handle tables here
            # template depth and top-level template name
            nonlocal table_nodes
            table_nodes.append((top_template_name, node))
            return [""]
        return None

    _ = wxr.wtp.node_to_html(snode, node_handler_fn=table_node_handler_fn)

    if len(table_nodes) > 0:
        for template_name, table_node in table_nodes:
            # XXX template_name
            parse_table(
                wxr,
                table_node,
                data,
                data.lang_code in GREEK_LANGCODES,
                template_name=template_name or "",
            )

            for form in data.forms:
                translate_raw_tags(form)

            # Postprocess forms.
            # XXX This should probably go into a "postprocess_forms"
            # function, together with "remove_duplicate_forms" just below.
            for form in data.forms:
                parts = form.form.split()
                # * Remove articles
                if len(parts) > 1 and parts[0] in ARTICLES:
                    form.form = " ".join(parts[1:])

                if not form.form:
                    continue

                # Parens > rare inflection (cf. μπόι)
                if form.form[0] == "(" and form.form[-1] == ")":
                    form.form = form.form[1:-1]
                    form.tags.append("rare")

    data.forms = remove_duplicate_forms(wxr, data.forms)


def parse_table(
    wxr: WiktextractContext,
    tnode: WikiNode,
    data: WordEntry,
    is_greek_entry: bool = False,  # Whether the entry is for a Greek word
    template_name: str = "",
) -> None:
    """Parse inflection table. Generates 'form' data; 'foos' is a form of 'foo'
    with the tags ['plural']."""
    assert (isinstance(tnode, WikiNode) and tnode.kind == NodeKind.TABLE) or (
        isinstance(tnode, HTMLNode) and tnode.tag == "table"
    )

    is_html_table = isinstance(tnode, HTMLNode)

    # Some debugging code: if wiktwords is passed a --inflection-tables-file
    # argument, we save tables to a file for debugging purposes, or for just
    # getting tables that can be used as test data.
    if wxr.config.expand_tables:
        with open(wxr.config.expand_tables, "w") as f:
            f.write(f"{wxr.wtp.title=}\n")
            text = wxr.wtp.node_to_wikitext(tnode)
            f.write(f"{text}\n")

    Row: TypeAlias = int
    Column: TypeAlias = int

    # We complete the table using nested dicts (instead of arrays for
    # convenience) such that when we come across a node, we push that node's
    # reference to each coordinate point in the table grid it occupies. Each
    # grid point can then be checked for if it's been handled already and
    # skipped if needed.
    table_grid: dict[Row, dict[Column, WikiNode]] = {}

    first_column_is_headers = True

    for r, row in enumerate(
        tnode.find_html_recursively("tr")
        if is_html_table
        else tnode.find_child_recursively(NodeKind.TABLE_ROW)
    ):
        c = 0
        # print(f"{r=}, {row=}")
        if r not in table_grid:
            table_grid[r] = {}

        for cell in (
            row.find_html(["th", "td"])
            if is_html_table
            else row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL,
            )
        ):
            while c in table_grid[r]:
                c += 1

            try:
                rowspan = int(cell.attrs.get("rowspan", "1"))  # 🡙
                colspan = int(cell.attrs.get("colspan", "1"))  # 🡘
            except ValueError:
                rowspan = 1
                colspan = 1
            # print("COL:", col)

            if colspan > 30:
                wxr.wtp.error(
                    f"Colspan {colspan} over 30, set to 1",
                    sortid="table/128/20250207",
                )
                colspan = 1
            if rowspan > 30:
                wxr.wtp.error(
                    f"Rowspan {rowspan} over 30, set to 1",
                    sortid="table/134/20250207b",
                )
                rowspan = 1

            for rr in range(r, r + rowspan):
                if rr not in table_grid:
                    table_grid[rr] = {}
                for cc in range(c, c + colspan):
                    table_grid[rr][cc] = cell

    if not table_grid[len(table_grid) - 1]:
        # Last row is empty; traverse backwards to skip empty rows at end
        last_item = None
        for i, rowd in reversed(table_grid.items()):
            if rowd:
                last_item = i
                break

        assert last_item is not None

        new_table_grid = dict()
        for i, rowd in table_grid.items():
            if i > last_item:
                continue
            new_table_grid[i] = rowd
        table_grid = new_table_grid

    if len(table_grid[0]) == 1:
        # Table is one column in width, no headers on rows
        first_column_is_headers = False

    if len(table_grid) == 2:
        # There's only one or two rows
        first_column_is_headers = False

    # Headers are saved in two dict that has their keys made out of tuples
    # made of their "bookends": so {(1,1), "foo"} for a header that is made
    # up of the first cell only of a row in the column_hdrs dict.
    # If we come across a header that has those exact same bookends, only
    # then do we replace the previous tags with it; if you have overlapping
    # 'widths', leave them so that we inherit different 'levels' of headers.
    Spread = tuple[int, int]
    SpreadDict = dict[Spread, str]
    # The column and row headers are saved into big dicts: column_hdrs is a dict
    # whose key is what row or column we are in. The values of that table grid
    # square is a dict with the bookends (`Spread`) and the tags associated with
    # those bookends
    column_hdrs_all: dict[Column, SpreadDict] = {}
    row_hdrs_all: dict[Row, dict[Column, SpreadDict]] = {}

    forms: list[Form] = []
    processed: set[WikiNode] = set()
    # Some tables have cells with stuff like `του` we want to add to the
    # next cell
    prefix: str | None = None

    # print(f"{table_grid=}")

    first_cells_are_bold = False
    found_unformatted_text = False

    for r, row_d in table_grid.items():
        # Check for previously added row headers that may have spread lower;
        # Remove old row headers that don't exist on this row.
        for c, cell in row_d.items():
            if cell in processed:
                continue
            processed.add(cell)

            try:
                rowspan = int(cell.attrs.get("rowspan", "1"))  # 🡙
                colspan = int(cell.attrs.get("colspan", "1"))  # 🡘
            except ValueError:
                rowspan = 1
                colspan = 1

            spans = process_cell_text(wxr, cell)

            if len(spans) <= 0:
                continue

            if r == 0:
                if spans[0][0]:  # starts_bold
                    first_cells_are_bold = True

            text = clean_value(wxr, " ".join(span[3] for span in spans))
            # print(f"{text=}")

            this_is_header, unformatted_text = is_header(
                wxr,
                cell,
                spans,
                is_greek_entry,
                found_unformatted_text,
                first_cells_are_bold,
            )

            if unformatted_text is True:
                found_unformatted_text = True

            if this_is_header or (c == 0 and first_column_is_headers is True):
                # Because Greek wiktionary has its own written script to rely
                # in heuristics, we can use that. It also seems that for
                # tables in Greek-language entries even if the table doesn't
                # use proper header cells, you can trust bolding and italics.

                # Currently we don't care which "direction" the header points:
                # we add the tag to both column headers and row headers, and
                # rely on that all headers are on only rows or columns that
                # don't have data cells; ie. headers and data aren't mixed.

                # Each row and each column gets its own header data.
                # The Spread key is used to keep track which headers should
                # "overlap": if the spread is different, that should always
                # mean that one is contained within another and thus they're
                # not complementary headers, but one "bigger" category and
                # one "specific" category. If the Spread is identical, then
                # that's obviously two complementary headers, and the later one
                # overwrites the other.
                for rr in range(r, r + rowspan):
                    if rr not in row_hdrs_all:
                        row_hdrs_all[rr] = {c: {(r, r + rowspan): text}}
                    elif c not in row_hdrs_all[rr]:
                        row_hdrs_all[rr][c] = {(r, r + rowspan): text}
                    else:
                        # Also overwrites headers with the same "span"; simple
                        # way to have overlapping sections.
                        row_hdrs_all[rr][c][(r, r + rowspan)] = text

                for cc in range(c, c + colspan):
                    if cc not in column_hdrs_all:
                        column_hdrs_all[cc] = {(c, c + colspan): text}
                    else:
                        column_hdrs_all[cc][(c, c + colspan)] = text

                prefix = None

            elif text in ARTICLES:
                prefix = text
            else:
                # cell is data
                if text in UNEXPECTED_ARTICLES:
                    wxr.wtp.debug(
                        f"Found '{text}' in table '{wxr.wtp.title}'",
                        sortid="table/335",
                    )
                tags: set[str] = set()
                for cc, vd in row_hdrs_all.get(r, {}).items():
                    if c <= cc:
                        continue
                    for (start, end), tag in vd.items():
                        if start > r or end < r + rowspan:
                            continue
                        tags.add(tag)
                for (start, end), tag in column_hdrs_all.get(c, {}).items():
                    if start > c or end < c + colspan:
                        continue
                    tags.add(tag)
                texts = [text]
                if "&" in text:
                    texts = [t.strip() for t in text.split("&")]
                # Avert your eyes... Python list comprehension syntax amirite
                texts = [line for text in texts for line in text.splitlines()]
                if prefix is not None:
                    texts = [f"{prefix} {t}" for t in texts]
                    prefix = None
                if len(tags) > 0:
                    # If a cell has no tags in a table, it's probably a note
                    # or something.
                    forms.extend(
                        Form(form=text, raw_tags=list(tags)) for text in texts
                    )
                else:
                    wxr.wtp.warning(
                        f"Cell without any tags in table: {text}",
                        sortid="table/300/20250217",
                    )

    # logger.debug(
    #     f"{wxr.wtp.title}\n{print_tree(tree, indent=2, ret_value=True)}"
    # )
    # print(forms)

    # # Replace raw_tags with tags if appropriate
    # for form in forms:
    #     legit_tags, new_raw_tags, poses = convert_tags(form.raw_tags)
    #     # Poses are strings like "adj 1", used in pronunciation data
    #     # to later associate sound data with the correct pos entry.
    #     # Ignored here.
    #     if legit_tags:
    #         form.tags = legit_tags
    #         form.tags.extend(poses)
    #         form.raw_tags = new_raw_tags
    # print(f"Inside parse_table: {forms=}")

    if len(forms) > 0:
        data.forms.append(
            Form(form=template_name, tags=["inflection-template"])
        )

        data.forms.extend(forms)


def process_cell_text(
    wxr: WiktextractContext, cell: WikiNode
) -> list[tuple[bool, bool, bool, str]]:
    cell_text = wxr.wtp.node_to_text(cell, node_handler_fn=cell_node_fn)
    cell_text = clean_value(wxr, cell_text)
    split_text = BOLD_RE.split(cell_text)

    # bold, italics, is greek, text
    spans: list[tuple[bool, bool, bool, str]] = []

    inside_bold = False
    inside_italics = False
    for i, text in enumerate(split_text):
        text = text.strip()
        if not text:
            continue
        if i % 2 == 0:
            for ch in text:
                if not ch.isalpha():
                    continue
                greek = unicode_name(ch).startswith("GREEK")
                break
            else:
                # no alphanumerics detected
                continue

            spans.append((inside_bold, inside_italics, greek, text))
            continue
        match text:
            case "__B__":
                inside_bold = True
            case "__/B__":
                inside_bold = False
            case "__I__":
                inside_italics = True
            case "__/I__":
                inside_italics = False

    return spans


UnformattedFound: TypeAlias = bool


def is_header(
    wxr: WiktextractContext,
    cell: WikiNode,
    spans: list[tuple[bool, bool, bool, str]],
    is_greek_entry: bool,
    unformatted_text_found: bool,
    first_cells_are_bold,
) -> tuple[bool, UnformattedFound]:
    # Container for more complex logic stuff because trying to figure out
    # if something is a header can get messy.
    if cell.kind == NodeKind.TABLE_HEADER_CELL:
        return True, False

    starts_bold, starts_italicized, starts_greek, text = spans[0]

    if "bold" in cell.attrs.get("style", ""):
        starts_bold = True
    if "italic" in cell.attrs.get("style", ""):
        starts_italicized = True

    # Not a Greek entry
    if not is_greek_entry:
        if starts_greek:
            # If the table is for another language other than Greek, a cell
            # starting with Greek text is a table header
            return True, (starts_bold or starts_italicized)
        else:
            return False, (starts_bold or starts_italicized)

    # Is a Greek entry
    if starts_italicized is True:
        return True, False

    if starts_bold is False:
        return False, True

    if unformatted_text_found:
        # This is bolded, but we've seen unformatted text before
        return True, False
    # print(f"{text=}-> {starts_bold=}, {starts_italicized=}, {starts_greek=}")

    if first_cells_are_bold:
        return True, False

    wxr.wtp.warning(
        f"Can't be sure if bolded text entry '{text}' is a header or not",
        sortid="table/20250210a",
    )
    return False, False
