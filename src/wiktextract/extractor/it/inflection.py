from dataclasses import dataclass
from itertools import chain

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_tabs_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:Tabs
    tags = [
        ["masculine", "singular"],
        ["masculine", "plural"],
        ["feminine", "singular"],
        ["feminine", "plural"],
    ]
    for arg_name in range(1, 5):
        arg_value = clean_node(
            wxr, None, node.template_parameters.get(arg_name, "")
        )
        if arg_value not in ["", wxr.wtp.title]:
            form = Form(form=arg_value, tags=tags[arg_name - 1])
            word_entry.forms.append(form)


def extract_it_decl_agg_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:It-decl-agg4
    # https://it.wiktionary.org/wiki/Template:It-decl-agg2
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        raw_tag = ""
        col_tags = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_tag = ""
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                match cell.kind:
                    case NodeKind.TABLE_HEADER_CELL:
                        col_span = cell.attrs.get("colspan", "")
                        if col_span != "":
                            raw_tag = clean_node(wxr, None, cell)
                        elif (
                            len(
                                [
                                    n
                                    for n in row.find_child(
                                        NodeKind.TABLE_HEADER_CELL
                                    )
                                ]
                            )
                            == 1
                        ):
                            row_tag = clean_node(wxr, None, cell)
                        else:
                            col_header = clean_node(wxr, None, cell)
                            if col_header != "":
                                col_tags.append(col_header)
                    case NodeKind.TABLE_CELL:
                        word = clean_node(wxr, None, cell)
                        if word not in ["", wxr.wtp.title]:
                            form = Form(form=word)
                            if raw_tag != "":
                                form.raw_tags.append(raw_tag)
                            if row_tag != "":
                                form.raw_tags.append(row_tag)
                            if col_index < len(col_tags):
                                form.raw_tags.append(col_tags[col_index])
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                        col_index += 1


def extract_appendix_conjugation_page(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    # https://it.wiktionary.org/wiki/Appendice:Coniugazioni
    page_text = wxr.wtp.get_page_body(page_title, 100)
    if page_text is None:
        return
    root = wxr.wtp.parse(page_text)
    for t_node in root.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.lower().endswith("-conj"):
            extract_conj_template(wxr, word_entry, t_node, page_title)


@dataclass
class TableHeader:
    text: str
    col_index: int
    colspan: int
    row_index: int
    rowspan: int


def extract_conj_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    page_title: str,
) -> None:
    # https://it.wiktionary.org/wiki/Template:It-conj
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        row_headers = []
        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            row_has_data = row.contain_node(NodeKind.TABLE_CELL)
            col_index = 0
            for header in chain(col_headers, row_headers):
                if (
                    row_index > header.row_index
                    and row_index < header.row_index + header.rowspan
                    and header.col_index <= col_index
                ):
                    col_index += header.colspan
            for cell_node in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_text = clean_node(wxr, None, cell_node)
                colspan = int(cell_node.attrs.get("colspan", "1"))
                rowspan = int(cell_node.attrs.get("rowspan", "1"))
                if cell_node.kind == NodeKind.TABLE_CELL:
                    pass
                elif not row_has_data:
                    col_headers.append(
                        TableHeader(
                            cell_text, col_index, colspan, row_index, rowspan
                        )
                    )
                else:
                    row_headers.append(
                        TableHeader(
                            cell_text, col_index, colspan, row_index, rowspan
                        )
                    )
                col_index += colspan

        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            col_index = 0
            added_headers = set()
            for header in chain(col_headers, row_headers):
                if (
                    row_index >= header.row_index
                    and row_index < header.row_index + header.rowspan
                    and header.col_index <= col_index
                ):
                    col_index += header.colspan
                    added_headers.add(header.text)
            for cell_node in row.find_child(
                NodeKind.TABLE_CELL | NodeKind.TABLE_HEADER_CELL
            ):
                cell_has_table = False
                for cell_table in cell_node.find_child_recursively(
                    NodeKind.TABLE
                ):
                    extract_conj_cell_table(
                        wxr,
                        word_entry,
                        cell_table,
                        row_headers,
                        col_headers,
                        page_title,
                        col_index,
                        row_index,
                    )
                    cell_has_table = True
                if not cell_has_table:
                    colspan = int(cell_node.attrs.get("colspan", "1"))
                    rowspan = int(cell_node.attrs.get("rowspan", "1"))
                    cell_text = clean_node(wxr, None, cell_node)
                    if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                        if cell_text not in added_headers:
                            col_index += colspan
                        continue
                    for line in cell_text.splitlines():
                        for form_str in line.split(","):
                            form_str = form_str.strip()
                            if form_str not in ["", "—", wxr.wtp.title]:
                                add_conj_form(
                                    word_entry,
                                    form_str,
                                    page_title,
                                    colspan,
                                    rowspan,
                                    col_index,
                                    col_headers,
                                    row_index,
                                    row_headers,
                                )
                    col_index += colspan


def extract_conj_cell_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    table_node: WikiNode,
    row_headers: list[TableHeader],
    col_headers: list[TableHeader],
    page_title: str,
    start_col_index: int,
    row_index: int,
):
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        for col_index, cell in enumerate(row.find_child(NodeKind.TABLE_CELL)):
            colspan = int(cell.attrs.get("colspan", "1"))
            rowspan = int(cell.attrs.get("rowspan", "1"))
            for cell_str in clean_node(wxr, None, cell).splitlines():
                if cell_str not in ["", "—", wxr.wtp.title]:
                    add_conj_form(
                        word_entry,
                        cell_str,
                        page_title,
                        colspan,
                        rowspan,
                        start_col_index + col_index,
                        col_headers,
                        row_index,
                        row_headers,
                    )


def add_conj_form(
    word_entry: WordEntry,
    form_str: str,
    page_title: str,
    colspan: int,
    rowspan: int,
    col_index: int,
    col_headers: list[TableHeader],
    row_index: int,
    row_headers: list[TableHeader],
):
    form = Form(form=form_str, source=page_title)
    use_tags = []
    last_col_header_row = -1
    last_row_header_col = -1
    for col_header in col_headers[::-1]:
        if (
            col_header.col_index < col_index + colspan
            and col_index < col_header.col_index + col_header.colspan
            and col_header.text not in form.raw_tags
            and col_header.text not in use_tags
            and (
                (
                    last_col_header_row != -1
                    and col_header.row_index + col_header.rowspan
                    in [last_col_header_row, last_col_header_row + 1]
                )
                or (
                    last_col_header_row == -1
                    and col_header.row_index + col_header.rowspan <= row_index
                )
            )
        ) or (
            # the last "imperativo" column header in Template:It-conj
            col_header.col_index == 0
            and col_header.row_index < row_index + rowspan
            and col_header.row_index + col_header.rowspan > row_index
        ):
            use_tags.append(col_header.text)
            last_col_header_row = col_header.row_index
    form.raw_tags.extend(use_tags[::-1])
    use_tags.clear()
    for row_header in row_headers[::-1]:
        if (
            row_header.row_index < row_index + rowspan
            and row_index < row_header.row_index + row_header.rowspan
            and row_header.text not in form.raw_tags
            and row_header.text not in use_tags
            and (
                (
                    last_row_header_col != -1
                    and (
                        row_header.col_index + row_header.colspan
                        in [last_row_header_col, last_row_header_col + 1]
                        or row_header.col_index == last_row_header_col
                    )
                )
                or (
                    last_row_header_col == -1
                    and row_header.col_index + row_header.colspan <= col_index
                )
            )
        ):
            use_tags.append(row_header.text)
            last_row_header_col = row_header.col_index
    form.raw_tags.extend(use_tags[::-1])
    translate_raw_tags(form)
    word_entry.forms.append(form)
