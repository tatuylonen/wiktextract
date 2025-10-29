from dataclasses import dataclass
from itertools import chain

from wikitextprocessor import HTMLNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


@dataclass
class TableHeader:
    text: str
    col_index: int = 0
    colspan: int = 1
    row_index: int = 0
    rowspan: int = 1


# Викисловарь:Шаблоны словоизменений


def parse_html_forms_table(
    wxr: WiktextractContext, word_entry: WordEntry, table_tag: HTMLNode
):
    # HTML table
    # https://ru.wiktionary.org/wiki/Шаблон:прил
    # Шаблон:спряжения
    col_headers = []
    row_headers = []
    for row_index, tr_tag in enumerate(table_tag.find_html("tr")):
        row_has_data = any(tr_tag.find_html("td"))
        col_index = 0
        for header in chain(col_headers, row_headers):
            if (
                row_index > header.row_index
                and row_index < header.row_index + header.rowspan
                and header.col_index <= col_index
            ):
                col_index += header.colspan
        for th_tag in tr_tag.find_html("th"):
            th_text = clean_node(wxr, None, th_tag)
            colspan = int(th_tag.attrs.get("colspan", "1"))
            rowspan = int(th_tag.attrs.get("rowspan", "1"))
            if not row_has_data:
                col_headers.append(
                    TableHeader(th_text, col_index, colspan, row_index, rowspan)
                )
            else:
                row_headers.append(
                    TableHeader(th_text, col_index, colspan, row_index, rowspan)
                )
            col_index += colspan

    has_rowspan_td = []
    for row_index, tr_tag in enumerate(table_tag.find_html("tr")):
        col_index = 0
        last_col_header_row = 0
        for col_header in col_headers[::-1]:
            if col_header.row_index < row_index:
                last_col_header_row = col_header.row_index
                break
        for row_header in row_headers:
            if (
                row_index >= row_header.row_index
                and row_index < row_header.row_index + row_header.rowspan
                and row_header.col_index <= col_index
            ):
                col_index += row_header.colspan
        for td_tag in tr_tag.find_html("td"):
            for above_td in has_rowspan_td:
                if (
                    row_index > above_td.row_index
                    and row_index < above_td.row_index + above_td.rowspan
                    and above_td.col_index <= col_index
                ):
                    col_index += above_td.colspan
            colspan = int(td_tag.attrs.get("colspan", "1"))
            rowspan = int(td_tag.attrs.get("rowspan", "1"))
            if rowspan > 1:
                has_rowspan_td.append(
                    TableHeader("", col_index, colspan, row_index, rowspan)
                )
            td_text = clean_node(wxr, None, td_tag)
            raw_tags = []
            use_col_tags = []
            for col_header in col_headers[::-1]:
                if (
                    col_header.col_index < col_index + colspan
                    and col_index < col_header.col_index + col_header.colspan
                    and col_header.text not in raw_tags
                    and col_header.text not in use_col_tags
                    # column header above cell and above last header
                    # don't use headers for other top sections
                    and col_header.row_index + col_header.rowspan
                    in [last_col_header_row, last_col_header_row + 1]
                ):
                    use_col_tags.append(col_header.text)
            raw_tags.extend(use_col_tags[::-1])
            for row_header in row_headers:
                if (
                    row_header.row_index < row_index + rowspan
                    and row_index < row_header.row_index + row_header.rowspan
                    and row_header.text not in raw_tags
                ):
                    raw_tags.append(row_header.text)
            for line in td_text.splitlines():
                for word in line.split(","):
                    word = word.strip()
                    if word not in ["", "—", wxr.wtp.title]:
                        form = Form(form=word, raw_tags=raw_tags)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
            col_index += colspan


def parse_wikitext_forms_table(
    wxr: WiktextractContext, word_entry: WordEntry, table: WikiNode
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:сущ-ru
    # Шаблон:inflection сущ ru
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
                if cell_text == "М." and cell_node.contain_node(NodeKind.LINK):
                    for link_node in cell_node.find_child(NodeKind.LINK):
                        cell_text = clean_node(wxr, None, link_node.largs[0][0])
                        break
                row_headers.append(
                    TableHeader(
                        cell_text, col_index, colspan, row_index, rowspan
                    )
                )
            col_index += colspan

    for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
        col_index = 0
        for header in chain(col_headers, row_headers):
            if (
                row_index >= header.row_index
                and row_index < header.row_index + header.rowspan
                and header.col_index <= col_index
            ):
                col_index += header.colspan
        for cell_node in row.find_child(NodeKind.TABLE_CELL):
            colspan = int(cell_node.attrs.get("colspan", "1"))
            rowspan = int(cell_node.attrs.get("rowspan", "1"))
            cell_text = clean_node(wxr, None, cell_node)
            last_col_header_row = -1
            use_tags = []
            for line in cell_text.splitlines():
                line = line.strip("\n /")
                if line not in ["", "—", "-", wxr.wtp.title]:
                    form = Form(form=line)
                    for col_header in col_headers[::-1]:
                        if (
                            col_header.text != ""
                            and col_header.col_index < col_index + colspan
                            and col_index
                            < col_header.col_index + col_header.colspan
                            and col_header.text not in form.raw_tags
                            and col_header.text not in use_tags
                            and (
                                (
                                    last_col_header_row != -1
                                    and col_header.row_index
                                    + col_header.rowspan
                                    in [
                                        last_col_header_row,
                                        last_col_header_row + 1,
                                    ]
                                )
                                or (
                                    last_col_header_row == -1
                                    and col_header.row_index
                                    + col_header.rowspan
                                    <= row_index
                                )
                            )
                        ):
                            use_tags.append(col_header.text)
                            last_col_header_row = col_header.row_index
                    form.raw_tags.extend(use_tags[::-1])
                    use_tags.clear()
                    for row_header in row_headers[::-1]:
                        if (
                            row_header.text != ""
                            and row_header.row_index < row_index + rowspan
                            and row_index
                            < row_header.row_index + row_header.rowspan
                            and row_header.text not in form.raw_tags
                            and row_header.text not in use_tags
                        ):
                            use_tags.append(row_header.text)
                    form.raw_tags.extend(use_tags[::-1])
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
            col_index += colspan


def extract_прил_ru_comparative_forms(
    wxr: WiktextractContext, word_entry: WordEntry, expanded_node: WikiNode
) -> None:
    after_comparative = False
    for node in expanded_node.children:
        if isinstance(node, str):
            node_str = clean_node(wxr, None, node)
            if node_str.endswith("Сравнительная степень —"):
                after_comparative = True
        elif (
            after_comparative
            and isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
        ):
            for link_node in node.find_child(NodeKind.LINK):
                form = clean_node(wxr, None, link_node)
                if form != "":
                    word_entry.forms.append(
                        Form(form=form, tags=["comparative"])
                    )
