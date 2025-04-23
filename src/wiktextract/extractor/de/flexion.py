from dataclasses import dataclass

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import GRAMMATICAL_TAGS, translate_raw_tags


def parse_flexion_page(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    # https://de.wiktionary.org/wiki/Hilfe:Flexionsseiten
    LEVEL2_TAGS = ["Hilfsverb haben", "Hilfsverb sein"]

    flexion_page = wxr.wtp.get_page_body(
        page_title, wxr.wtp.NAMESPACE_DATA["Flexion"]["id"]
    )
    if flexion_page is None:
        return
    flexion_root = wxr.wtp.parse(flexion_page)
    shared_raw_tags = []
    for node in flexion_root.find_child_recursively(
        NodeKind.TEMPLATE | NodeKind.LEVEL2
    ):
        match node.kind:
            case NodeKind.LEVEL2:
                shared_raw_tags.clear()
                section_str = clean_node(wxr, None, node.largs)
                for word in section_str.split(" "):
                    word = word.strip(", ")
                    if word in GRAMMATICAL_TAGS and not page_title.endswith(
                        f":{word}"
                    ):
                        shared_raw_tags.append(word)
                for raw_tag in LEVEL2_TAGS:
                    if raw_tag in section_str:
                        shared_raw_tags.append(raw_tag)
            case NodeKind.TEMPLATE:
                if node.template_name == "Deklinationsseite Numerale":
                    extract_deklinationsseite_numerale_template(
                        wxr, word_entry, node, page_title
                    )
                elif node.template_name.startswith("Deklinationsseite"):
                    process_deklinationsseite_template(
                        wxr, word_entry, node, page_title
                    )
                elif node.template_name.startswith("Deutsch Verb"):
                    process_deutsch_verb_template(
                        wxr, word_entry, node, page_title, shared_raw_tags
                    )


@dataclass
class SpanHeader:
    text: str
    index: int
    span: int


def process_deklinationsseite_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
    page_tite: str,
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Deklinationsseite_Adjektiv
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    h4_text = ""
    for node in expanded_template.find_child(NodeKind.HTML | NodeKind.TABLE):
        if isinstance(node, HTMLNode) and node.tag == "h4":
            h4_text = clean_node(wxr, None, node)
        elif node.kind == NodeKind.TABLE:
            col_headers = []
            has_article = False
            for row_node in node.find_child(NodeKind.TABLE_ROW):
                col_index = 0
                row_header = ""
                article = ""
                for cell_node in row_node.find_child(
                    NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
                ):
                    cell_text = clean_node(wxr, None, cell_node)
                    if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                        if cell_text == "":
                            continue
                        elif cell_text in ("Artikel", "Wortform"):
                            has_article = True
                            continue
                        elif "colspan" in cell_node.attrs:
                            col_span = int(cell_node.attrs.get("colspan"))
                            if col_span == 9:  # new table
                                has_article = False
                                col_headers.clear()
                            col_headers.append(
                                SpanHeader(cell_text, col_index, col_span)
                            )
                            col_index += col_span
                        else:
                            row_header = cell_text
                    elif cell_node.kind == NodeKind.TABLE_CELL:
                        if has_article and col_index % 2 == 0:
                            article = cell_text
                        else:
                            form_text = ""
                            if article not in ("", "—"):
                                form_text = article + " "
                            form_text += cell_text
                            form = Form(form=form_text, source=page_tite)
                            if h4_text != "":
                                form.raw_tags.append(h4_text)
                            if row_header != "":
                                form.raw_tags.append(row_header)
                            for col_header in col_headers:
                                if (
                                    col_header.text not in ("", "—")
                                    and col_index >= col_header.index
                                    and col_index
                                    < col_header.index + col_header.span
                                ):
                                    form.raw_tags.append(col_header.text)
                            if form.form not in ("", "—"):
                                translate_raw_tags(form)
                                word_entry.forms.append(form)
                        col_index += int(cell_node.attrs.get("colspan", "1"))


def process_deutsch_verb_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
    page_tite: str,
    shared_raw_tags: list[str],
) -> None:
    # Vorlage:Deutsch Verb regelmäßig
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for level_node in expanded_template.find_child(LEVEL_KIND_FLAGS):
        process_deutsch_verb_section(
            wxr, word_entry, level_node, page_tite, shared_raw_tags
        )


def process_deutsch_verb_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    page_tite: str,
    shared_raw_tags: list[str],
) -> None:
    section_title = clean_node(wxr, None, level_node.largs)
    new_raw_tags = shared_raw_tags.copy()
    new_raw_tags.append(section_title)
    for table_node in level_node.find_child(NodeKind.TABLE):
        process_deutsch_verb_table(
            wxr, word_entry, table_node, page_tite, new_raw_tags
        )
    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        process_deutsch_verb_section(
            wxr, word_entry, next_level, page_tite, new_raw_tags
        )


def process_deutsch_verb_table(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    table: WikiNode,
    page_tite: str,
    shared_raw_tags: list[str],
) -> None:
    col_headers = []
    for row in table.find_child(NodeKind.TABLE_ROW):
        row_header = ""
        col_index = 0
        col_header_index = 0
        is_bold_col_header = all(
            c.contain_node(NodeKind.BOLD)
            for c in row.find_child(NodeKind.TABLE_CELL)
            if clean_node(wxr, None, c) != ""
        )
        if (
            len(
                list(
                    row.find_child(
                        NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
                    )
                )
            )
            == 1
        ):
            col_headers.clear()  # new table
        for cell in row.find_child(
            NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
        ):
            cell_text = clean_node(wxr, None, cell)
            if cell_text in (
                "Flexion der Verbaladjektive",
                "(nichterweiterte) Infinitive",
            ):
                break
            elif cell.kind == NodeKind.TABLE_HEADER_CELL and cell_text not in (
                "",
                "Person",
            ):
                colspan = int(cell.attrs.get("colspan", "1"))
                col_headers.append(
                    SpanHeader(
                        cell_text,
                        col_header_index,
                        colspan,
                    )
                )
                col_header_index += colspan
            elif cell.kind == NodeKind.TABLE_CELL:
                if cell_text in (
                    "",
                    "—",
                    "Text",
                    "Person",
                ) or cell_text.startswith("Flexion:"):
                    col_index += 1
                elif (
                    cell.contain_node(NodeKind.BOLD)
                    or (
                        len(list(cell.find_html("small"))) > 0
                        and len(list(cell.filter_empty_str_child())) == 1
                    )
                    # Vorlage:Deutsch Verb schwach untrennbar reflexiv
                    or cell.attrs.get("bgcolor", "").lower() == "#f4f4f4"
                ):  # header in cell
                    colspan = int(cell.attrs.get("colspan", "1"))
                    if is_bold_col_header:
                        for bold_node in cell.find_child(NodeKind.BOLD):
                            col_headers.append(
                                SpanHeader(
                                    clean_node(wxr, None, bold_node),
                                    col_header_index,
                                    colspan,
                                )
                            )
                    else:
                        row_header = cell_text
                    col_header_index += colspan
                else:
                    for form_text in cell_text.splitlines():
                        form_text = form_text.strip(", ")
                        form_raw_tag = ""
                        if ":" in form_text:
                            form_raw_tag, form_text = form_text.split(":", 1)
                        form = Form(
                            form=form_text.strip(),
                            source=page_tite,
                            raw_tags=shared_raw_tags,
                        )
                        if form_raw_tag != "":
                            form.raw_tags.append(form_raw_tag)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        for col_header in col_headers:
                            if (
                                col_index >= col_header.index
                                and col_index
                                < col_header.index + col_header.span
                            ):
                                if col_header.text.endswith("I"):
                                    form.raw_tags.append(col_header.text)
                                else:
                                    for raw_tag in col_header.text.split():
                                        form.raw_tags.append(raw_tag)
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                    col_index += 1


def extract_deklinationsseite_numerale_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    page_tite: str,
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Deklinationsseite_Numerale
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_template.find_child(NodeKind.TABLE):
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            row_has_data = row.contain_node(NodeKind.TABLE_CELL)
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_text == "":
                    continue
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if row_has_data:
                        row_header = cell_text
                    else:
                        col_span = int(cell.attrs.get("colspan", "1"))
                        if col_index == 0 and not row_has_data:
                            col_headers.clear()  # new table
                        col_headers.append(
                            SpanHeader(cell_text, col_index, col_span)
                        )
                        col_index += col_span
                else:
                    word_nodes = []
                    raw_tags = []
                    for cell_child in cell.children:
                        if (
                            isinstance(cell_child, HTMLNode)
                            and cell_child.tag == "br"
                        ):
                            word = clean_node(wxr, None, word_nodes)
                            if word != "":
                                deklinationsseite_numerale_add_form(
                                    word_entry,
                                    word,
                                    page_tite,
                                    raw_tags,
                                    col_index,
                                    row_header,
                                    col_headers,
                                )
                                word_nodes.clear()
                        elif (
                            isinstance(cell_child, WikiNode)
                            and cell_child.kind == NodeKind.ITALIC
                        ):
                            raw_tag = clean_node(wxr, None, cell_child).strip(
                                ": "
                            )
                            if raw_tag != "":
                                raw_tags.append(raw_tag)
                        else:
                            word_nodes.append(cell_child)
                    word = clean_node(wxr, None, word_nodes)
                    if word != "":
                        deklinationsseite_numerale_add_form(
                            word_entry,
                            word,
                            page_tite,
                            raw_tags,
                            col_index,
                            row_header,
                            col_headers,
                        )
                    col_index += 1


def deklinationsseite_numerale_add_form(
    word_entry: WordEntry,
    word: str,
    source: str,
    raw_tags: list[str],
    index: int,
    row_header: str,
    col_headers: list[SpanHeader],
) -> None:
    form = Form(
        form=word,
        source=source,
        raw_tags=raw_tags,
    )
    if row_header != "":
        form.raw_tags.append(row_header)
    for col_header in col_headers:
        if (
            index >= col_header.index
            and index < col_header.index + col_header.span
        ):
            form.raw_tags.append(col_header.text)
    translate_raw_tags(form)
    word_entry.forms.append(form)
