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
        if t_node.template_name == "es.v":
            new_forms, new_cats = process_es_v_template(wxr, t_node)
            forms.extend(new_forms)
            cats.extend(new_cats)

    for data in page_data:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.etymology_text == page_data[-1].etymology_text
            and data.pos == "verb"  # should be fixed on Wiktionary
        ):
            data.forms.extend(forms)
            data.categories.extend(cats)


@dataclass
class SpanHeader:
    text: str
    index: int
    span: int


# https://en.wikipedia.org/wiki/Spanish_pronouns
PRONOUN_TAGS = {
    "yo": ["first-person", "singular"],
    "que yo": ["first-person", "singular"],
    "tú": ["second-person", "singular"],
    "que tú": ["second-person", "singular"],
    "(tú)": ["second-person", "singular"],
    "vos": ["second-person", "singular", "vos-form"],
    "que vos": ["second-person", "singular", "vos-form"],
    "(vos)": ["second-person", "singular", "vos-form"],
    "él, ella, usted": ["third-person", "singular"],
    "que él, que ella, que usted": ["third-person", "singular"],
    "(usted)": ["third-person", "singular"],
    "nosotros": ["first-person", "plural"],
    "que nosotros": ["first-person", "plural"],
    "(nosotros)": ["first-person", "plural"],
    "vosotros": ["second-person", "plural"],
    "que vosotros": ["second-person", "plural"],
    "(vosotros)": ["second-person", "plural"],
    "ustedes, ellos": ["third-person", "plural"],
    "que ustedes, que ellos": ["third-person", "plural"],
    "(ustedes)": ["third-person", "plural"],
}


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
        return [], []
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
        is_archaic_row = False
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
                    is_archaic_row = cell_text.endswith("^†")
                    row_header = cell_text.removesuffix("^†").strip()
            else:
                cell_nodes = []
                for node in cell.children:
                    if isinstance(node, HTMLNode) and node.tag == "sup":
                        sup_tag = clean_node(wxr, None, node.children)
                        if sup_tag != "" and len(forms) > 0:
                            forms[-1].raw_tags.append(sup_tag)
                            translate_raw_tags(forms[-1])
                    elif (
                        isinstance(node, WikiNode)
                        and node.kind == NodeKind.LINK
                    ):
                        cell_nodes.append(node)
                        form = Form(
                            form=clean_node(wxr, None, cell_nodes).lstrip(", ")
                        )
                        for col_head in col_headers:
                            if (
                                col_index >= col_head.index
                                and col_index < col_head.index + col_head.span
                            ):
                                form.raw_tags.append(col_head.text)
                                form.tags.extend(
                                    PRONOUN_TAGS.get(col_head.text, [])
                                )
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if is_archaic_row:
                            form.tags.append("archaic")
                        if form.form not in ["", "―"]:
                            translate_raw_tags(form)
                            forms.append(form)
                        cell_nodes.clear()
                    elif not (
                        isinstance(node, HTMLNode)
                        and "movil" in node.attrs.get("class", "")
                    ):
                        cell_nodes.append(node)  # hidden HTML tag
                col_index += 1
    return forms, cats.get("categories", [])
