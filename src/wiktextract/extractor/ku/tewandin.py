import re
from itertools import count

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_tewandin_page(
    wxr: WiktextractContext, word_entry: WordEntry, title: str
) -> None:
    page = wxr.wtp.get_page(title, 106)
    if page is None or page.body is None:
        return
    root = wxr.wtp.parse(page.body)
    for t_node in root.find_child(NodeKind.TEMPLATE):
        extract_tewandin_template(wxr, word_entry, t_node, title)
    for level_node in root.find_child(LEVEL_KIND_FLAGS):
        for t_node in level_node.find_child(NodeKind.TEMPLATE):
            extract_tewandin_template(wxr, word_entry, t_node, title)


def extract_tewandin_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    source_page: str,
    tab_name: str = "",
    form_set: set[str] = set(),
) -> None:
    if t_node.template_name == "ku-tewandin":
        extract_ku_tewandin_template(
            wxr,
            word_entry,
            t_node,
            source_page,
            tab_name=tab_name,
            form_set=form_set,
        )
    elif t_node.template_name == "etîket tewandin":
        extract_etîket_tewandin_template(wxr, word_entry, t_node, source_page)


def extract_ku_tewandin_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    source_page: str,
    tab_name: str = "",
    form_set: set[str] = {},
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:ku-tewandin
    from .form_table import TableHeader

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    clean_node(wxr, word_entry, expanded_node)
    for table in expanded_node.find_child_recursively(NodeKind.TABLE):
        col_headers = []
        last_row_has_data_cell = False
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_str = clean_node(wxr, None, cell)
                if cell_str == "":
                    continue
                colspan = 1
                colspan_str = cell.attrs.get("colspan", "1")
                if re.fullmatch(r"\d+", colspan_str):
                    colspan = int(colspan_str)
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if row.contain_node(NodeKind.TABLE_CELL):
                        row_header = cell_str
                    else:
                        if last_row_has_data_cell:
                            col_headers.clear()
                        col_headers.append(
                            TableHeader(
                                text=cell_str,
                                col_index=col_index,
                                colspan=colspan,
                            )
                        )
                        col_index += colspan
                        last_row_has_data_cell = False
                else:
                    last_row_has_data_cell = True
                    form = Form(form=cell_str, source=source_page)
                    if tab_name != "":
                        form.raw_tags.append(tab_name)
                    if row_header != "":
                        form.raw_tags.append(row_header)
                    for header in col_headers:
                        if (
                            col_index >= header.col_index
                            and col_index < header.col_index + header.colspan
                        ):
                            form.raw_tags.append(header.text)
                    if form.form != wxr.wtp.title and form.form not in form_set:
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                        form_set.add(form.form)
                    col_index += colspan


def extract_etîket_tewandin_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    source_page: str,
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:etîket_tewandin
    form_set = set()
    for num in count(1):
        tab_name_arg = f"etîket{num}"
        if tab_name_arg not in t_node.template_parameters:
            break
        tab_name = clean_node(
            wxr, None, t_node.template_parameters[tab_name_arg]
        )
        tab_arg = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                t_node.template_parameters[f"naverok{num}"]
            )
        )
        for node in tab_arg.find_child(NodeKind.TEMPLATE):
            extract_tewandin_template(
                wxr,
                word_entry,
                node,
                source_page,
                tab_name=tab_name,
                form_set=form_set,
            )
