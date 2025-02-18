import re
from dataclasses import dataclass

from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags
from .tewandin import extract_tewandin_page


def extract_ku_tewîn_nav_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:ku-tewîn-nav
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    gender_tags = []
    gender_arg = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if gender_arg == "mê":
        gender_tags = ["feminine"]
    elif gender_arg == "nêr":
        gender_tags = ["masculine"]
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        row_header = ""
        col_headers = []
        shared_tags = []
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    header_str = clean_node(wxr, None, cell)
                    if len(row.children) == 1:
                        if header_str.endswith(" nebinavkirî"):
                            shared_tags = ["indefinite"]
                        elif header_str.endswith(" binavkirî"):
                            shared_tags = ["definite"]
                    elif row.contain_node(NodeKind.TABLE_CELL):
                        row_header = header_str
                    elif header_str not in ["Rewş", ""]:
                        col_headers.append(header_str)
                elif len(row.children) == 1:
                    continue
                else:
                    for form_str in clean_node(wxr, None, cell).splitlines():
                        if form_str not in ["", wxr.wtp.title]:
                            form = Form(
                                form=form_str, tags=gender_tags + shared_tags
                            )
                            if row_header != "":
                                form.raw_tags.append(row_header)
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                    col_index += 1


@dataclass
class TableHeader:
    text: str
    row_index: int = 0
    rowspan: int = 0
    col_index: int = 0
    colspan: int = 0


def extract_ku_tewîn_lk_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:ku-tewîn-lk
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        row_index = 0
        shared_tags = []
        row_headers = []
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            if len(row.children) == 1:
                row_str = clean_node(wxr, None, row.children)
                clear_values = False
                if row_str.endswith(" gerguhêz)"):
                    shared_tags = ["transitive"]
                    clear_values = True
                elif row_str.endswith(" negerguhêz)"):
                    shared_tags = ["intransitive"]
                    clear_values = True
                elif row_str.startswith("Rehê dema "):
                    clear_values = True
                elif row_str.startswith("Formên din:"):
                    extract_tewandin_page(wxr, word_entry, row_str[11:].strip())
                if clear_values:
                    row_index = 0
                    row_headers.clear()
                    continue
            for header_cell in row.find_child(NodeKind.TABLE_HEADER_CELL):
                rowspan = 1
                rowspan_str = header_cell.attrs.get("rowspan", "1")
                if re.fullmatch(r"\d+", rowspan_str):
                    rowspan = int(rowspan_str)
                row_headers.append(
                    TableHeader(
                        text=clean_node(wxr, None, header_cell),
                        rowspan=rowspan,
                        row_index=row_index,
                    )
                )
            for col_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                cell_str = clean_node(wxr, None, cell)
                if cell_str == "":
                    continue
                if col_index == 0:
                    row_headers.append(
                        TableHeader(
                            text=cell_str, rowspan=1, row_index=row_index
                        )
                    )
                else:
                    for form_str in cell_str.split("/"):
                        form_str = form_str.strip()
                        if form_str not in ["", wxr.wtp.title]:
                            form = Form(form=form_str, tags=shared_tags)
                            for header in row_headers:
                                if (
                                    row_index >= header.row_index
                                    and row_index
                                    < header.row_index + header.rowspan
                                ):
                                    form.raw_tags.append(header.text)
                            translate_raw_tags(form)
                            word_entry.forms.append(form)

            row_index += 1
