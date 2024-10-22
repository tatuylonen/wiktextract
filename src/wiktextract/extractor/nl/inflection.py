from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_inflection_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    if t_node.template_name == "-nlnoun-":
        extract_nlnoun_template(wxr, word_entry, t_node)


def extract_nlnoun_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-nlnoun-
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
                    form_str = clean_node(wxr, None, data_node)
                    if form_str not in ["", wxr.wtp.title]:
                        form = Form(form=form_str)
                        if row_header not in ["", "naamwoord"]:
                            form.raw_tags.append(row_header)
                        if col_index - 1 < len(column_headers):
                            form.raw_tags.append(column_headers[col_index - 1])
                        translate_raw_tags(form)
                        word_entry.forms.append(form)

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)
