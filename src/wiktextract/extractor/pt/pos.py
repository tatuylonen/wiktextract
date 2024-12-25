import re

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .head_line import extract_head_line_nodes
from .inflection import extract_flex_template
from .models import Example, Linkage, Sense, WordEntry
from .section_titles import POS_DATA


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
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
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
    for arg in range(2, 9):
        if arg not in t_node.template_parameters:
            break
        raw_tag = clean_node(wxr, None, t_node.template_parameters[arg])
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)
    clean_node(wxr, sense, t_node)


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


def extract_example_list_item(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    example = Example()
    ref_nodes = []

    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and example.text == ""
        ):
            example.text = clean_node(wxr, None, node)
        elif isinstance(node, HTMLNode) and node.tag == "small":
            example.translation = clean_node(wxr, None, node)
            if example.translation.startswith(
                "("
            ) and example.translation.endswith(")"):
                example.translation = example.translation.strip("()")
        elif isinstance(node, TemplateNode):
            match node.template_name:
                case "OESP":
                    example.ref = clean_node(wxr, sense, node).strip("()")
                case "tradex":
                    example.text = clean_node(
                        wxr, None, node.template_parameters.get(2, "")
                    )
                    example.translation = clean_node(
                        wxr, None, node.template_parameters.get(3, "")
                    )
                    clean_node(wxr, sense, node)
                case "Ex.":
                    example.text = clean_node(
                        wxr, sense, node.template_parameters.get(1, "")
                    )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            bold_str = clean_node(wxr, None, node)
            if re.fullmatch(r"\d+", bold_str) is not None:
                list_item_str = clean_node(
                    wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
                )
                if list_item_str.endswith(":"):
                    ref_nodes.clear()
                    example.ref = list_item_str
                    for child_list in list_item.find_child(NodeKind.LIST):
                        for child_list_item in child_list.find_child(
                            NodeKind.LIST_ITEM
                        ):
                            example.text = clean_node(
                                wxr, None, child_list_item.children
                            )
                    break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            ref_nodes.clear()
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                ref_nodes.append(child_list_item.children)
        else:
            ref_nodes.append(node)

    if example.text != "":
        if example.ref == "":
            example.ref = clean_node(wxr, sense, ref_nodes).strip(":() \n")
        sense.examples.append(example)
