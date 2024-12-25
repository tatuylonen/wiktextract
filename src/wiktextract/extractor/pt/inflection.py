import re
from dataclasses import dataclass

from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


@dataclass
class TableHeader:
    text: str
    col_index: int
    colspan: int
    row_index: int
    rowspan: int


def extract_flex_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://pt.wiktionary.org/wiki/Predefinição:flex.pt
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            col_cell_index = 0
            col_header_index = 0
            for cell_node in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                col_span = 1
                col_span_str = cell_node.attrs.get("colspan", "1")
                if re.fullmatch(r"\d+", col_span_str):
                    col_span = int(col_span_str)
                cell_text = clean_node(wxr, None, cell_node)
                if cell_text == "":
                    continue
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    if row_node.contain_node(NodeKind.TABLE_CELL):
                        row_header = cell_text
                    else:
                        col_headers.append(
                            TableHeader(
                                cell_text, col_header_index, col_span, 0, 0
                            )
                        )
                    col_header_index += col_span
                elif cell_node.attrs.get("style") == "background:#f4f4f4;":
                    row_header = cell_text
                    col_header_index += col_span
                else:
                    for link_node in cell_node.find_child(NodeKind.LINK):
                        form_str = clean_node(wxr, None, link_node)
                        if form_str in ["", "–", "-", wxr.wtp.title]:
                            continue
                        form_data = Form(form=form_str)
                        if row_header != "":
                            form_data.raw_tags.append(row_header)
                        for col_header in col_headers:
                            if (
                                col_cell_index >= col_header.col_index
                                and col_cell_index
                                < col_header.col_index + col_header.colspan
                            ):
                                form_data.raw_tags.append(col_header.text)
                        translate_raw_tags(form_data)
                        word_entry.forms.append(form_data)

                    col_cell_index += col_span
