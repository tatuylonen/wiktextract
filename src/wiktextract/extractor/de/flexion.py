from dataclasses import dataclass

from wikitextprocessor import NodeKind
from wikitextprocessor.parser import HTMLNode, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def parse_flexion_page(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    # https://de.wiktionary.org/wiki/Hilfe:Flexionsseiten
    flexion_page = wxr.wtp.get_page_body(
        page_title, wxr.wtp.NAMESPACE_DATA["Flexion"]["id"]
    )
    if flexion_page is None:
        return
    flexion_root = wxr.wtp.parse(flexion_page)
    for flexion_template in flexion_root.find_child_recursively(
        NodeKind.TEMPLATE
    ):
        if flexion_template.template_name.startswith("Deklinationsseite"):
            process_deklinationsseite_template(
                wxr, word_entry, flexion_template, page_title
            )
        elif flexion_template.template_name.startswith("Deutsch Verb"):
            process_deutsch_verb_template(
                wxr, word_entry, flexion_template, page_title
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
) -> None:
    # Vorlage:Deutsch Verb regelmäßig
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table in expanded_template.find_child_recursively(NodeKind.TABLE):
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
                elif (
                    cell.kind == NodeKind.TABLE_HEADER_CELL
                    and cell_text not in ("", "Person")
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
                    elif cell.contain_node(NodeKind.BOLD) or (
                        len(list(cell.find_html("small"))) > 0
                        and len(list(cell.filter_empty_str_child())) == 1
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
                                form_raw_tag, form_text = form_text.split(
                                    ":", 1
                                )
                            form = Form(
                                form=form_text.strip(), source=page_tite
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
