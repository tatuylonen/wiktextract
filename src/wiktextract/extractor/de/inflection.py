import re

from wikitextprocessor import NodeKind
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .flexion import parse_adj_flexion_page
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_forms(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    if template_node.template_name.endswith("Substantiv Übersicht"):
        process_noun_table(wxr, word_entry, template_node)
    elif template_node.template_name.endswith("Adjektiv Übersicht"):
        process_adj_table(wxr, word_entry, template_node)


def process_noun_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    # Vorlage:Deutsch Substantiv Übersicht
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
        is_header_row = not table_row.contain_node(NodeKind.TABLE_CELL)
        for col_index, table_cell in enumerate(
            table_row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            )
        ):
            cell_text = clean_node(wxr, None, table_cell)
            if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                if is_header_row:
                    column_headers.append(re.sub(r"\s*\d+$", "", cell_text))
                else:
                    row_header = cell_text
            else:
                for form_text in cell_text.splitlines():
                    form = Form(form=form_text)
                    if len(row_header) > 0:
                        form.raw_tags.append(row_header)
                    if col_index < len(column_headers):
                        form.raw_tags.append(column_headers[col_index])
                    if len(form.form) > 0 and form.form != "—":
                        translate_raw_tags(form)
                        word_entry.forms.append(form)

    clean_node(wxr, word_entry, expanded_template)  # category links


def process_adj_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    # Vorlage:Deutsch Adjektiv Übersicht
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        for col_index, table_cell in enumerate(
            table_row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            )
        ):
            cell_text = clean_node(wxr, None, table_cell)
            if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                column_headers.append(cell_text)
                # because {{int:}} magic word is not implemented
                # template "Textbaustein-Intl" expands to English words
                if cell_text.startswith("All other forms:"):
                    for link_node in table_cell.find_child(NodeKind.LINK):
                        parse_adj_flexion_page(
                            wxr, word_entry, clean_node(wxr, None, link_node)
                        )
            else:
                for form_text in cell_text.splitlines():
                    if form_text in ("—", ""):
                        continue
                    form = Form(form=form_text)
                    if col_index < len(column_headers):
                        form.raw_tags.append(column_headers[col_index])
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
