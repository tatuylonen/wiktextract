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
                forms.extend(
                    extract_inflection_template(wxr, node, sense_index)
                )
    if not level_node.contain_node(NodeKind.LIST):
        # have to search recursively cuz "preformatted" node
        for node in level_node.find_child_recursively(NodeKind.TEMPLATE):
            forms.extend(extract_inflection_template(wxr, node, sense_index))

    for data in page_data:
        if data.lang_code == lang_code:
            for form in forms:
                if form.sense_index == "" or match_sense_index(
                    form.sense_index, data
                ):
                    data.forms.append(form)


def extract_inflection_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense_index: str
) -> list[Form]:
    if template_node.template_name == "odmiana-rzeczownik-polski":
        return extract_odmiana_rzeczownik_polski(
            wxr, template_node, sense_index
        )
    elif template_node.template_name == "odmiana-przymiotnik-polski":
        return extract_odmiana_przymiotnik_polski(
            wxr, template_node, sense_index
        )
    elif template_node.template_name == "odmiana-czasownik-polski":
        return extract_odmiana_czasownik_polski(wxr, template_node, sense_index)
    return []


def extract_odmiana_rzeczownik_polski(
    wxr: WiktextractContext, template_node: TemplateNode, sense_index: str
) -> list[Form]:
    # noun table
    # https://pl.wiktionary.org/wiki/Szablon:odmiana-rzeczownik-polski
    forms = []
    for arg_name, arg_value in template_node.template_parameters.items():
        if not isinstance(arg_name, str):
            continue
        if arg_name.startswith("Forma"):
            raw_tags = ["depr."] if arg_name.endswith("depr") else ["ndepr."]
            raw_tags.extend(["M.", "W.", "lm"])
        else:
            raw_tags = arg_name.lower().split()
        if isinstance(arg_value, str):
            arg_value = [arg_value]
        if isinstance(arg_value, list):
            form_nodes = []
            current_form_raw_tags = []
            for node in arg_value:
                if isinstance(node, str) and "/" in node:
                    slash_index = node.index("/")
                    form_nodes.append(node[:slash_index])
                    form_text = clean_node(wxr, None, form_nodes)
                    if form_text != "" and form_text != wxr.wtp.title:
                        form = Form(
                            form=form_text,
                            sense_index=sense_index,
                            raw_tags=raw_tags + current_form_raw_tags,
                        )
                        translate_raw_tags(form)
                        forms.append(form)
                    form_nodes.clear()
                    current_form_raw_tags.clear()
                    form_nodes.append(node[slash_index + 1 :])
                elif isinstance(node, TemplateNode):
                    node_text = clean_node(wxr, None, node)
                    if node_text.endswith("."):
                        current_form_raw_tags.append(node_text)
                    else:
                        form_nodes.append(node_text)
                else:
                    form_nodes.append(node)
            if len(form_nodes) > 0:
                form_text = clean_node(wxr, None, form_nodes)
                if form_text != "" and form_text != wxr.wtp.title:
                    form = Form(
                        form=form_text,
                        sense_index=sense_index,
                        raw_tags=raw_tags + current_form_raw_tags,
                    )
                    translate_raw_tags(form)
                    forms.append(form)
    return forms


def create_noun_form(
    form_text: str,
    sense_idx: str,
    raw_tags: list[str],
) -> Form:
    form = Form(form=form_text, sense_index=sense_idx, raw_tags=raw_tags)
    translate_raw_tags(form)
    return form


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


def extract_odmiana_czasownik_polski(
    wxr: WiktextractContext, template_node: TemplateNode, sense_index: str
) -> list[Form]:
    # verb table
    # https://pl.wiktionary.org/wiki/Szablon:odmiana-czasownik-polski
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    forms = []
    col_headers = []
    for table_tag in expanded_node.find_html_recursively("table"):
        forms.extend(
            extract_odmiana_czasownik_polski_table(
                wxr, table_tag, sense_index, col_headers
            )
        )
    return forms


def extract_odmiana_czasownik_polski_table(
    wxr: WiktextractContext,
    table_tag: WikiNode,
    sense_index: str,
    col_headers: list[TableHeader],
) -> list[Form]:
    forms = []
    row_headers = []
    for row_index, tr_tag in enumerate(table_tag.find_html("tr")):
        has_td_tag = any(t for t in tr_tag.find_html("td"))
        th_col_index = 0
        for th_tag in tr_tag.find_html("th"):
            th_text = clean_node(wxr, None, th_tag)
            if th_text in ["forma", "pozostałe formy"]:
                continue
            if not has_td_tag and "rowspan" not in th_tag.attrs:
                col_span = int(th_tag.attrs.get("colspan", "1"))
                col_headers.append(
                    TableHeader(th_text, th_col_index, th_col_index + col_span)
                )
                th_col_index += col_span
            else:
                row_span = int(th_tag.attrs.get("rowspan", "1"))
                if th_tag.contain_node(NodeKind.LINK):
                    for link_node in th_tag.find_child(NodeKind.LINK):
                        row_headers.append(
                            TableHeader(
                                clean_node(wxr, None, link_node),
                                row_index,
                                row_index + row_span,
                            )
                        )
                else:
                    row_headers.append(
                        TableHeader(th_text, row_index, row_index + row_span)
                    )

    for row_index, tr_tag in enumerate(table_tag.find_html("tr")):
        td_col_index = 0
        for td_tag in tr_tag.find_html("td"):
            if any(t for t in td_tag.find_html("table")):
                break
            td_text = clean_node(wxr, None, td_tag)
            col_span = int(td_tag.attrs.get("colspan", "1"))
            row_span = int(td_tag.attrs.get("rowspan", "1"))
            # "Szablon:potencjalnie" uses "{{int:potential-form-tooltip}}"
            # not implemented magic word
            is_potential_form = False
            for span_tag in td_tag.find_html(
                "span", attr_name="class", attr_value="potential-form"
            ):
                is_potential_form = True

            for line in td_text.splitlines():
                for form_text in line.split(","):
                    form_text = form_text.strip()
                    if form_text == "" or form_text == wxr.wtp.title:
                        continue
                    form = Form(form=form_text, sense_index=sense_index)
                    for col_header in col_headers:
                        if (
                            col_header.start < td_col_index + col_span
                            and td_col_index < col_header.end
                        ):
                            form.raw_tags.append(col_header.text)
                    for row_header in row_headers:
                        if (
                            row_header.start < row_index + row_span
                            and row_index < row_header.end
                        ):
                            form.raw_tags.append(row_header.text)
                    translate_raw_tags(form)
                    if is_potential_form:
                        form.tags.extend(["potential", "rare"])
                    forms.append(form)

            td_col_index += col_span

    return forms
