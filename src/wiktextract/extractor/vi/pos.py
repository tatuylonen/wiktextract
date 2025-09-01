from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
):
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    base_data.pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    gloss_list_index = len(level_node.children)
    for index, list_node in level_node.find_child(NodeKind.LIST, True):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if list_node.sarg.startswith("#") and list_node.sarg.endswith("#"):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
                if index < gloss_list_index:
                    gloss_list_index = index


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
):
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["nhãn", "label", "def-lb"]:
                extract_label_template(wxr, sense, node)
            elif node.template_name == "term":
                extract_term_template(wxr, sense, node)
            else:
                gloss_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)
    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)


def extract_label_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:nhãn
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        span_classes = span_tag.attrs.get("class", "").split()
        if "label-content" in span_classes:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                sense.raw_tags.append(raw_tag)


def extract_term_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:term
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for italic_node in expanded_node.find_child(NodeKind.ITALIC):
        raw_tag = clean_node(wxr, None, italic_node)
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)
