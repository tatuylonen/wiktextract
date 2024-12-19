import re
from dataclasses import dataclass

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_tabs_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:Tabs
    tags = [
        ["masculine", "singular"],
        ["masculine", "plural"],
        ["feminine", "singular"],
        ["feminine", "plural"],
    ]
    for arg_name in range(1, 5):
        arg_value = clean_node(
            wxr, None, node.template_parameters.get(arg_name, "")
        )
        if arg_value not in ["", wxr.wtp.title]:
            form = Form(form=arg_value, tags=tags[arg_name - 1])
            word_entry.forms.append(form)


def extract_it_decl_agg_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:It-decl-agg4
    # https://it.wiktionary.org/wiki/Template:It-decl-agg2
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        raw_tag = ""
        col_tags = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_tag = ""
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                match cell.kind:
                    case NodeKind.TABLE_HEADER_CELL:
                        col_span = cell.attrs.get("colspan", "")
                        if col_span != "":
                            raw_tag = clean_node(wxr, None, cell)
                        elif (
                            len(
                                [
                                    n
                                    for n in row.find_child(
                                        NodeKind.TABLE_HEADER_CELL
                                    )
                                ]
                            )
                            == 1
                        ):
                            row_tag = clean_node(wxr, None, cell)
                        else:
                            col_header = clean_node(wxr, None, cell)
                            if col_header != "":
                                col_tags.append(col_header)
                    case NodeKind.TABLE_CELL:
                        word = clean_node(wxr, None, cell)
                        if word not in ["", wxr.wtp.title]:
                            form = Form(form=word)
                            if raw_tag != "":
                                form.raw_tags.append(raw_tag)
                            if row_tag != "":
                                form.raw_tags.append(row_tag)
                            if col_index < len(col_tags):
                                form.raw_tags.append(col_tags[col_index])
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                        col_index += 1


def extract_appendix_conjugation_page(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    # https://it.wiktionary.org/wiki/Appendice:Coniugazioni
    page_text = wxr.wtp.get_page_body(page_title, 100)
    if page_text is None:
        return
    root = wxr.wtp.parse(page_text)
    for t_node in root.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.lower() == "it-conj":
            extract_it_conj_template(wxr, word_entry, t_node, page_title)


@dataclass
class TableHeader:
    text: str
    col_index: int
    colspan: int
    row_index: int
    rowspan: int


def extract_it_conj_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    page_title: str,
) -> None:
    # https://it.wiktionary.org/wiki/Template:It-conj
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        row_header = ""
        for row in table.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                match cell.kind:
                    case NodeKind.TABLE_HEADER_CELL:
                        header_str = clean_node(wxr, None, cell)
                        if header_str in ["persona", "indicativo"]:
                            continue
                        elif header_str in ["condizionale", "congiuntivo"]:
                            col_headers.clear()
                            continue
                        elif header_str == "imperativo":
                            col_headers.clear()
                            row_header = "imperativo"
                            continue

                        if row.contain_node(NodeKind.TABLE_CELL):
                            row_header = header_str
                        else:
                            colspan = 1
                            colspan_str = cell.attrs.get("colspan", "1")
                            if re.fullmatch(r"\d+", colspan_str):
                                colspan = int(colspan_str)
                            col_headers.append(
                                TableHeader(
                                    header_str, col_index, colspan, 0, 0
                                )
                            )
                            col_index += colspan
                    case NodeKind.TABLE_CELL:
                        cell_has_table = False
                        for cell_table in cell.find_child_recursively(
                            NodeKind.TABLE
                        ):
                            extract_it_conj_cell_table(
                                wxr,
                                word_entry,
                                cell_table,
                                row_header,
                                col_headers,
                                page_title,
                            )
                            cell_has_table = True
                        if not cell_has_table:
                            for form_str in clean_node(
                                wxr, None, cell
                            ).splitlines():
                                form_str = form_str.strip(", ")
                                if form_str.startswith("verbo di "):
                                    continue  # first row
                                if form_str not in ["", wxr.wtp.title]:
                                    add_it_conj_form(
                                        word_entry,
                                        form_str,
                                        page_title,
                                        row_header,
                                        col_index,
                                        col_headers,
                                    )
                        col_index += 1


def extract_it_conj_cell_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    table_node: WikiNode,
    row_header: str,
    col_headers: list[TableHeader],
    page_title: str,
) -> None:
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        for col_index, cell in enumerate(row.find_child(NodeKind.TABLE_CELL)):
            for cell_str in clean_node(wxr, None, cell).splitlines():
                if cell_str not in ["", wxr.wtp.title]:
                    add_it_conj_form(
                        word_entry,
                        cell_str,
                        page_title,
                        row_header,
                        col_index,
                        col_headers,
                    )


def add_it_conj_form(
    word_entry: WordEntry,
    form_str: str,
    page_title: str,
    row_header: str,
    col_index: int,
    col_headers: list[TableHeader],
) -> None:
    form = Form(form=form_str, source=page_title)
    if row_header != "":
        form.raw_tags.append(row_header)
    for col_header in col_headers:
        if (
            col_index >= col_header.col_index
            and col_index < col_header.col_index + col_header.colspan
        ):
            form.raw_tags.append(col_header.text)
    translate_raw_tags(form)
    word_entry.forms.append(form)
