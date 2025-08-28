from collections import defaultdict
from dataclasses import dataclass

from wikitextprocessor import HTMLNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


@dataclass
class TableHeader:
    text: str
    start_index: int
    span: int


# Викисловарь:Шаблоны словоизменений


def parse_html_forms_table(
    wxr: WiktextractContext, word_entry: WordEntry, table_tag: HTMLNode
):
    # HTML table
    # https://ru.wiktionary.org/wiki/Шаблон:прил
    column_headers = []
    row_headers = []
    td_rowspan = defaultdict(int)
    for row_index, tr_element in enumerate(table_tag.find_html("tr")):
        if len(list(tr_element.find_html("td"))) == 0:
            # all column headers
            col_index = 0
            for th_element in tr_element.find_html("th"):
                header_text = ""
                for header_link in th_element.find_child(NodeKind.LINK):
                    header_text = clean_node(wxr, None, header_link)
                if header_text == "падеж":
                    continue  # ignore top left corner header
                header_span = int(th_element.attrs.get("colspan", "1"))
                column_headers.append(
                    TableHeader(header_text, col_index, header_span)
                )
                col_index += header_span
        else:  # row headers
            for node in tr_element.children:
                if isinstance(node, HTMLNode) and (
                    node.tag == "th"
                    or (
                        node.tag == "td"
                        and node.attrs.get("bgcolor") == "#EEF9FF"
                    )
                ):
                    header_text = ""
                    for header_link in node.find_child(NodeKind.LINK):
                        header_text = clean_node(wxr, None, header_link)
                    header_span = int(node.attrs.get("rowspan", "1"))
                    row_headers.append(
                        TableHeader(header_text, row_index, header_span)
                    )

    for row_index, tr_element in enumerate(table_tag.find_html("tr")):
        col_index = 0
        has_rowspan = False
        for td_element in tr_element.find_html("td"):
            rowspan = 1
            if td_element.attrs.get("bgcolor") == "#EEF9FF":
                # this is a td tag but contains header text
                continue
            if "rowspan" in td_element.attrs:
                rowspan = int(td_element.attrs["rowspan"])
                td_rowspan[col_index] = rowspan - 1
                has_rowspan = True
            elif not has_rowspan:
                for rowspan_index, rowspan_value in td_rowspan.items():
                    if rowspan_value > 0 and col_index == rowspan_index:
                        col_index += 1
                        td_rowspan[rowspan_index] -= 1
            td_text = clean_node(wxr, None, td_element)
            for line in td_text.splitlines():
                form = Form(form=line)
                for col_header in column_headers:
                    if (
                        col_index >= col_header.start_index
                        and col_index < col_header.start_index + col_header.span
                    ):
                        form.raw_tags.append(col_header.text)
                for row_header in row_headers:
                    if (
                        row_index < row_header.start_index + row_header.span
                        and row_index + rowspan > row_header.start_index
                    ):
                        form.raw_tags.append(row_header.text)
                if len(form.form) > 0:
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
            col_index += 1


def parse_wikitext_forms_table(
    wxr: WiktextractContext, word_entry: WordEntry, table_node: WikiNode
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:сущ-ru
    # Шаблон:inflection сущ ru
    # Шаблон:Гл-блок
    column_headers = []
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        row_headers = []
        has_data_cell = table_row.contain_node(NodeKind.TABLE_CELL)
        for col_index, table_cell in enumerate(
            table_row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            )
        ):
            if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                cell_text = clean_node(wxr, None, table_cell)
                if not has_data_cell:
                    column_headers.append(cell_text)
                else:
                    if cell_text == "М." and table_cell.contain_node(
                        NodeKind.LINK
                    ):
                        for link_node in table_cell.find_child(NodeKind.LINK):
                            row_headers.append(link_node.largs[0][0])
                            break
                    else:
                        row_headers.append(cell_text)
            elif table_cell.kind == NodeKind.TABLE_CELL:
                cell_text = clean_node(  # remove cursed <tr> tag
                    wxr,
                    None,
                    [
                        n
                        for n in table_cell.children
                        if not (isinstance(n, HTMLNode) and n.tag == "tr")
                    ],
                )
                if table_cell.attrs.get("bgcolor", "").lower() == "#eef9ff":
                    if cell_text == "М." and table_cell.contain_node(
                        NodeKind.LINK
                    ):
                        for link_node in table_cell.find_child(NodeKind.LINK):
                            row_headers.append(link_node.largs[0][0])
                            break
                    else:
                        row_headers.append(cell_text)
                else:
                    for form_text in cell_text.splitlines():
                        add_form_data(
                            word_entry,
                            form_text,
                            row_headers,
                            column_headers,
                            col_index,
                        )

        # cursed layout from Шаблон:Гл-блок
        # tr tag could be after or inside table cell node: Шаблон:сущ cu (-а)
        for tr_tag in table_row.find_html_recursively("tr"):
            row_headers = []
            has_th_tag = False
            for th_tag in tr_tag.find_html("th"):
                row_headers.append(clean_node(wxr, None, th_tag))
                has_th_tag = True
            for td_index, td_tag in enumerate(tr_tag.find_html("td")):
                if td_tag.contain_node(NodeKind.LINK):
                    for link_node in td_tag.find_child(NodeKind.LINK):
                        if td_tag.attrs.get("bgcolor", "").lower() == "#eef9ff":
                            row_headers.append(clean_node(wxr, None, link_node))
                        else:
                            add_form_data(
                                word_entry,
                                clean_node(wxr, None, link_node),
                                row_headers,
                                []
                                if "colspan" in td_tag.attrs
                                else column_headers,
                                td_index,
                            )
                else:
                    add_form_data(
                        word_entry,
                        clean_node(wxr, None, td_tag),
                        row_headers,
                        [] if "colspan" in td_tag.attrs else column_headers,
                        td_index + 1 if has_th_tag else td_index,
                    )


def add_form_data(
    word_entry: WordEntry,
    form_text: str,
    row_headers: list[str],
    col_headers: list[str],
    col_index: int,
) -> None:
    form = Form(form=form_text.strip(" /"))
    form.raw_tags.extend(row_headers)
    if col_index < len(col_headers) and col_headers[col_index] != "":
        form.raw_tags.append(col_headers[col_index])
    if form.form not in ["", "—", "-"]:
        translate_raw_tags(form)
        word_entry.forms.append(form)


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
