from dataclasses import dataclass

from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_inflection_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in ["tr-ad-tablo", "tr-eylem-tablo"]:
            extract_tr_ad_tablo_template(wxr, word_entry, t_node)


@dataclass
class SpanHeader:
    text: str
    index: int
    span: int


def extract_tr_ad_tablo_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)
    for table in expanded_node.find_child_recursively(NodeKind.TABLE):
        last_row_has_data = False
        col_headers = []
        row_headers = []
        row_index = 0
        for row in table.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            row_has_data = row.contain_node(NodeKind.TABLE_CELL)
            if not row_has_data and not row.contain_node(
                NodeKind.TABLE_HEADER_CELL
            ):
                continue
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_text == "":
                    continue
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if not row_has_data:
                        if last_row_has_data:  # new table
                            col_headers.clear()
                            row_headers.clear()
                            col_index = 0
                            row_index = 0
                        colspan = int(cell.attrs.get("colspan", "1"))
                        col_headers.append(
                            SpanHeader(cell_text, col_index, colspan)
                        )
                        col_index += colspan
                    else:
                        rowspan = int(cell.attrs.get("rowspan", "1"))
                        row_headers.append(
                            SpanHeader(cell_text, row_index, rowspan)
                        )
                elif cell.kind == NodeKind.TABLE_CELL:
                    if cell_text == "—":
                        col_index += 1
                        continue
                    for line in cell_text.splitlines():
                        word = line.strip()
                        if word == "":
                            continue
                        form = Form(form=word)
                        for col_head in col_headers:
                            if (
                                col_index >= col_head.index
                                and col_index < col_head.index + col_head.span
                            ):
                                form.raw_tags.append(col_head.text)
                        for row_head in row_headers:
                            if (
                                row_index >= row_head.index
                                and row_index < row_head.index + row_head.span
                            ):
                                form.raw_tags.append(row_head.text)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                    col_index += 1
            row_index += 1
            last_row_has_data = row_has_data
