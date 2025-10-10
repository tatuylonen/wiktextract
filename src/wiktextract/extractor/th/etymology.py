from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    e_nodes = []
    for node in level_node.children:
        if not (
            (isinstance(node, WikiNode) and node.kind in LEVEL_KIND_FLAGS)
            or (
                isinstance(node, TemplateNode)
                and node.template_name in ["ja-see", "ja-see-kango"]
            )
        ):
            e_nodes.append(node)

    e_str = clean_node(wxr, base_data, e_nodes)
    if e_str != "":
        base_data.etymology_text = e_str
