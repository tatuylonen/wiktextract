import re
from dataclasses import dataclass

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

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


def extract_conjugation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.startswith(("conj.pt", "conj/pt")):
            extract_conj_pt_template(wxr, word_entry, t_node)
        elif t_node.template_name.startswith("conj.en"):
            extract_conj_en_template(wxr, word_entry, t_node)


def extract_conj_pt_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://pt.wiktionary.org/wiki/Predefinição:conj.pt
    # https://pt.wiktionary.org/wiki/Predefinição:conj/pt
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for index, table_node in enumerate(
        expanded_node.find_child_recursively(NodeKind.TABLE)
    ):
        match index:
            case 0:
                extract_conj_pt_template_first_table(
                    wxr, word_entry, table_node
                )
            case 1:
                extract_conj_pt_template_second_table(
                    wxr, word_entry, table_node
                )


def extract_conj_pt_template_first_table(
    wxr: WiktextractContext, word_entry: WordEntry, table_node: WikiNode
) -> None:
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            match cell.kind:
                case NodeKind.TABLE_HEADER_CELL:
                    row_header = clean_node(wxr, None, cell)
                case NodeKind.TABLE_CELL:
                    form_str = clean_node(wxr, None, cell)
                    if form_str not in ["", wxr.wtp.title]:
                        form = Form(form=form_str)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)


def extract_conj_pt_template_second_table(
    wxr: WiktextractContext, word_entry: WordEntry, table_node: WikiNode
) -> None:
    col_headers = []
    row_headers = []
    row_index = 0
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        col_index = 0
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            match cell.kind:
                case NodeKind.TABLE_HEADER_CELL:
                    colspan = 1
                    colspan_str = cell.attrs.get("colspan", "1")
                    if re.fullmatch(r"\d+", colspan_str):
                        colspan = int(colspan_str)
                    rowspan = 1
                    rowspan_str = cell.attrs.get("rowspan", "1")
                    if re.fullmatch(r"\d+", rowspan_str):
                        rowspan = int(rowspan_str)
                    header_str = clean_node(wxr, None, cell)
                    if header_str == "":
                        continue
                    if rowspan > 1:
                        row_index = 0
                        row_headers.clear()
                    header = TableHeader(
                        header_str, col_index, colspan, row_index, rowspan
                    )
                    if not row.contain_node(NodeKind.TABLE_CELL):
                        col_headers.append(header)
                        col_index += colspan
                    else:
                        row_headers.append(header)
                case NodeKind.TABLE_CELL:
                    has_link = False
                    for link_node in cell.find_child(NodeKind.LINK):
                        link_str = clean_node(wxr, None, link_node)
                        if link_str not in ["", wxr.wtp.title]:
                            add_conj_pt_form(
                                word_entry,
                                link_str,
                                col_index,
                                row_index,
                                col_headers,
                                row_headers,
                            )
                        has_link = True
                    if not has_link:
                        cell_str = clean_node(wxr, None, cell)
                        if cell_str not in ["", wxr.wtp.title]:
                            add_conj_pt_form(
                                word_entry,
                                cell_str,
                                col_index,
                                row_index,
                                col_headers,
                                row_headers,
                            )
                    col_index += 1

        row_index += 1


def add_conj_pt_form(
    word_entry: WordEntry,
    form_str: str,
    col_index: int,
    row_index: int,
    col_headers: list[TableHeader],
    row_headers: list[TableHeader],
) -> None:
    form = Form(form=form_str)
    for col_header in col_headers:
        if (
            col_index >= col_header.col_index
            and col_index < col_header.col_index + col_header.colspan
        ):
            form.raw_tags.append(col_header.text)
    for row_header in row_headers:
        if (
            row_index >= row_header.row_index
            and row_index < row_header.row_index + row_header.rowspan
        ):
            form.raw_tags.append(row_header.text)
    translate_raw_tags(form)
    word_entry.forms.append(form)


def extract_conj_en_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://pt.wiktionary.org/wiki/Predefinição:conj.en
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        for row in table.find_child(NodeKind.TABLE_ROW):
            for cell in row.find_child(NodeKind.TABLE_CELL):
                raw_tag = ""
                for sup_tag in cell.find_html("sup"):
                    raw_tag = clean_node(wxr, None, sup_tag.children).strip(
                        ": "
                    )
                for list_node in cell.find_child(NodeKind.LIST):
                    for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                        for bold_node in list_item.find_child(NodeKind.BOLD):
                            form_str = clean_node(wxr, None, bold_node)
                            if form_str not in ["", wxr.wtp.title]:
                                form = Form(form=form_str)
                                if raw_tag != "":
                                    form.raw_tags.append(raw_tag)
                                translate_raw_tags(form)
                                word_entry.forms.append(form)


def extract_degree_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for index, bold_node in list_item.find_child(NodeKind.BOLD, True):
                bold_str = clean_node(wxr, None, bold_node)
                forms_str = clean_node(
                    wxr, None, list_item.children[index + 1 :]
                ).strip(": ")
                for form_str in forms_str.split(","):
                    form_str = form_str.strip()
                    if form_str not in ["", wxr.wtp.title]:
                        form = Form(form=form_str)
                        if form_str != "":
                            form.raw_tags.append(bold_str)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                break
