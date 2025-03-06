from dataclasses import dataclass

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_conjugation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: WikiNode
) -> None:
    forms = []
    cats = []
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if "es.v.conj." in t_node.template_name:
            new_forms, new_cats = process_es_v_conj_template(wxr, t_node)
            forms.extend(new_forms)
            cats.extend(new_cats)
        elif t_node.template_name == "es.v":
            new_forms, new_cats = process_es_v_template(wxr, t_node)
            forms.extend(new_forms)
            cats.extend(new_cats)

    for data in page_data:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.etymology_text == page_data[-1].etymology_text
        ):
            data.forms.extend(forms)
            data.categories.extend(cats)


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
    wxr: WiktextractContext, template_node: TemplateNode
) -> tuple[list[Form], list[str]]:
    # https://es.wiktionary.org/wiki/Plantilla:es.v.conj
    forms = []
    cats = {}
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    clean_node(wxr, cats, expanded_node)
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
                    col_cell_index += colspan - 1
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
                        forms.append(form)
                col_cell_index += colspan
    return forms, cats.get("categories", [])


def process_es_v_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> tuple[list[Form], list[str]]:
    # https://es.wiktionary.org/wiki/Plantilla:es.v
    forms = []
    cats = {}
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    clean_node(wxr, cats, expanded_node)
    table_nodes = list(expanded_node.find_child_recursively(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        single_cell = len(list(row.filter_empty_str_child())) == 1
        all_header_row = row.contain_node(
            NodeKind.TABLE_HEADER_CELL
        ) and not row.contain_node(NodeKind.TABLE_CELL)
        if not all_header_row and single_cell:
            continue  # ignore end notes
        if all_header_row and single_cell:
            col_headers.clear()  # new table

        col_index = 0
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, cell)
            if cell_text == "":
                continue
            if cell.kind == NodeKind.TABLE_HEADER_CELL:
                if all_header_row:
                    colspan = int(cell.attrs.get("colspan", "1"))
                    col_headers.append(
                        SpanHeader(
                            cell_text.removeprefix("Modo ").strip(),
                            col_index,
                            colspan,
                        )
                    )
                    col_index += colspan
                else:
                    row_header = cell_text.removesuffix("^†").strip()
            else:
                cell_nodes = []
                for node in cell.children:
                    if not (
                        isinstance(node, HTMLNode)
                        and "movil" in node.attrs.get("class", "")
                    ):
                        cell_nodes.append(node)  # hidden HTML tag
                cell_text = clean_node(wxr, None, cell_nodes)
                for word in cell_text.split(","):
                    word = word.strip()
                    form = Form(form=word)
                    for col_head in col_headers:
                        if (
                            col_index >= col_head.index
                            and col_index < col_head.index + col_head.span
                        ):
                            form.raw_tags.append(col_head.text)
                    if row_header != "":
                        form.raw_tags.append(row_header)
                    if form.form not in ["", "―"]:
                        translate_raw_tags(form)
                        forms.append(form)
                col_index += 1
    return forms, cats.get("categories", [])
