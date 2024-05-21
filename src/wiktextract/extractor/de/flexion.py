from dataclasses import dataclass

from wikitextprocessor import NodeKind
from wikitextprocessor.parser import HTMLNode, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def parse_adj_flexion_page(
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


@dataclass
class ColspanHeader:
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
                                ColspanHeader(cell_text, col_index, col_span)
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
