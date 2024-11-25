import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS
from .tags import translate_raw_tags

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
                word_entry.derived.append(
                    Linkage(
                        word=word,
                        sense=word_entry.senses[-1].glosses[-1]
                        if len(word_entry.senses) > 0
                        else "",
                    )
                )


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
            extract_linkage_list_item(
                wxr, word_entry, list_item, linkage_type, True
            )

        for t_node in level_node.find_child(NodeKind.TEMPLATE):
            extract_linkage_template(wxr, word_entry, t_node)
            if t_node.template_name == "외국어":
                extract_translation_template(wxr, word_entry, t_node)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    in_linkage_section: bool,
) -> None:
    raw_tag = ""
    is_roman = False
    for child in list_item.children:
        if isinstance(child, str):
            if ":" in child:
                l_type_str = child[: child.index(":")].strip()
                if l_type_str in LINKAGE_SECTIONS:
                    linkage_type = LINKAGE_SECTIONS[l_type_str]
            else:
                m = re.search(r"\(([^()]+)\)", child)
                if m is not None:
                    raw_tag = m.group(1).strip()
                    is_roman = re.search(r"[a-z]", raw_tag) is not None

    for link_node in list_item.find_child(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if word != "":
            linkage = Linkage(
                word=word,
                sense=word_entry.senses[-1].glosses[-1]
                if len(word_entry.senses) > 0 and not in_linkage_section
                else "",
            )
            if len(raw_tag) > 0:
                if is_roman:
                    linkage.roman = raw_tag
                elif re.fullmatch(r"\d+", raw_tag) is not None:
                    linkage.sense_index = raw_tag
                else:
                    linkage.raw_tags.append(raw_tag)
                    translate_raw_tags(linkage)
            getattr(word_entry, linkage_type).append(linkage)

    if not list_item.contain_node(NodeKind.LINK):
        word = clean_node(wxr, None, list_item.children)
        if word != "":
            linkage = Linkage(
                word=word,
                sense=word_entry.senses[-1].glosses[-1]
                if len(word_entry.senses) > 0 and not in_linkage_section
                else "",
            )
            translate_raw_tags(linkage)
            getattr(word_entry, linkage_type).append(linkage)


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
        else:
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name in ["l", "연결"]:
                    extract_l_template(wxr, word_entry, t_node, "proverbs")


def extract_l_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    # https://ko.wiktionary.org/wiki/틀:연결
    # https://en.wiktionary.org/wiki/Template:link
    for word_arg in [3, 2]:
        if word_arg in t_node.template_parameters:
            word = clean_node(wxr, None, t_node.template_parameters[word_arg])
            if word == "":
                break
            linkage = Linkage(word=word)
            for sense_arg in ["t", 4]:
                if sense_arg in t_node.template_parameters:
                    linkage.sense = clean_node(
                        wxr, None, t_node.template_parameters[sense_arg]
                    )
                    break
            getattr(word_entry, linkage_type).append(linkage)
            break
