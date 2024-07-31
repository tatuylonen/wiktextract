from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .example import extract_example_list_item
from .models import Sense, WordEntry
from .section_titles import POS_DATA


def parse_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            process_gloss_list_item(wxr, page_data[-1], list_item)


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item_node: WikiNode,
) -> None:
    gloss_nodes = list(
        list_item_node.invert_find_child(NodeKind.LIST, include_empty_str=True)
    )
    sense_data = Sense()
    gloss_only_nodes = []
    for gloss_node in gloss_nodes:
        if isinstance(
            gloss_node, TemplateNode
        ) and gloss_node.template_name in ("context", "タグ"):
            # https://ja.wiktionary.org/wiki/テンプレート:context
            # https://ja.wiktionary.org/wiki/テンプレート:タグ
            raw_tag = clean_node(wxr, sense_data, gloss_node).strip("()")
            if len(raw_tag) > 0:
                sense_data.raw_tags.append(raw_tag)
        else:
            gloss_only_nodes.append(gloss_node)
    expanded_gloss = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(gloss_only_nodes), expand_all=True
    )
    ruby, no_ruby = extract_ruby(wxr, expanded_gloss.children)
    gloss_text = clean_node(wxr, sense_data, no_ruby)
    sense_data.ruby = ruby
    if len(gloss_text) > 0:
        sense_data.glosses.append(gloss_text)

    for nest_gloss_list in list_item_node.find_child(NodeKind.LIST):
        if nest_gloss_list.sarg.endswith(("*", ":")):
            for example_list_item in nest_gloss_list.find_child(
                NodeKind.LIST_ITEM
            ):
                extract_example_list_item(wxr, sense_data, example_list_item)

    if len(sense_data.glosses) > 0:
        word_entry.senses.append(sense_data)
