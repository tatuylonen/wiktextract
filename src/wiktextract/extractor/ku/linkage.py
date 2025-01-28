import re
from itertools import count

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry


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
    linkage_type: str = "",
    sense: str = "",
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
        if linkage_type == "":
            word_entry.forms.append(form)
        else:
            getattr(word_entry, linkage_type).append(
                Linkage(
                    word=form.form,
                    raw_tags=form.raw_tags,
                    sense=sense,
                )
            )


def extract_g_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str = "",
    sense: str = "",
) -> None:
    if linkage_type == "":
        form = Form(
            form=clean_node(
                wxr,
                None,
                t_node.template_parameters.get(
                    2, t_node.template_parameters.get("cuda", "")
                ),
            ),
            roman=clean_node(
                wxr, None, t_node.template_parameters.get("tr", "")
            ),
            translation=clean_node(
                wxr, None, t_node.template_parameters.get("w", "")
            ),
        )
        if form.form != "":
            word_entry.forms.append(form)
    else:
        l_data = Linkage(
            word=clean_node(
                wxr,
                None,
                t_node.template_parameters.get(
                    2, t_node.template_parameters.get("cuda", "")
                ),
            ),
            roman=clean_node(
                wxr, None, t_node.template_parameters.get("tr", "")
            ),
            translation=clean_node(
                wxr, None, t_node.template_parameters.get("w", "")
            ),
            sense=sense,
        )
        if l_data.word != "":
            getattr(word_entry, linkage_type).append(l_data)


def extract_hw_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str = "",
    sense: str = "",
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

    if linkage_type == "":
        word_entry.forms.extend(forms)
    else:
        getattr(word_entry, linkage_type).extend(
            [
                Linkage(
                    word=f.form,
                    roman=f.roman,
                    sense=sense,
                    raw_tags=f.raw_tags,
                )
                for f in forms
            ]
        )


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
    linkage_type: str,
) -> None:
    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if (
            isinstance(node, TemplateNode)
            and re.fullmatch(r"kol(?:\d+)?", node.template_name) is not None
        ):
            extract_kol_template(wxr, word_entry, node, linkage_type)
        elif isinstance(node, TemplateNode) and node.template_name == "stûn":
            pass
        elif node.kind == NodeKind.LIST:
            pass


def extract_kol_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:kol
    sense = clean_node(wxr, None, t_node.template_parameters.get("sernav", ""))
    for arg in count(3 if t_node.template_name == "kol" else 2):
        if arg not in t_node.template_parameters:
            break
        arg_value = t_node.template_parameters[arg]
        if isinstance(arg_value, str) and arg_value.strip() != "":
            getattr(word_entry, linkage_type).append(
                Linkage(word=arg_value.strip(), sense=sense)
            )
        elif (
            isinstance(arg_value, TemplateNode)
            and arg_value.template_name == "g"
        ):
            extract_g_template(wxr, word_entry, arg_value, linkage_type)
