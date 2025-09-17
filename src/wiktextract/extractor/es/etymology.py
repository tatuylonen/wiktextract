from wikitextprocessor.parser import LEVEL_KIND_FLAGS, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Attestation, WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: TemplateNode
) -> None:
    text = clean_node(
        wxr,
        word_entry,
        list(
            level_node.invert_find_child(
                LEVEL_KIND_FLAGS, include_empty_str=True
            )
        ),
    )
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "datación":
            date = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
            if date != "":
                word_entry.attestations.append(Attestation(date=date))
    if not text.startswith("Si puedes, incorpórala: ver cómo"):
        word_entry.etymology_text = text
