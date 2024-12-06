import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import translate_raw_tags


def extract_expression_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_expression_list_item(wxr, word_entry, list_item)


def extract_expression_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    from .pos import extract_gloss_list_item

    expression_data = Linkage(word="")
    sense_nodes = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            expression_data.word = clean_node(wxr, None, node)
        elif isinstance(node, str) and ":" in node:
            node = node.lstrip(": ")
            if node != "":
                sense_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            sense_nodes.append(node)

    sense_str = clean_node(
        wxr,
        None,
        [
            n
            for n in sense_nodes
            if not (
                isinstance(n, TemplateNode) and n.template_name == "escopo2"
            )
        ],
    )
    if sense_str != "":
        gloss_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
        gloss_list_item.children = sense_nodes
        for child_list in list_item.find_child(NodeKind.LIST):
            gloss_list_item.children.append(child_list)
        extract_gloss_list_item(wxr, expression_data, gloss_list_item)
    else:
        for child_list in list_item.find_child(NodeKind.LIST):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, expression_data, child_list_item)

    if expression_data.word != "":
        word_entry.expressions.append(expression_data)


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    sense = ""
    sense_index = 0
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name == "fraseini":
            sense, sense_index = extract_fraseini_template(wxr, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_linkage_list_item(
                    wxr, word_entry, list_item, linkage_type, sense, sense_index
                )


def extract_fraseini_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[str, int]:
    sense = ""
    sense_index = 0
    first_arg = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    m = re.search(r"(\d+)$", first_arg)
    if m is not None:
        sense_index = int(m.group(1))
        sense = first_arg[: m.start()].strip()
    else:
        sense = first_arg
    return sense, sense_index


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    sense: str,
    sense_index: int,
) -> None:
    linkage_words = []
    raw_tags = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            match node.template_name:
                case "link preto":
                    word = clean_node(
                        wxr, None, node.template_parameters.get(1, "")
                    )
                    if word != "":
                        linkage_words.append(word)
                case "escopo2":
                    from .pos import extract_escopo2_template

                    raw_tags.extend(extract_escopo2_template(wxr, node))
        elif isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "" and not word.startswith("Wikisaurus:"):
                        linkage_words.append(word)
                case NodeKind.BOLD:
                    bold_str = clean_node(wxr, None, node)
                    if re.fullmatch(r"\d+", bold_str):
                        sense_index = int(bold_str)
                case NodeKind.ITALIC:
                    raw_tag = clean_node(wxr, None, node)
                    if raw_tag != "":
                        raw_tags.append(raw_tag)
                case NodeKind.LIST:
                    for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                        extract_linkage_list_item(
                            wxr,
                            word_entry,
                            child_list_item,
                            linkage_type,
                            sense,
                            sense_index,
                        )
        elif isinstance(node, str):
            m = re.search(r"\((.+)\)", node)
            if m is not None:
                sense = m.group(1)

    for word in linkage_words:
        linkage = Linkage(
            word=word, sense=sense, sense_index=sense_index, raw_tags=raw_tags
        )
        translate_raw_tags(linkage)
        getattr(word_entry, linkage_type).append(linkage)
