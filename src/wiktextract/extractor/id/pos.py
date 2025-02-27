from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import Example, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    gloss_list_index = len(level_node.children)
    for index, node in enumerate(level_node.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#") and node.sarg.endswith("#"):
                    extract_gloss_list_item(wxr, page_data[-1], list_item)
                    if index < gloss_list_index:
                        gloss_list_index = index
        elif isinstance(node, TemplateNode) and node.template_name in [
            "lihat 2",
            "lihat ulang",
            "lihat v",
            "lihat2 a",
            "lihat2 adv",
            "lihat v ber2",
            "lihat n",
            "lihat 2 an",
            "lihat v ter2",
            "lihat2 v",
        ]:
            extract_lihat_2_template(wxr, page_data[-1], node)


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
) -> None:
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    after_br_tag = False
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            expanded = clean_node(wxr, sense, node)
            if expanded.startswith("(") and expanded.strip().endswith(
                (")", ") ·")
            ):
                sense.raw_tags.append(expanded.strip("()· "))
            else:
                gloss_nodes.append(expanded)
        elif (
            isinstance(node, HTMLNode) and node.tag == "br" and not after_br_tag
        ):
            after_br_tag = True
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and after_br_tag
        ):
            e_str = clean_node(wxr, None, node)
            if e_str != "":
                sense.examples.append(Example(text=e_str))
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
        elif child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for e_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, word_entry, sense, e_list_item)


def extract_lihat_2_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://id.wiktionary.org/wiki/Templat:lihat_2
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list_node in expanded_template.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sense = Sense()
            gloss_str = clean_node(wxr, sense, list_item.children)
            if "⇢" in gloss_str:
                sense.glosses.append(
                    gloss_str[gloss_str.index("⇢") + 1 :].strip()
                )
            if ")" in gloss_str:
                sense.raw_tags.append(
                    gloss_str[: gloss_str.index(")")].strip("( ")
                )
            if len(sense.glosses) > 0:
                word_entry.senses.append(sense)
