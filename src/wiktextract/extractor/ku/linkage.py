from itertools import count

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_other_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
                if isinstance(node, TemplateNode):
                    if node.template_name.startswith("ku-"):
                        extract_ku_form_template(wxr, word_entry, node)
                    elif node.template_name == "g":
                        extract_g_template(wxr, word_entry, node)
                    elif node.template_name in ["herwiha", "hw"]:
                        extract_hw_template(wxr, word_entry, node)
                elif node.kind == NodeKind.LINK:
                    form = clean_node(wxr, None, node)
                    if form != "":
                        word_entry.forms.append(Form(form=form))


def extract_ku_form_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    form = Form(form="")
    for index, span_tag in enumerate(expanded_node.find_html("span")):
        if index == 0:
            form.raw_tags.append(clean_node(wxr, None, span_tag))
        elif index == 1:
            form.form = clean_node(wxr, None, span_tag)
    if form.form != "":
        word_entry.forms.append(form)


def extract_g_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    form = Form(
        form=clean_node(
            wxr,
            None,
            t_node.template_parameters.get(
                2, t_node.template_parameters.get("cuda", "")
            ),
        ),
        roman=clean_node(wxr, None, t_node.template_parameters.get("tr", "")),
        translation=clean_node(
            wxr, None, t_node.template_parameters.get("w", "")
        ),
    )
    if form.form != "":
        word_entry.forms.append(form)


def extract_hw_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:hw
    raw_tags = []
    forms = []
    for arg in count(5):
        if arg not in t_node.template_parameters:
            break
        raw_tag = clean_node(wxr, None, t_node.template_parameters[arg])
        if raw_tag != "":
            raw_tags.append(raw_tag)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        if span_lang == lang_code:
            form_str = clean_node(wxr, None, span_tag)
            if form_str != "":
                forms.append(Form(form=form_str, raw_tags=raw_tags))
        elif span_lang.endswith("-Latn") and len(forms) > 0:
            forms[-1].roman = clean_node(wxr, None, span_tag)

    word_entry.forms.extend(forms)
