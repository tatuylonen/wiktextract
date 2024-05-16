from collections import defaultdict
from dataclasses import dataclass

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_inflection(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name.startswith("прил"):
            parse_adj_forms_table(wxr, word_entry, template_node)
        elif template_node.template_name.startswith("сущ"):
            parse_noun_forms_table(wxr, word_entry, template_node)


@dataclass
class TableHeader:
    text: str
    start_index: int
    span: int


def parse_adj_forms_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:прил
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_element in expanded_template.find_html("table"):
        column_headers = []
        row_headers = []
        td_rowspan = defaultdict(int)
        for tr_element in table_element.find_html("tr"):
            if len(list(tr_element.find_html("td"))) == 0:
                # all header
                current_index = 0
                for th_element in tr_element.find_html("th"):
                    header_text = ""
                    for header_link in th_element.find_child(NodeKind.LINK):
                        header_text = clean_node(
                            wxr, None, header_link.largs[0]
                        )
                    if header_text == "падеж":
                        continue  # ignore top left corner header
                    header_span = int(th_element.attrs.get("colspan", "1"))
                    column_headers.append(
                        TableHeader(header_text, current_index, header_span)
                    )
                    current_index += header_span
            else:
                col_index = 0
                has_rowspan = False
                for td_element in tr_element.find_html("td"):
                    if td_element.attrs.get("bgcolor") == "#EEF9FF":
                        # this is a td tag but contains header text
                        header_text = ""
                        for header_link in td_element.find_child(NodeKind.LINK):
                            header_text = clean_node(
                                wxr, None, header_link.largs[0]
                            )
                        header_span = int(td_element.attrs.get("rowspan", "1"))
                        row_headers.append(
                            TableHeader(header_text, 0, header_span)
                        )
                        continue
                    if "rowspan" in td_element.attrs:
                        td_rowspan[col_index] = (
                            int(td_element.attrs["rowspan"]) - 1
                        )
                        has_rowspan = True
                    elif not has_rowspan:
                        for rowspan_index, rowspan_value in td_rowspan.items():
                            if rowspan_value > 0 and col_index == rowspan_index:
                                col_index += 1
                                td_rowspan[rowspan_index] -= 1
                    td_text = clean_node(wxr, None, td_element)
                    for line in td_text.split():
                        form = Form(form=line)
                        for col_header in column_headers:
                            if (
                                col_index >= col_header.start_index
                                and col_index
                                < col_header.start_index + col_header.span
                            ):
                                form.raw_tags.append(col_header.text)
                        form.raw_tags.extend([h.text for h in row_headers])
                        if len(form.form) > 0:
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                    col_index += 1

            updated_row_headers = []
            for row_header in row_headers:
                if row_header.span > 1:
                    row_header.span -= 1
                    updated_row_headers.append(row_header)
            row_headers = updated_row_headers


def parse_noun_forms_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:сущ-ru
    # Шаблон:inflection сущ ru
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        for col_index, table_cell in enumerate(
            table_row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            )
        ):
            if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                column_headers.append(clean_node(wxr, None, table_cell))
            elif table_cell.kind == NodeKind.TABLE_CELL:
                if table_cell.attrs.get("bgcolor") == "#eef9ff":
                    row_header = clean_node(wxr, None, table_cell)
                else:
                    cell_text = clean_node(wxr, None, table_cell)
                    for form_text in cell_text.splitlines():
                        form = Form(form=form_text)
                        if len(row_header) > 0:
                            form.raw_tags.append(row_header)
                        if col_index < len(column_headers):
                            form.raw_tags.append(column_headers[col_index])
                        if len(form.form) > 0 and form.form != "—":
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
    clean_node(wxr, word_entry, expanded_template)  # add category links
