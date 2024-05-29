from wikitextprocessor import NodeKind
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_inflection(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
) -> None:
    if template_node.template_name.startswith("inflect."):
        process_inflect_template(wxr, page_data, template_node)


def process_inflect_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:inflect.es.sust.reg
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        for col_index, cell in enumerate(
            row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
        ):
            cell_text = clean_node(wxr, None, cell)
            if cell.kind == NodeKind.TABLE_HEADER_CELL:
                col_headers.append(cell_text)
            else:
                form = Form(form=cell_text)
                if col_index < len(col_headers):
                    form.raw_tags.append(col_headers[col_index])
                if len(form.form) > 0:
                    translate_raw_tags(form)
                    page_data[-1].forms.append(form)
