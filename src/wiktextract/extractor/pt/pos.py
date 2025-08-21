import re

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .head_line import extract_head_line_nodes
from .inflection import extract_flex_template
from .models import AltForm, Linkage, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
    categories: list[str],
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title.lower()]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))
    page_data[-1].categories.extend(categories)

    first_gloss_index = len(level_node.children)
    for index, list_node in level_node.find_child(NodeKind.LIST, True):
        if list_node.sarg.startswith("#") and list_node.sarg.endswith("#"):
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
            if index < first_gloss_index:
                first_gloss_index = index
    extract_head_line_nodes(
        wxr, page_data[-1], level_node.children[:first_gloss_index]
    )
    # forms table template may not in header line
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.startswith("flex."):
            extract_flex_template(wxr, page_data[-1], t_node)

    base_data_pos = page_data[-1].model_copy(deep=True)
    first_child_section = True
    for child_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        child_section = clean_node(wxr, None, child_level_node.largs)
        if child_section in ["Brasil", "Portugal"]:
            page_data.append(base_data_pos.model_copy(deep=True))
            if first_child_section:
                page_data.pop()
                first_child_section = False
            page_data[-1].raw_tags.append(child_section)
            for list_node in child_level_node.find_child(NodeKind.LIST):
                if list_node.sarg.startswith("#") and list_node.sarg.endswith(
                    "#"
                ):
                    for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                        extract_gloss_list_item(wxr, page_data[-1], list_item)
            translate_raw_tags(page_data[-1])


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry | Linkage,
    list_item: WikiNode,
    parent_gloss: list[str] = [],
) -> None:
    gloss_nodes = []
    sense = Sense(glosses=parent_gloss)
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name == "escopo":
                extract_escopo_template(wxr, sense, node)
            elif node.template_name == "escopo2":
                sense.raw_tags.extend(extract_escopo2_template(wxr, node))
            else:
                gloss_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            if node.sarg.endswith(("*", ":")):
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(wxr, sense, next_list_item)
        else:
            gloss_nodes.append(node)

    gloss_str = clean_node(wxr, sense, gloss_nodes)
    if len(gloss_str) > 0:
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        if "form-of" in word_entry.tags:
            extract_form_of_word(wxr, sense, list_item)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(
                    wxr, word_entry, child_list_item, sense.glosses
                )


def extract_escopo_template(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    # https://pt.wiktionary.org/wiki/Predefinição:escopo
    expanded_str = clean_node(wxr, sense, t_node).strip("()")
    for raw_tag in re.split(r", | e ", expanded_str):
        if raw_tag.strip() != "":
            sense.raw_tags.append(raw_tag.strip())


def extract_escopo2_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
) -> list[str]:
    # https://pt.wiktionary.org/wiki/Predefinição:escopo2
    raw_tags = []
    for arg in range(1, 4):
        if arg not in t_node.template_parameters:
            break
        raw_tag = clean_node(wxr, None, t_node.template_parameters[arg])
        if raw_tag != "":
            raw_tags.append(raw_tag)
    return raw_tags


def extract_form_of_word(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
) -> None:
    form_of = ""
    for link_node in list_item.find_child_recursively(NodeKind.LINK):
        form_of = clean_node(wxr, None, link_node)
    if form_of != "":
        sense.form_of.append(AltForm(word=form_of))
        sense.tags.append("form-of")
