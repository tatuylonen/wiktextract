import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags

FORM_SECTIONS = {
    "zapis": [],
    "transliteracja": ["transliteration"],
    "transkrypcja": ["transcription"],
    "zapisy w ortografiach alternatywnych": ["alternative"],
    "warianty": ["alternative"],
    "kody": ["alternative"],
    "kolejność": ["alternative"],
    "kreski": ["alternative"],
    "słowniki": ["alternative"],
    "hanja": ["hanja"],
}


def extract_form_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    forms = []
    # get around "preformatted" node
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\([\d\s,-.]+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
                    roman = node[m.end() :].strip()
                    if roman != "":
                        forms.append(
                            Form(
                                form=roman,
                                sense_index=sense_index,
                                tags=tags,
                            )
                        )
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                form = clean_node(wxr, None, node)
                if form != "":
                    forms.append(Form(form=form, tags=tags))

    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name in ["ptrad", "pupr"]:
            forms.extend(extract_ptrad_template(wxr, t_node, tags))
        elif t_node.template_name == "translit":
            roman = clean_node(wxr, None, t_node)
            if roman != "":
                forms.append(Form(form=roman, tags=tags))
        elif t_node.template_name.startswith("ortografie"):
            forms.extend(extract_ortografie_template(wxr, t_node, tags))
        elif t_node.template_name == "hep":
            forms.extend(extract_hep_template(wxr, t_node, tags))

    if len(forms) == 0:
        form = clean_node(wxr, None, level_node.children)
        if form != "":
            forms.append(Form(form=form, tags=tags))

    for data in page_data:
        if data.lang_code == base_data.lang_code:
            data.forms.extend(forms)
    if len(page_data) == 0:
        base_data.forms.extend(forms)


def extract_ptrad_template(
    wxr: WiktextractContext, t_node: TemplateNode, tags: list[str]
) -> list[Form]:
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tag = ""
    for span_tag in expanded_node.find_html("span"):
        if span_tag.attrs.get("class", "") == "short-container":
            raw_tag = clean_node(wxr, None, span_tag)
        if span_tag.attrs.get("lang", "") == "zh":
            word = clean_node(wxr, None, span_tag)
            if word not in ["", wxr.wtp.title]:
                form = Form(form=word, tags=tags)
                if raw_tag != "":
                    form.raw_tags.append(raw_tag)
                    translate_raw_tags(form)
                forms.append(form)
    return forms


def extract_ortografie_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    tags: list[str],
) -> list[Form]:
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    forms.extend(extract_ortografie_list_item(wxr, expanded_node, tags))
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            forms.extend(extract_ortografie_list_item(wxr, list_item, tags))
    return forms


def extract_ortografie_list_item(
    wxr: WiktextractContext, list_item: WikiNode, tags: list[str]
) -> list[Form]:
    forms = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            node_str = clean_node(wxr, None, node)
            if node_str.endswith(":"):
                raw_tag = node_str.strip(": ")
        elif isinstance(node, str) and node.strip() != "":
            form = Form(form=node.strip(), tags=tags)
            if raw_tag != "":
                form.raw_tags.append(raw_tag)
                translate_raw_tags(form)
            forms.append(form)
    return forms


def extract_hep_template(
    wxr: WiktextractContext, t_node: TemplateNode, tags: list[str]
) -> list[Form]:
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tag = ""
    for node in expanded_node.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            node_str = clean_node(wxr, None, node)
            if node_str.endswith(":"):
                raw_tag = node_str.strip(":")
        elif isinstance(node, str) and node.strip() != "":
            form = Form(form=node.strip(), tags=tags)
            if raw_tag != "":
                form.raw_tags.append(raw_tag)
                translate_raw_tags(form)
            forms.append(form)
    return forms
