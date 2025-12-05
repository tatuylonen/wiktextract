from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Attestation, WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    missing_etymology = "Si puedes, incorpórala: ver cómo"
    e_nodes = []
    for node in level_node.children:
        if isinstance(node, LevelNode):
            break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                e_text = clean_node(wxr, base_data, list_item.children)
                if e_text != "" and not e_text.startswith(missing_etymology):
                    base_data.etymology_texts.append(e_text)
        elif (
            isinstance(node, TemplateNode) and node.template_name == "datación"
        ):
            date = clean_node(wxr, None, node.template_parameters.get(1, ""))
            if date != "":
                base_data.attestations.append(Attestation(date=date))
            e_nodes.append(node)
        else:
            e_nodes.append(node)

    if len(e_nodes) > 0:
        e_text = clean_node(wxr, base_data, e_nodes)
        if e_text != "" and not e_text.startswith(missing_etymology):
            base_data.etymology_texts.append(e_text)
