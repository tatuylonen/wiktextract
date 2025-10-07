import re
from dataclasses import dataclass

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    HTMLNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_conjugation(
    wxr: WiktextractContext,
    entry: WordEntry,
    conj_page_title: str,
    select_tab: str = "1",
) -> None:
    """
    Find and extract conjugation page.

    https://fr.wiktionary.org/wiki/Conjugaison:français
    https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles/Français/Conjugaison
    https://fr.wiktionary.org/wiki/Aide:Conjugaisons
    """
    conj_page = wxr.wtp.get_page_body(
        conj_page_title, wxr.wtp.NAMESPACE_DATA["Conjugaison"]["id"]
    )
    if conj_page is None:
        return
    conj_root = wxr.wtp.parse(conj_page)
    for conj_template in conj_root.find_child(NodeKind.TEMPLATE):
        if conj_template.template_name.endswith("-intro"):
            continue
        if conj_template.template_name in ["ku-conj-trans", "ku-conj"]:
            extract_ku_conj_trans_template(
                wxr, entry, conj_template, conj_page_title
            )
        elif conj_template.template_name == "ko-conj":
            extract_ko_conj_template(wxr, entry, conj_template, conj_page_title)
        elif conj_template.template_name == "de-conj":
            extract_de_conj_template(wxr, entry, conj_template, conj_page_title)
        elif "-conj" in conj_template.template_name:
            process_conj_template(wxr, entry, conj_template, conj_page_title)
        elif conj_template.template_name == "Onglets conjugaison":
            process_onglets_conjugaison_template(
                wxr, entry, conj_template, conj_page_title, select_tab
            )
        elif conj_template.template_name.removeprefix(":").startswith(
            "Conjugaison:"
        ):
            extract_conjugation(
                wxr,
                entry,
                conj_template.template_name.removeprefix(":"),
                clean_node(
                    wxr, None, conj_template.template_parameters.get("sél", "2")
                ),
            )
        elif conj_template.template_name.startswith("ja-flx-adj"):
            process_ja_flx_adj_template(
                wxr, entry, conj_template, conj_page_title
            )
        elif conj_template.template_name.startswith("ja-"):
            process_ja_conj_template(wxr, entry, conj_template, conj_page_title)

    if conj_page_title.startswith("Conjugaison:kurde/"):
        for table in conj_root.find_child(NodeKind.TABLE):
            extract_ku_conj_trans_table_node(wxr, entry, table, conj_page_title)

    for link_node in conj_root.find_child(NodeKind.LINK):
        clean_node(wxr, None, link_node)


def process_onglets_conjugaison_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    node: TemplateNode,
    conj_page_title: str,
    select_tab: str,
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:Onglets_conjugaison
    # this template expands to two tabs of tables
    selected_tabs = []
    if select_tab != "1" or (
        select_tab == "1"
        and clean_node(wxr, None, node.template_parameters.get("onglet1", ""))
        == "Conjugaison active"
    ):
        # don't extract or only extract "Conjugaison pronominale" tab
        selected_tabs = [select_tab]
    else:
        selected_tabs = [str(i) for i in range(1, 7)]

    for tab_index in selected_tabs:
        arg_name = f"contenu{tab_index}"
        if arg_name not in node.template_parameters:
            break
        arg_value = node.template_parameters[arg_name]
        if (
            isinstance(arg_value, TemplateNode)
            and "-conj" in arg_value.template_name
        ):
            process_conj_template(wxr, entry, arg_value, conj_page_title)
        elif isinstance(arg_value, list):
            for arg_node in arg_value:
                if (
                    isinstance(arg_node, TemplateNode)
                    and "-conj" in arg_node.template_name
                ):
                    process_conj_template(wxr, entry, arg_node, conj_page_title)


def process_conj_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    template_node: TemplateNode,
    conj_page_title: str,
) -> None:
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_conjugaison_en_français
    # https://fr.wiktionary.org/wiki/Modèle:fr-conj-1-ger
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    process_expanded_conj_template(
        wxr, entry, expanded_template, conj_page_title
    )


def process_expanded_conj_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    node: WikiNode,
    conj_page_title: str,
) -> None:
    h3_text = (
        clean_node(wxr, None, node.largs)
        if node.kind == NodeKind.LEVEL3
        else ""
    )
    for child in node.find_child(NodeKind.HTML | LEVEL_KIND_FLAGS):
        if child.kind in LEVEL_KIND_FLAGS:
            process_expanded_conj_template(wxr, entry, child, conj_page_title)
        elif child.kind == NodeKind.HTML:
            if child.tag == "h3":
                h3_text = clean_node(wxr, None, child)
            elif child.tag == "div":
                if h3_text == "Modes impersonnels":
                    process_fr_conj_modes_table(
                        wxr, entry, child, conj_page_title
                    )
                else:
                    process_fr_conj_table(
                        wxr, entry, child, h3_text, conj_page_title
                    )


@dataclass
class TableHeader:
    text: str
    col_index: int = 0
    colspan: int = 0
    row_index: int = 0
    rowspan: int = 0


def process_fr_conj_modes_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    div_node: HTMLNode,
    conj_page_title: str,
) -> None:
    # the first "Modes impersonnels" table

    for table_node in div_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            is_header_row = not row.contain_node(NodeKind.TABLE_CELL)
            col_index = 0
            form_text = ""
            for node in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if node.kind == NodeKind.TABLE_HEADER_CELL or (
                    node.contain_node(NodeKind.BOLD) and col_index == 0
                ):
                    if is_header_row:
                        header_text = clean_node(wxr, None, node)
                        if header_text == "Mode":
                            continue
                        else:
                            colspan = 1
                            colspan_str = node.attrs.get("colspan", "1")
                            if re.fullmatch(r"\d+", colspan_str) is not None:
                                colspan = int(colspan_str)
                            col_headers.append(
                                TableHeader(header_text, col_index, colspan)
                            )
                            col_index += colspan
                    else:
                        row_header = clean_node(wxr, None, node)
                else:
                    node_text = clean_node(wxr, None, node)
                    if (
                        node_text.endswith(("]", "\\", "Prononciation ?"))
                        and form_text != ""
                    ):
                        form = Form(
                            form=form_text,
                            ipas=[node_text]
                            if node_text.endswith(("]", "\\"))
                            else [],
                            source=conj_page_title,
                        )
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        for col_header in col_headers:
                            if (
                                col_index >= col_header.col_index
                                and col_index
                                < col_header.col_index + col_header.colspan
                            ):
                                form.raw_tags.append(col_header.text)
                        translate_raw_tags(form)
                        entry.forms.append(form)
                        form_text = ""
                    elif node_text != "":
                        if not form_text.endswith("’") and form_text != "":
                            form_text += " "
                        form_text += node_text
                    col_index += 1


def process_fr_conj_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    div_node: HTMLNode,
    h3_text: str,
    conj_page_title: str,
) -> None:
    for table_node in div_node.find_child(NodeKind.TABLE):
        for row_index, row in enumerate(
            table_node.find_child(NodeKind.TABLE_ROW)
        ):
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                for cell_child in cell.children:
                    if isinstance(cell_child, WikiNode):
                        if (
                            cell_child.kind == NodeKind.HTML
                            and cell_child.tag == "table"
                        ):
                            process_fr_conj_html_table(
                                wxr, entry, cell_child, h3_text, conj_page_title
                            )
                        elif cell_child.kind == NodeKind.TABLE:
                            process_fr_conj_wiki_table(
                                wxr, entry, cell_child, h3_text, conj_page_title
                            )


def process_fr_conj_html_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    table_node: HTMLNode,
    h3_text: str,
    conj_page_title: str,
):
    tags = [h3_text] if h3_text != "" else []
    for tr_index, tr_node in enumerate(table_node.find_html_recursively("tr")):
        if tr_index == 0:
            tags.append(clean_node(wxr, None, tr_node.children))
        else:
            form = Form(raw_tags=tags, source=conj_page_title)
            for td_index, td_node in enumerate(
                tr_node.find_html_recursively("td")
            ):
                td_text = clean_node(wxr, None, td_node)
                if td_index < 2:
                    form.form += td_text
                    if td_index == 0 and not td_text.endswith("’"):
                        form.form += " "
                else:
                    if len(form.ipas) > 0:
                        form.ipas[0] += td_text
                    else:
                        if not td_text.endswith("‿"):
                            td_text += " "
                        form.ipas.append(td_text)

            translate_raw_tags(form)
            entry.forms.append(form)


def process_fr_conj_wiki_table(
    wxr: WiktextractContext,
    entry: WordEntry,
    table_node: WikiNode,
    h3_text: str,
    conj_page_title: str,
):
    tags = [h3_text] if h3_text != "" else []
    for row_index, row in enumerate(table_node.find_child(NodeKind.TABLE_ROW)):
        if row_index == 0:
            tags.append(clean_node(wxr, None, row.children))
        else:
            form = Form(raw_tags=tags, source=conj_page_title)
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_index < 2:
                    if cell_text == "—" or cell_text.endswith(
                        "Prononciation ?"
                    ):
                        continue
                    if cell_text.startswith(
                        "-"
                    ) and not form.form.strip().endswith(")"):
                        form.form = form.form.strip()
                    form.form += cell_text
                    if cell_index == 0 and len(cell_text) > 0:
                        form.form += " "
                elif not cell_text.endswith("Prononciation ?"):
                    form.ipas.append(cell_text)

            if len(form.form) > 0:
                translate_raw_tags(form)
                entry.forms.append(form)


def process_ja_flx_adj_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    template_node: TemplateNode,
    conj_page_title: str,
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:ja-adj
    # https://fr.wiktionary.org/wiki/Modèle:ja-flx-adj-な
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_node in expanded_template.find_child(NodeKind.TABLE):
        first_tag = ""
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            forms = []
            tags = [first_tag]
            for cell_index, row_child in enumerate(
                row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
            ):
                row_child_text = clean_node(wxr, None, row_child)
                if row_child.kind == NodeKind.TABLE_HEADER_CELL:
                    first_tag = row_child_text
                else:
                    for line_index, line in enumerate(
                        row_child_text.splitlines()
                    ):
                        if cell_index == 0:
                            tags.append(line)
                            continue
                        if line_index + 1 > len(forms):
                            forms.append(
                                translate_raw_tags(
                                    Form(raw_tags=tags, source=conj_page_title)
                                )
                            )
                        if cell_index == 1:
                            forms[line_index].form = line
                        elif cell_index == 2:
                            forms[line_index].hiragana = line
                        elif cell_index == 3:
                            forms[line_index].roman = line

            entry.forms.extend(forms)


def process_ja_conj_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    template_node: TemplateNode,
    conj_page_title: str,
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:ja-verbe-conj
    # Modèle:ja-在る
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_node in expanded_template.find_child(NodeKind.TABLE):
        first_tag = ""
        row_headers = {}
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            if (
                all(
                    isinstance(c, WikiNode)
                    and c.kind == NodeKind.TABLE_HEADER_CELL
                    for c in row.children
                )
                and len(row.children) > 1
            ):
                # skip header row of the "Clefs de constructions" table
                continue

            for header in row.find_child(NodeKind.TABLE_HEADER_CELL):
                header_text = clean_node(wxr, None, header)
                if len(row.children) == 1:
                    first_tag = header_text
                else:
                    row_headers[header_text] = int(
                        header.attrs.get("rowspan", "1")
                    )

            tags = [first_tag]
            for tag, rowspan in row_headers.copy().items():
                tags.append(tag)
                if rowspan == 1:
                    del row_headers[tag]
                else:
                    row_headers[tag] = rowspan - 1
            form = Form(raw_tags=tags, source=conj_page_title)
            for cell_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_index == 0:
                    form.form = cell_text
                elif cell_index == 1:
                    form.hiragana = cell_text
                elif cell_index == 2:
                    form.roman = cell_text
            if len(form.form) > 0:
                translate_raw_tags(form)
                entry.forms.append(form)


def extract_ku_conj_trans_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    t_node: TemplateNode,
    conj_page_title: str,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        extract_ku_conj_trans_table_node(wxr, entry, table, conj_page_title)
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, entry, link_node)


def extract_ku_conj_trans_table_node(
    wxr: WiktextractContext,
    entry: WordEntry,
    table_node: WikiNode,
    conj_page_title: str,
) -> None:
    @dataclass
    class TableHeader:
        text: str
        index: int
        span: int

    ignore_headers = (
        "Conjugaison du verbe",
        "TEMPS DU PRÉSENT ET DU FUTUR",
        "TEMPS DU PRESENT ET DU FUTUR",
        "TEMPS DU PASSÉ",
        "TEMPS DU PASSE",
    )
    col_headers = []
    last_row_has_header = False
    last_header = ""
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        col_index = 0
        current_row_has_header = row.contain_node(NodeKind.TABLE_HEADER_CELL)
        if not last_row_has_header and current_row_has_header:
            col_headers.clear()
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_str = clean_node(wxr, None, cell)
            if cell_str == "":
                col_index += 1
                continue
            if cell.kind == NodeKind.TABLE_HEADER_CELL:
                if cell_str.startswith(ignore_headers):
                    last_header = cell_str
                    continue
                colspan = 1
                colspan_str = cell.attrs.get("colspan", "1")
                if re.fullmatch(r"\d+", colspan_str) is not None:
                    colspan = int(colspan_str)
                col_headers.append(
                    TableHeader(text=cell_str, index=col_index, span=colspan)
                )
                last_header = cell_str
                col_index += colspan
            elif last_header == "TEMPS DU PASSÉ":
                continue
            elif cell_str == "(inusité)":
                col_index += 1
            elif cell_str != wxr.wtp.title:
                form = Form(form=cell_str, source=conj_page_title)
                for header in col_headers:
                    if (
                        col_index >= header.index
                        and col_index < header.index + header.span
                    ):
                        form.raw_tags.append(header.text)
                translate_raw_tags(form)
                entry.forms.append(form)
                col_index += 1
        last_row_has_header = current_row_has_header


def extract_ko_conj_template(
    wxr: WiktextractContext,
    entry: WordEntry,
    t_node: TemplateNode,
    conj_page_title: str,
) -> None:
    word_page_title = wxr.wtp.title
    wxr.wtp.title = conj_page_title
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for h3 in expanded_node.find_html("h3"):
        clean_node(wxr, entry, h3)
    for table_index, table in enumerate(
        expanded_node.find_child(NodeKind.TABLE)
    ):
        if table_index == 0:
            continue
        shared_raw_tags = []
        for caption_node in table.find_child(NodeKind.TABLE_CAPTION):
            caption = clean_node(wxr, None, caption_node.children)
            if caption != "":
                shared_raw_tags.append(caption)
        col_headers = []
        row_headers = []
        row_index = 0
        row_header_indexes = [0]
        for row in table.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for header_cell in row.find_child(NodeKind.TABLE_HEADER_CELL):
                cell_str = clean_node(wxr, None, header_cell)
                if cell_str == "":
                    continue
                colspan, rowspan = get_cell_span(header_cell)
                if row.contain_node(NodeKind.TABLE_CELL):
                    header_added = False
                    current_row_index = row_index
                    for index, row_header_index in enumerate(
                        row_header_indexes
                    ):
                        if row_index >= row_header_index:
                            current_row_index = row_header_indexes[index]
                            row_header_indexes[index] += rowspan
                        header_added = True
                        break
                    if not header_added:
                        row_header_indexes.append(rowspan)
                    row_headers.append(
                        TableHeader(
                            text=cell_str,
                            row_index=current_row_index,
                            rowspan=rowspan,
                        )
                    )
                else:
                    col_headers.append(
                        TableHeader(
                            text=cell_str,
                            col_index=col_index,
                            colspan=colspan,
                        )
                    )
                col_index += colspan
            if row.contain_node(NodeKind.TABLE_CELL):
                row_index += 1

        row_index = 0
        for row in table.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for cell in row.find_child(NodeKind.TABLE_CELL):
                cell_str = clean_node(wxr, None, cell)
                colspan, rowspan = get_cell_span(cell)
                if cell_str == "—":
                    col_index += 1
                else:
                    form = Form(
                        source=conj_page_title, raw_tags=shared_raw_tags
                    )
                    for line_index, line in enumerate(cell_str.splitlines()):
                        match line_index:
                            case 0:
                                form.form = line
                            case 1:
                                form.roman = line
                            case 2:
                                form.ipas.append(line)
                    for header in col_headers:
                        if (
                            col_index >= header.col_index
                            and col_index < header.col_index + header.colspan
                        ):
                            form.raw_tags.append(header.text)
                    for header in row_headers:
                        if (
                            row_index < header.row_index + header.rowspan
                            and row_index + rowspan > header.row_index
                        ):
                            form.raw_tags.append(header.text)
                    if form.form not in ["", wxr.wtp.title]:
                        translate_raw_tags(form)
                        entry.forms.append(form)
                    col_index += 1
            if row.contain_node(NodeKind.TABLE_CELL):
                row_index += 1

    for link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, entry, link)
    wxr.wtp.title = word_page_title


def get_cell_span(cell: WikiNode) -> tuple[int, int]:
    colspan = 1
    colspan_str = cell.attrs.get("colspan", "1")
    if re.fullmatch(r"\d+", colspan_str) is not None:
        colspan = int(colspan_str)
    rowspan = 1
    rowspan_str = cell.attrs.get("rowspan", "1")
    if re.fullmatch(r"\d+", rowspan_str) is not None:
        rowspan = int(rowspan_str)
    return colspan, rowspan


def extract_de_conj_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    conj_page_title: str,
):
    word_page_title = wxr.wtp.title
    wxr.wtp.title = conj_page_title
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    wxr.wtp.title = word_page_title
    for table_index, table in enumerate(
        expanded_node.find_child(NodeKind.TABLE)
    ):
        table_header = ""
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            word_part = ""
            col_index = 0
            if table_index >= 2 and row.contain_node(
                NodeKind.TABLE_HEADER_CELL
            ):
                col_headers.clear()
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_text == "":
                    continue
                elif cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if len(row.children) == 1:
                        table_header = clean_node(wxr, None, cell)
                    else:
                        col_headers.append(clean_node(wxr, None, cell))
                elif table_index < 2:
                    form = Form(form=cell_text, source=conj_page_title)
                    if ":" in cell_text:
                        colon_index = cell_text.index(":")
                        raw_tag = cell_text[:colon_index].strip()
                        if raw_tag != "":
                            form.raw_tags.append(raw_tag)
                        form.form = cell_text[colon_index + 1 :].strip()
                    if table_header != "":
                        form.raw_tags.append(table_header)
                    if col_index < len(col_headers):
                        form.raw_tags.append(col_headers[col_index])
                    if form.form not in ["", wxr.wtp.title]:
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                elif col_index % 2 == 0:
                    word_part = cell_text
                else:
                    form = Form(
                        form=f"{word_part} {cell_text}", source=conj_page_title
                    )
                    if table_header != "":
                        form.raw_tags.append(table_header)
                    if col_index // 2 < len(col_headers):
                        form.raw_tags.append(col_headers[col_index // 2])
                    if form.form not in ["", wxr.wtp.title]:
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                col_index += 1

    for cat_link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, cat_link)
