from dataclasses import dataclass

from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_declension_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.startswith(
            ("Substantivum ", "Adjektivum ", "Stupňování ")
        ):
            extract_substantivum_template(wxr, word_entry, t_node)


@dataclass
class TableHeader:
    text: str
    colspan: int
    rowspan: int
    col_index: int
    row_index: int


def extract_substantivum_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://cs.wiktionary.org/wiki/Šablona:Substantivum_(cs)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            row_header = ""
            is_column_header = not row.contain_node(NodeKind.TABLE_CELL)
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_text = clean_node(wxr, None, cell)
                colspan = int(cell.attrs.get("colspan", "1"))
                rowspan = int(cell.attrs.get("rowspan", "1"))
                for col_header in col_headers:
                    if (
                        col_header.rowspan > 1
                        and col_header.row_index <= row_index
                        and col_header.row_index + col_header.rowspan
                        > row_index
                    ):
                        col_index += col_header.colspan
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if is_column_header:
                        col_headers.append(
                            TableHeader(
                                cell_text,
                                colspan,
                                rowspan,
                                col_index,
                                row_index,
                            )
                        )
                    elif not is_column_header:
                        row_header = cell_text
                else:
                    for word in cell_text.split("/"):
                        word = word.strip()
                        if word in ["", wxr.wtp.title]:
                            continue
                        form = Form(form=word)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        for col_header in col_headers:
                            if (
                                col_header.col_index <= col_index
                                and col_header.col_index + col_header.colspan
                                > col_index
                            ):
                                form.raw_tags.append(col_header.text)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                col_index += colspan
