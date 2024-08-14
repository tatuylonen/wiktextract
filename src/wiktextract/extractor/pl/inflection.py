import re
from dataclasses import dataclass

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


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
                elif node.template_name == "odmiana-przymiotnik-polski":
                    forms.extend(
                        extract_odmiana_przymiotnik_polski(
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
                            translate_raw_tags(form)
                            forms.append(form)
                    col_index += 1
    return forms


@dataclass
class TableHeader:
    text: str
    start: int
    end: int


def extract_odmiana_przymiotnik_polski(
    wxr: WiktextractContext, template_node: TemplateNode, sense_index: str
) -> list[Form]:
    # adj table
    # https://pl.wiktionary.org/wiki/Szablon:odmiana-przymiotnik-polski
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    forms = []
    for table_tag in expanded_node.find_html_recursively("table"):
        forms.extend(
            extract_odmiana_przymiotnik_polski_table(
                wxr, table_tag, sense_index
            )
        )
    return forms


def extract_odmiana_przymiotnik_polski_table(
    wxr: WiktextractContext, table_tag: WikiNode, sense_index: str
) -> list[Form]:
    forms = []
    col_headers = []
    for tr_tag in table_tag.find_html("tr"):
        th_col_index = 0
        for th_tag in tr_tag.find_html("th"):
            if th_tag.contain_node(NodeKind.BOLD):
                # comparative forms in the second and third table header
                raw_tag_nodes = []
                for th_child in th_tag.children:
                    if (
                        isinstance(th_child, WikiNode)
                        and th_child.kind == NodeKind.BOLD
                    ):
                        form = Form(
                            form=clean_node(wxr, None, th_child),
                            raw_tags=[clean_node(wxr, None, raw_tag_nodes)],
                            sense_index=sense_index,
                        )
                        translate_raw_tags(form)
                        forms.append(form)
                    else:
                        raw_tag_nodes.append(th_child)
            else:
                th_text = clean_node(wxr, None, th_tag)
                col_span = int(th_tag.attrs.get("colspan", "1"))
                if th_text != "przypadek":
                    col_headers.append(
                        TableHeader(
                            th_text,
                            th_col_index,
                            th_col_index + col_span,
                        )
                    )
                    th_col_index += col_span

        # td tags
        th_col_index = 0
        td_col_index = 0
        row_header = ""
        all_header_row = all(
            td_tag.attrs.get("class", "") == "forma"
            for td_tag in tr_tag.find_html("td")
        )
        for td_tag in tr_tag.find_html("td"):
            if any(td_tag.find_html("table")):
                break
            td_text = clean_node(wxr, None, td_tag)
            if all_header_row:
                col_headers.append(
                    TableHeader(td_text, th_col_index, th_col_index + 1)
                )
                th_col_index += 1
            elif "forma" == td_tag.attrs.get("class", ""):
                row_header = td_text
            else:
                col_span = int(td_tag.attrs.get("colspan", "1"))
                if td_text == wxr.wtp.title:
                    td_col_index += col_span
                    continue
                form = Form(form=td_text, sense_index=sense_index)
                if row_header != "":
                    form.raw_tags.append(row_header)
                for col_header in col_headers:
                    if (
                        col_header.start < td_col_index + col_span
                        and td_col_index < col_header.end
                    ):
                        form.raw_tags.append(col_header.text)
                td_col_index += col_span
                translate_raw_tags(form)
                forms.append(form)
    return forms
