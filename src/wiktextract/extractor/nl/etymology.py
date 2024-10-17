import re

from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Etymology


def extract_etymology_section(
    wxr: WiktextractContext, level_node: LevelNode
) -> list[Etymology]:
    etymology_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name == "((":
                    return etymology_list
            e_data = Etymology()
            cats = {}
            e_text = clean_node(wxr, cats, list_item.children)
            m = re.match(r"\[([A-Z])\]", e_text)
            if m is not None:
                e_data.index = m.group(1)
                e_text = e_text[m.end() :].strip()
            e_data.text = e_text
            e_data.categories = cats.get("categories", [])
            if len(e_data.text) > 0:
                etymology_list.append(e_data)
    return etymology_list
