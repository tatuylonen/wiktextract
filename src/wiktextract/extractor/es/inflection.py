from wikitextprocessor.parser import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def process_inflect_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:inflect.es.sust.reg
    # POS headword table template
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    row_header = ""
    forms_with_row_span = []
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        col_index = 0
        is_col_header_row = not row.contain_node(NodeKind.TABLE_CELL)
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, cell)
            if cell_text == "":
                continue
            elif cell.kind == NodeKind.TABLE_HEADER_CELL:
                if is_col_header_row:
                    col_headers.append(cell_text)
                else:
                    row_header = cell_text
                    for form in forms_with_row_span[:]:
                        form.raw_tags.append(row_header)
                        translate_raw_tags(form)
                        if form.row_span == 1:
                            forms_with_row_span.remove(form)
                        else:
                            form.row_span -= 1
            elif cell.kind == NodeKind.TABLE_CELL:
                form = Form(form=cell_text)
                row_span = int(cell.attrs.get("rowspan", "1"))
                if row_span > 1:
                    forms_with_row_span.append(form)
                if len(row_header) > 0:
                    form.raw_tags.append(row_header)
                if col_index < len(col_headers):
                    form.raw_tags.append(col_headers[col_index])
                if len(form.form) > 0:
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
                col_index += 1
