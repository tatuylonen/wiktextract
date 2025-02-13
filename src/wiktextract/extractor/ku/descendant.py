from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Descendant, WordEntry


def extract_descendant_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_desc_list_item(wxr, word_entry, [], list_item)


def extract_desc_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    parent_data: list[Descendant],
    list_item: WikiNode,
) -> None:
    desc_list = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "dû":
            desc = extract_dû_template(wxr, word_entry, node, parent_data)
            if desc is not None:
                desc_list.append(desc)
        elif isinstance(node, TemplateNode) and node.template_name == "dardû":
            desc = extract_dardû_template(wxr, word_entry, node, parent_data)
            if desc is not None:
                desc_list.append(desc)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_desc_list_item(
                    wxr, word_entry, desc_list, child_list_item
                )


def extract_dû_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    parent_descs: list[Descendant],
) -> Descendant | None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    desc = Descendant(
        word="",
        lang_code=clean_node(wxr, None, t_node.template_parameters.get(1, "")),
        lang="unknown",
    )
    extract_expanded_dû_template(wxr, desc, parent_descs, expanded_node)
    if desc.word != "":
        for parent_desc in parent_descs:
            parent_desc.descendants.append(desc)
        if len(parent_descs) == 0:
            word_entry.descendants.append(desc)
        return desc
    return None


def extract_expanded_dû_template(
    wxr: WiktextractContext,
    desc: Descendant,
    parent_descs: list[Descendant],
    expanded_node: WikiNode,
) -> None:
    for node in expanded_node.children:
        if isinstance(node, str) and ":" in node and desc.lang == "unknown":
            desc.lang = node[: node.index(":")].strip()
        elif isinstance(node, HTMLNode) and node.tag == "span":
            span_lang = node.attrs.get("lang", "")
            span_class = node.attrs.get("class", "")
            if span_lang.endswith("-Latn"):
                desc.roman = clean_node(wxr, None, node)
            elif span_lang != "":
                desc.word = clean_node(wxr, None, node)
                if desc.lang_code == "unknown":
                    desc.lang_code = span_lang
            elif span_class == "mention-gloss":
                desc.sense = clean_node(wxr, None, node)


def extract_dardû_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    parent_descs: list[Descendant],
) -> Descendant | None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    desc = Descendant(
        word="",
        lang_code=clean_node(wxr, None, t_node.template_parameters.get(1, "")),
        lang="unknown",
    )
    extract_expanded_dû_template(wxr, desc, parent_descs, expanded_node)
    for dd_tag in expanded_node.find_html_recursively("dd"):
        child_desc = Descendant(word="", lang_code="unknown", lang="unknown")
        extract_expanded_dû_template(wxr, child_desc, [desc], dd_tag)
        if child_desc.word != "":
            desc.descendants.append(child_desc)
    if desc.word != "":
        for parent_desc in parent_descs:
            parent_desc.descendants.append(desc)
        if len(parent_descs) == 0:
            word_entry.descendants.append(desc)
        return desc
    return None
