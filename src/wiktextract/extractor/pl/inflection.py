import re

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_inflection_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    lang_code: str,
    level_node: WikiNode,
) -> None:
    from .page import match_sense_index

    sense_index = ""
    forms = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\([\d\s,-.]+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
            elif isinstance(node, TemplateNode):
                if node.template_name == "odmiana-rzeczownik-polski":
                    forms.extend(
                        extract_odmiana_rzeczownik_polski(
                            wxr, node, sense_index
                        )
                    )

    for data in page_data:
        if data.lang_code == lang_code:
            for form in forms:
                if match_sense_index(form.sense_index, data):
                    data.forms.append(form)


def extract_odmiana_rzeczownik_polski(
    wxr: WiktextractContext, template_node: TemplateNode, sense_index: str
) -> list[Form]:
    # noun table
    # https://pl.wiktionary.org/wiki/Szablon:odmiana-rzeczownik-polski
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    forms = []
    for table_tag in expanded_node.find_html_recursively("table"):
        col_headers = []
        for tr_tag in table_tag.find_html("tr"):
            for th_tag in tr_tag.find_html("th"):
                th_text = clean_node(wxr, None, th_tag)
                if th_text != "przypadek":
                    col_headers.append(th_text)
            col_index = 0
            row_header = ""
            for td_tag in tr_tag.find_html("td"):
                td_text = clean_node(wxr, None, td_tag)
                if "forma" == td_tag.attrs.get("class", ""):
                    row_header = td_text
                else:
                    for form_text in td_text.split("/"):
                        form_text = form_text.strip()
                        if form_text != "" and form_text != wxr.wtp.title:
                            form = Form(form=form_text, sense_index=sense_index)
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            if len(row_header) > 0:
                                form.raw_tags.append(row_header)
                            forms.append(form)
                    col_index += 1
    return forms
