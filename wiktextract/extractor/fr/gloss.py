from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = list(list_item_node.invert_find_child(NodeKind.LIST))
        gloss_data = defaultdict(list)
        gloss_start = 0
        # process modifier, theme tempaltes before gloss text
        # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste de tous les modèles/Précisions de sens
        if (
            len(gloss_nodes) > 0
            and isinstance(gloss_nodes[0], WikiNode)
            and gloss_nodes[0].kind == NodeKind.TEMPLATE
        ):
            gloss_start = 1
            for index, gloss_node in enumerate(gloss_nodes[1:], 1):
                if (
                    not isinstance(gloss_node, WikiNode)
                    or gloss_node.kind != NodeKind.TEMPLATE
                ):
                    gloss_start = index
                    break
            for mod_template in gloss_nodes[:gloss_start]:
                gloss_data["tags"].append(
                    clean_node(wxr, gloss_data, mod_template).strip("()")
                )

        gloss_text = clean_node(wxr, gloss_data, gloss_nodes[gloss_start:])
        gloss_data["glosses"] = [gloss_text]
        page_data[-1]["senses"].append(gloss_data)
