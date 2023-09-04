from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


GENDER_TEMPLATES = {
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",
    "mf": "masculine and feminine identical",
    "mf ?": "masculine or feminine (usage hesitates)",
    "fm ?": "feminine or masculine (usage hesitates)",
}


def extract_form_line(
    wxr: WiktextractContext,
    page_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
) -> None:
    """
    Ligne de forme
    https://fr.wiktionary.org/wiki/Wiktionnaire:Structure_des_pages#Syntaxe

    A line of wikitext between pos subtitle and the first gloss, contains IPA,
    gender and inflection forms.
    """
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.TEMPLATE:
            if node.template_name in {"pron", "prononciation"}:
                page_data[-1]["sounds"].append(
                    {"ipa": clean_node(wxr, None, node)}
                )
            elif node.template_name in GENDER_TEMPLATES:
                page_data[-1]["tags"].append(
                    GENDER_TEMPLATES.get(node.template_name)
                )
