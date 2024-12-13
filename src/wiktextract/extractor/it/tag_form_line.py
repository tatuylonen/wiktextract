from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .inflection import extract_tabs_template
from .models import Form, WordEntry


def extract_tag_form_line_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    # https://it.wiktionary.org/wiki/Wikizionario:Manuale_di_stile#Genere_e_numero,_declinazione_o_paradigma
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            extract_italic_tag_node(wxr, word_entry, node)
        elif isinstance(node, TemplateNode):
            match node.template_name.lower():
                case "tabs":
                    extract_tabs_template(wxr, word_entry, node)
                case "linkp":
                    form = clean_node(
                        wxr, None, node.template_parameters.get(1, "")
                    )
                    if form != "":
                        word_entry.forms.append(
                            Form(form=form, tags=["plural"])
                        )


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
