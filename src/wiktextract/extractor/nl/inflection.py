import re
from dataclasses import dataclass

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags

FORMS_TABLE_TEMPLATES = frozenset(
    [
        "-nlnoun-",
        "adjcomp",
        "-nlname-",
        "-denoun-",
        "-denoun1-",
        "-nlstam-",
        "-csadjc-comp-",
    ]
)


def extract_inflection_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    if t_node.template_name in [
        "-nlnoun-",
        "adjcomp",
        "-nlname-",
        "-denoun-",
        "-denoun1-",
    ]:
        extract_noun_adj_table(wxr, word_entry, t_node)
    elif t_node.template_name == "-nlstam-":
        extract_nlstam_template(wxr, word_entry, t_node)
    elif t_node.template_name.startswith("-csadjc-comp-"):
        extract_csadjc_comp_template(wxr, word_entry, t_node)


def extract_noun_adj_table(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-nlnoun-
    # https://nl.wiktionary.org/wiki/Sjabloon:adjcomp
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    column_headers = []
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            for header_node in row_node.find_child(NodeKind.TABLE_HEADER_CELL):
                header_text = clean_node(wxr, None, header_node)
                if header_text != "":
                    column_headers.append(header_text)
            row_header = ""
            for col_index, data_node in enumerate(
                row_node.find_child(NodeKind.TABLE_CELL)
            ):
                if col_index == 0:
                    row_header = clean_node(wxr, None, data_node)
                else:
                    for form_str in clean_node(
                        wxr, None, data_node
                    ).splitlines():
                        if form_str not in ["", "-", wxr.wtp.title]:
                            form = Form(form=form_str)
                            if row_header not in ["", "naamwoord", "demoniem"]:
                                form.raw_tags.append(row_header)
                            if col_index - 1 < len(column_headers):
                                form.raw_tags.append(
                                    column_headers[col_index - 1]
                                )
                            translate_raw_tags(form)
                            word_entry.forms.append(form)

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)


def extract_nlstam_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # verb table
    # https://nl.wiktionary.org/wiki/Sjabloon:-nlstam-
    for arg in [2, 3]:
        form_texts = clean_node(
            wxr, None, t_node.template_parameters.get(arg, "")
        )
        ipa_texts = clean_node(
            wxr, None, t_node.template_parameters.get(arg + 3, "")
        ).splitlines()
        for index, form_str in enumerate(form_texts.splitlines()):
            if form_str != "":
                form = Form(form=form_str)
                if index < len(ipa_texts):
                    form.ipa = ipa_texts[index]
                form.tags.extend(
                    ["past"] if arg == 2 else ["past", "participle"]
                )
                word_entry.forms.append(form)
    clean_node(wxr, word_entry, t_node)
    if not word_entry.extracted_vervoeging_page:
        extract_vervoeging_page(wxr, word_entry)
        word_entry.extracted_vervoeging_page = True


def extract_vervoeging_page(
    wxr: WiktextractContext, word_entry: WordEntry
) -> None:
    page = wxr.wtp.get_page(f"{wxr.wtp.title}/vervoeging", 0)
    if page is None:
        return
    root = wxr.wtp.parse(page.body)
    table_templates = ["-nlverb-", "-nlverb-reflex-", "-nlverb-onp-"]
    for t_node in root.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in table_templates:
            extract_nlverb_template(wxr, word_entry, t_node, "")
    sense = ""
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        sense = clean_node(wxr, None, level_node.largs)
        for t_node in level_node.find_child(NodeKind.TEMPLATE):
            if t_node.template_name in table_templates:
                extract_nlverb_template(wxr, word_entry, t_node, sense)


@dataclass
class TableHeader:
    text: str
    col_index: int
    colspan: int
    row_index: int
    rowspan: int


NLVERB_HEADER_PREFIXES = {
    "vervoeging van de bedrijvende vorm van": ["active"],
    "onpersoonlijke lijdende vorm": ["impersonal", "passive"],
    "lijdende vorm": ["passive"],
}


def extract_nlverb_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-nlverb-
    # Sjabloon:-nlverb-reflex-
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        row_index = 0
        shared_tags = []
        shared_raw_tags = []
        last_row_all_header = False
        col_headers = []
        row_headers = []
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for row_header in row_headers:
                if (
                    row_index >= row_header.row_index
                    and row_index < row_header.row_index + row_header.rowspan
                ):
                    col_index += row_header.rowspan

            current_row_all_header = all(
                nlverb_table_cell_is_header(n)
                for n in row_node.find_child(
                    NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
                )
            )
            if current_row_all_header and not last_row_all_header:
                row_index = 0
                shared_tags.clear()
                shared_raw_tags.clear()
                col_headers.clear()
                row_headers.clear()

            small_tag = ""
            is_row_first_node = True
            for cell_node in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_colspan = 1
                cell_colspan_str = cell_node.attrs.get("colspan", "1")
                if re.fullmatch(r"\d+", cell_colspan_str):
                    cell_colspan = int(cell_colspan_str)
                cell_rowspan = 1
                cell_rowspan_str = cell_node.attrs.get("rowspan", "1")
                if re.fullmatch(r"\d+", cell_rowspan_str):
                    cell_rowspan = int(cell_rowspan_str)
                cell_str = clean_node(wxr, None, cell_node).strip("| ")
                if cell_str in ["", "—", wxr.wtp.title]:
                    col_index += cell_colspan
                    is_row_first_node = False
                    continue
                if nlverb_table_cell_is_header(cell_node):
                    for (
                        header_prefix,
                        prefix_tags,
                    ) in NLVERB_HEADER_PREFIXES.items():
                        if cell_str.startswith(header_prefix):
                            shared_tags.extend(prefix_tags)
                            break
                    else:
                        if cell_str.startswith("vervoeging van "):
                            pass
                        elif current_row_all_header:
                            if (
                                is_row_first_node
                                and t_node.template_name == "-nlverb-"
                            ):
                                shared_raw_tags.append(cell_str)
                            else:
                                col_headers.append(
                                    TableHeader(
                                        cell_str,
                                        col_index,
                                        cell_colspan,
                                        row_index,
                                        cell_rowspan,
                                    )
                                )
                        else:
                            if "(" in cell_str:
                                cell_str = cell_str[
                                    : cell_str.index("(")
                                ].strip()
                            row_headers.append(
                                TableHeader(
                                    cell_str,
                                    col_index,
                                    cell_colspan,
                                    row_index,
                                    cell_rowspan,
                                )
                            )
                else:  # data cell
                    has_small_tag = False
                    for small_node in cell_node.find_html("small"):
                        has_small_tag = True
                    if has_small_tag:
                        small_tag = cell_str
                        col_index += cell_colspan
                        continue
                    form_texts = [cell_str]
                    if "/ " in cell_str:  # "zweerde/ zwoor"
                        form_texts = cell_str.split("/")
                    elif "/" in cell_str and " " in cell_str:
                        # "zult/zal zweren" -> ["zult zweren", "zal zweren"]
                        space_index = cell_str.index(" ")
                        second_part = cell_str[space_index:]
                        form_texts = [
                            f_str + second_part
                            for f_str in cell_str[:space_index].split("/")
                        ]
                    for form_str in form_texts:
                        form_str = form_str.strip()
                        if len(form_str) == 0:
                            continue
                        form = Form(
                            form=form_str,
                            tags=shared_tags,
                            raw_tags=shared_raw_tags,
                            source=f"{wxr.wtp.title}/vervoeging",
                            sense=sense,
                        )
                        if small_tag != "":
                            form.raw_tags.append(small_tag)
                            small_tag = ""
                        for row_header in row_headers:
                            if (
                                row_index >= row_header.row_index
                                and row_index
                                < row_header.row_index + row_header.rowspan
                            ):
                                form.raw_tags.append(row_header.text)
                        for col_header in col_headers:
                            if (
                                col_index >= col_header.col_index
                                and col_index
                                < col_header.col_index + col_header.colspan
                            ):
                                form.raw_tags.append(col_header.text)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)

                col_index += cell_colspan
                is_row_first_node = False

            row_index += 1
            last_row_all_header = current_row_all_header


def nlverb_table_cell_is_header(node: WikiNode) -> bool:
    return (
        node.kind == NodeKind.TABLE_HEADER_CELL
        or node.attrs.get("class", "") == "infoboxrijhoofding"
    )


def extract_csadjc_comp_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-csadjc-comp-ý3-
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            for cell_node in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    row_header = clean_node(wxr, None, cell_node)
                elif cell_node.kind == NodeKind.TABLE_CELL:
                    form_text = clean_node(wxr, None, cell_node)
                    if form_text not in ["", wxr.wtp.title]:
                        form = Form(form=form_text)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                            translate_raw_tags(form)
                        word_entry.forms.append(form)
