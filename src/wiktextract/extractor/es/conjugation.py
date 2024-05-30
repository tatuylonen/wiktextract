from dataclasses import dataclass

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_conjugation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        process_conjugation_template(wxr, word_entry, template_node)


def process_conjugation_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    if "es.v.conj." in template_node.template_name:
        process_es_v_conj_template(wxr, word_entry, template_node)


@dataclass
class SpanHeader:
    text: str
    index: int
    span: int


IGNORE_ES_V_ROW_PREFIXES = (
    "Modo ",
    "Tiempos ",
)
IGNORE_ES_V_HEADERS = {"número:", "persona:"}


def process_es_v_conj_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:es.v.conj
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        all_header_row = not row.contain_node(NodeKind.TABLE_CELL)
        if row.contain_node(NodeKind.TABLE_HEADER_CELL) and all_header_row:
            first_header = next(row.find_child(NodeKind.TABLE_HEADER_CELL))
            first_header_text = clean_node(wxr, None, first_header)
            if first_header_text.startswith(IGNORE_ES_V_ROW_PREFIXES):
                continue  # ignore personal pronouns row
            elif len(list(row.filter_empty_str_child())) == 1:  # new table
                col_headers.clear()
                continue
        if row.contain_node(NodeKind.TABLE_CELL) and not row.contain_node(
            NodeKind.TABLE_HEADER_CELL
        ):
            continue  # ignore end notes

        col_header_index = 0
        col_cell_index = 0
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, cell)
            colspan = int(cell.attrs.get("colspan", "1"))
            if cell_text == "" or cell_text in IGNORE_ES_V_HEADERS:
                continue
            elif cell.kind == NodeKind.TABLE_HEADER_CELL:
                if all_header_row:
                    col_headers.append(
                        SpanHeader(cell_text, col_header_index, colspan)
                    )
                else:
                    row_header = cell_text
                col_header_index += colspan
            else:
                for line in cell_text.splitlines():
                    form = Form(form=line)
                    if row_header != "":
                        form.raw_tags.extend(row_header.split(" o "))
                    for col_head in col_headers:
                        if (
                            col_cell_index >= col_head.index
                            and col_cell_index < col_head.index + col_head.span
                        ):
                            form.raw_tags.append(col_head.text)

                    if form.form != "":
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                col_cell_index += colspan
