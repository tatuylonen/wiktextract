from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS

LINKAGE_TEMPLATES = frozenset(["파생어 상자", "합성어 상자"])


def extract_linkage_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    node: TemplateNode,
) -> None:
    # https://ko.wiktionary.org/wiki/틀:파생어_상자
    # https://ko.wiktionary.org/wiki/틀:합성어_상자
    if node.template_name in ["파생어 상자", "합성어 상자"]:
        for key in range(1, 41):
            if key not in node.template_parameters:
                break
            word = clean_node(wxr, None, node.template_parameters[key])
            if word != "":
                word_entry.derived.append(Linkage(word=word))


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    if linkage_type == "proverbs":
        extract_proverb_section(wxr, word_entry, level_node)
    else:
        from .translation import extract_translation_template

        for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item, linkage_type)

        for t_node in level_node.find_child(NodeKind.TEMPLATE):
            extract_linkage_template(wxr, word_entry, t_node)
            if t_node.template_name == "외국어":
                extract_translation_template(wxr, word_entry, t_node)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
) -> None:
    for child in list_item.children:
        if isinstance(child, str) and ":" in child:
            l_type_str = child[: child.index(":")].strip()
            if l_type_str in LINKAGE_SECTIONS:
                linkage_type = LINKAGE_SECTIONS[l_type_str]

    for link_node in list_item.find_child(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if word != "":
            getattr(word_entry, linkage_type).append(Linkage(word=word))


def extract_proverb_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        linkage = Linkage(word="")
        for index, child in enumerate(list_item.children):
            if isinstance(child, str) and ":" in child:
                linkage.word = clean_node(wxr, None, list_item.children[:index])
                linkage.word += child[: child.index(":")].strip()
                linkage.sense = child[child.index(":") + 1 :].strip()
                linkage.sense += clean_node(
                    wxr, None, list_item.children[index + 1 :]
                )
                break
        if linkage.word != "":
            word_entry.proverbs.append(linkage)
