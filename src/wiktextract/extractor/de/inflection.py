import re
from dataclasses import dataclass

from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .flexion import parse_flexion_page
from .models import Form, WordEntry
from .tags import translate_raw_tags

# Kategorie:Wiktionary:Flexionstabelle (Deutsch)


def extract_inf_table_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    if (
        "Substantiv Übersicht" in t_node.template_name
        or t_node.template_name.endswith(
            (
                "Nachname Übersicht",
                "Eigenname Übersicht",
                "Vorname Übersicht m",
                "Name Übersicht",
                "Pronomina-Tabelle",
                "Pronomen Übersicht",
                "adjektivisch Übersicht",
                "Substantiv Dialekt",
                "Toponym Übersicht",
            )
        )
        or re.search(r" Personalpronomen \d$", t_node.template_name)
    ):
        process_noun_table(wxr, word_entry, t_node)
    elif t_node.template_name.endswith(
        ("Adjektiv Übersicht", "Adverb Übersicht")
    ):
        process_adj_table(wxr, word_entry, t_node)
    elif (
        t_node.template_name.endswith("Verb Übersicht")
        or t_node.template_name == "Kardinalzahl 2-12"
    ):
        process_verb_table(wxr, word_entry, t_node)
    elif t_node.template_name == "Deutsch Possessivpronomen":
        extract_pronoun_table(wxr, word_entry, t_node)


@dataclass
class RowspanHeader:
    text: str
    index: int
    span: int


def process_verb_table(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # Vorlage:Deutsch Verb Übersicht
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    has_person = False
    row_headers = []
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        col_index = 0
        header_col_index = 0
        person = ""
        for table_cell in table_row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, table_cell)
            if cell_text.startswith("All other forms:"):
                for link_node in table_cell.find_child_recursively(
                    NodeKind.LINK
                ):
                    link_text = clean_node(wxr, None, link_node)
                    if link_text.startswith("Flexion:"):
                        parse_flexion_page(wxr, word_entry, link_text)
            elif table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                if cell_text == "":
                    continue
                elif header_col_index == 0:
                    rowspan = int(table_cell.attrs.get("rowspan", "1"))
                    row_headers.append(RowspanHeader(cell_text, 0, rowspan))
                elif cell_text in ("Person", "Wortform"):
                    has_person = True
                else:  # new table
                    col_headers.append(cell_text)
                    has_person = False
                    person = ""
                header_col_index += 1
            elif table_cell.kind == NodeKind.TABLE_CELL:
                if has_person and col_index == 0:
                    if cell_text in ("Singular", "Plural"):
                        row_headers.append(RowspanHeader(cell_text, 0, 1))
                    else:
                        person = cell_text
                else:
                    for cell_line in cell_text.splitlines():
                        cell_line = cell_line.strip()
                        if cell_line in ["", "—"]:
                            continue
                        elif cell_line.startswith("Flexion:"):
                            parse_flexion_page(wxr, word_entry, cell_line)
                            continue
                        for p in person.split(","):
                            p = p.strip()
                            form_text = cell_line
                            if p != "":
                                form_text = p + " " + cell_line
                            if form_text == wxr.wtp.title:
                                continue
                            form = Form(form=form_text)
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            for row_header in row_headers:
                                form.raw_tags.append(row_header.text)
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                col_index += 1

        new_row_headers = []
        for row_header in row_headers:
            if row_header.span > 1:
                row_header.span -= 1
                new_row_headers.append(row_header)
        row_headers = new_row_headers


def process_noun_table(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # Vorlage:Deutsch Substantiv Übersicht
    from .page import extract_note_section

    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    table_header = ""
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        is_header_row = not table_row.contain_node(NodeKind.TABLE_CELL)
        row_has_header = table_row.contain_node(NodeKind.TABLE_HEADER_CELL)
        col_index = 0
        for table_cell in table_row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, table_cell)
            if cell_text == "":
                continue
            if table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                if cell_text in ["Kasus", "Utrum"]:
                    continue
                elif is_header_row:
                    colspan = int(table_cell.attrs.get("colspan", "1"))
                    column_headers.append(
                        RowspanHeader(
                            re.sub(r"\s*\d+$", "", cell_text),
                            col_index,
                            colspan,
                        )
                    )
                    col_index += colspan
                else:
                    row_header = cell_text
            elif not row_has_header:
                # Vorlage:Deutsch adjektivisch Übersicht
                table_header = cell_text
                column_headers.clear()
            else:
                for form_text in cell_text.splitlines():
                    form_text = form_text.strip()
                    if form_text.startswith("(") and form_text.endswith(")"):
                        form_text = form_text.strip("() ")
                    if form_text in ["—", "–", "", "?", wxr.wtp.title]:
                        continue
                    form = Form(form=form_text)
                    if table_header != "":
                        form.raw_tags.append(table_header)
                    if len(row_header) > 0:
                        form.raw_tags.append(row_header)
                    for col_header in column_headers:
                        if (
                            col_header.text not in ("", "—")
                            and col_index >= col_header.index
                            and col_index < col_header.index + col_header.span
                        ):
                            form.raw_tags.append(col_header.text)
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
                col_index += 1

    clean_node(wxr, word_entry, expanded_template)  # category links
    # Vorlage:Deutsch Nachname Übersicht
    for level_node in expanded_template.find_child(NodeKind.LEVEL4):
        section_text = clean_node(wxr, None, level_node.largs)
        if section_text.startswith("Anmerkung"):
            extract_note_section(wxr, word_entry, level_node)


def process_adj_table(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # Vorlage:Deutsch Adjektiv Übersicht
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    for table_row in table_node.find_child(NodeKind.TABLE_ROW):
        for col_index, table_cell in enumerate(
            table_row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            )
        ):
            cell_text = clean_node(wxr, None, table_cell)
            # because {{int:}} magic word is not implemented
            # template "Textbaustein-Intl" expands to English words
            if cell_text.startswith("All other forms:"):
                for link_node in table_cell.find_child(NodeKind.LINK):
                    parse_flexion_page(
                        wxr, word_entry, clean_node(wxr, None, link_node)
                    )
            elif table_cell.kind == NodeKind.TABLE_HEADER_CELL:
                column_headers.append(cell_text)
            else:
                for form_text in cell_text.splitlines():
                    if form_text in ("—", "", "?"):
                        continue
                    form = Form(form=form_text)
                    if col_index < len(column_headers):
                        form.raw_tags.append(column_headers[col_index])
                    translate_raw_tags(form)
                    word_entry.forms.append(form)


def extract_pronoun_table(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # Vorlage:Deutsch Possessivpronomen
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    table_nodes = list(expanded_template.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    col_headers = []
    table_header = ""
    for row in table_node.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        row_has_data = row.contain_node(NodeKind.TABLE_CELL)
        col_index = 0
        article = ""
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, cell)
            if cell.kind == NodeKind.TABLE_HEADER_CELL:
                if cell_text == "":
                    continue
                elif row_has_data:
                    row_header = cell_text
                elif len(list(row.find_child(NodeKind.TABLE_HEADER_CELL))) == 1:
                    table_header = cell_text
                    col_headers.clear()  # new table
                    article = ""
                else:
                    colspan = 1
                    colspan_str = cell.attrs.get("colspan", "1")
                    if re.fullmatch(r"\d+", colspan_str):
                        colspan = int(colspan_str)
                    if cell_text != "—":
                        col_headers.append(
                            RowspanHeader(cell_text, col_index, colspan)
                        )
                    col_index += colspan
            elif cell.kind == NodeKind.TABLE_CELL:
                if col_index % 2 == 0:
                    article = cell_text
                else:
                    form_str = (
                        article + " " + cell_text
                        if article not in ["", "—"]
                        else cell_text
                    )
                    form = Form(form=form_str)
                    if table_header != "":
                        form.raw_tags.append(table_header)
                    if row_header != "":
                        form.raw_tags.append(row_header)
                    for header in col_headers:
                        if (
                            col_index >= header.index
                            and col_index < header.index + header.span
                            and header.text != "Wortform"
                        ):
                            form.raw_tags.append(header.text)
                    translate_raw_tags(form)
                    if form.form != wxr.wtp.title:
                        word_entry.forms.append(form)
                    article = ""
                col_index += 1
