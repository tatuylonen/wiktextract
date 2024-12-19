from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .inflection import (
    extract_appendix_conjugation_page,
    extract_it_decl_agg_template,
    extract_tabs_template,
)
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_tag_form_line_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    # https://it.wiktionary.org/wiki/Wikizionario:Manuale_di_stile#Genere_e_numero,_declinazione_o_paradigma
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            extract_italic_tag_node(wxr, word_entry, node)
        elif isinstance(node, TemplateNode):
            if node.template_name.lower() == "tabs":
                extract_tabs_template(wxr, word_entry, node)
            elif node.template_name.lower() in FORM_LINK_TEMPLATES:
                extract_form_link_template(wxr, word_entry, node)
            elif node.template_name.lower().startswith("it-decl-agg"):
                extract_it_decl_agg_template(wxr, word_entry, node)
            elif node.template_name.lower() == "a cmp":
                extract_a_cmp_template(wxr, word_entry, node)
            elif node.template_name.lower() == "pn":
                extract_pn_template(wxr, word_entry, node)


ITALIC_TAGS = {
    "c": "common",
    "coll": "collective",
    "f": "feminine",
    "m": "masculine",
    "n": "neuter",
    "pl": "plural",
    "sing": "singular",
    "prom": "common",
    "inv": "invariable",
}


def extract_italic_tag_node(
    wxr: WiktextractContext, word_entry: WordEntry, node: WikiNode
) -> None:
    # https://it.wiktionary.org/wiki/Wikizionario:Genere
    italic_str = clean_node(wxr, None, node)
    for raw_tag in italic_str.split():
        if raw_tag in ITALIC_TAGS:
            word_entry.tags.append(ITALIC_TAGS[raw_tag])
        else:
            word_entry.raw_tags.append(raw_tag)


FORM_LINK_TEMPLATES = {
    "linkf": ["feminine"],
    "linkfp": ["feminine", "plural"],
    "linkg": ["genitive"],
    "linkm": ["masculine"],
    "linkn": ["neuter"],
    "linkmai": ["uppercase"],
    "linkp": ["plural"],
    "links": ["singular"],
}


def extract_form_link_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    arg_name = 1
    while arg_name in t_node.template_parameters:
        form = clean_node(
            wxr, None, t_node.template_parameters.get(arg_name, "")
        )
        if form != "":
            word_entry.forms.append(Form(form=form, tags=["plural"]))
        arg_name += 1


def extract_a_cmp_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:A_cmp
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tag = ""
    for node in expanded_node.find_child(NodeKind.ITALIC | NodeKind.BOLD):
        match node.kind:
            case NodeKind.ITALIC:
                raw_tag = clean_node(wxr, None, node)
            case NodeKind.BOLD:
                form_str = clean_node(wxr, None, node)
                if form_str not in ["", wxr.wtp.title]:
                    form = Form(form=form_str)
                    if raw_tag != "":
                        form.raw_tags.append(raw_tag)
                    translate_raw_tags(form)
                    word_entry.forms.append(form)


def extract_pn_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:Pn
    has_c_arg = False
    for arg_key, arg_value in t_node.template_parameters.items():
        if arg_key == "c":
            has_c_arg = True
            break
        arg_value_str = clean_node(wxr, None, arg_value)
        if arg_value_str == "c":
            has_c_arg = True
            break
    if not has_c_arg:
        return
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for small_tag in expanded_node.find_html("small"):
        for link_node in small_tag.find_child(NodeKind.LINK):
            if len(link_node.largs) > 0:
                link_str = clean_node(wxr, None, link_node.largs[0])
                if link_str.startswith("Appendice:Coniugazioni/"):
                    extract_appendix_conjugation_page(wxr, word_entry, link_str)
