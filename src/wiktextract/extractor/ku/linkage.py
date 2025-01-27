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
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name.startswith("ku-"):
                    extract_ku_form_template(wxr, word_entry, t_node)
                elif t_node.template_name == "g":
                    extract_g_template(wxr, word_entry, t_node)


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
