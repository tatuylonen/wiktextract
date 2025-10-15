import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import capture_text_in_parentheses
from .models import Descendant, Form, Linkage, WordEntry
from .section_types import LINKAGE_SECTIONS, LINKAGE_TAGS
from .tags import translate_raw_tags


def extract_linkage(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    section_type: str,
) -> None:
    if section_type == "anagrammes":
        for node in level_node.find_child(NodeKind.TEMPLATE):
            if node.template_name == "voir anagrammes":
                anagram_list = process_voir_anagrammes_template(wxr, node)
                for data in page_data:
                    if data.lang_code == page_data[-1].lang_code:
                        data.anagrams.extend(anagram_list)
    else:
        extract_linkage_section(
            wxr,
            page_data[-1],
            level_node,
            LINKAGE_SECTIONS[section_type],
            LINKAGE_TAGS.get(section_type, []),
        )


def extract_desc_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    # drrive to other languages list
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        lang_code = "unknown"
        lang_name = "unknown"
        for node in list_item.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
            if isinstance(node, TemplateNode) and node.template_name == "L":
                lang_code = node.template_parameters.get(1)
                lang_name = clean_node(wxr, None, node)
            elif node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                word_entry.descendants.append(
                    Descendant(lang_code=lang_code, lang=lang_name, word=word)
                )
            elif isinstance(node, TemplateNode) and node.template_name in [
                "l",
                "lien",
                "zh-lien",
                "zh-lien-t",
            ]:
                l_data = Linkage(word="")
                process_linkage_template(wxr, node, l_data)
                word_entry.descendants.append(
                    Descendant(
                        lang=lang_name,
                        lang_code=lang_code,
                        word=l_data.word,
                        roman=l_data.roman,
                        ruby=l_data.ruby,
                        tags=l_data.tags,
                        raw_tags=l_data.raw_tags,
                    )
                )
            elif (
                isinstance(node, TemplateNode) and node.template_name == "zh-l"
            ):
                l_list = extract_zh_l_template(wxr, node)
                for l_data in l_list:
                    word_entry.descendants.append(
                        Descendant(
                            lang=lang_name,
                            lang_code=lang_code,
                            word=l_data.word,
                            roman=l_data.roman,
                            tags=l_data.tags,
                            raw_tags=l_data.raw_tags,
                        )
                    )


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
    section_tags: list[str] = [],
):
    sense_text = ""
    sense_index = 0
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name == "(":
            new_sense_text = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            if new_sense_text != "":
                sense_text = new_sense_text
            sense_index_text = node.template_parameters.get(2, "0")
            if (
                isinstance(sense_index_text, str)
                and sense_index_text.isdecimal()
            ):
                sense_index = int(sense_index_text)
        elif (
            isinstance(node, WikiNode)
            and node.kind in NodeKind.BOLD | NodeKind.ITALIC
        ):
            sense_text = clean_node(wxr, None, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            # sense could also be in ";" description list
            if node.sarg in [";", ":"]:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    sense_text = clean_node(wxr, None, list_item.children)
                    index_pattern = r"\s*\((?:sens\s*)?(\d+)\)$"
                    m = re.search(index_pattern, sense_text)
                    if m is not None:
                        sense_text = re.sub(index_pattern, "", sense_text)
                        sense_index = int(m.group(1))
            else:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_linkage_list_item(
                        wxr,
                        word_entry,
                        list_item,
                        linkage_type,
                        section_tags,
                        sense_text,
                        sense_index,
                    )


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    section_tags: list[str],
    sense: str,
    sense_index: int,
):
    linkage_data = Linkage(
        word="", tags=section_tags, sense=sense, sense_index=sense_index
    )
    pending_tag = ""
    inside_bracket = False
    for index, child_node in enumerate(list_item.children):
        if isinstance(
            child_node, TemplateNode
        ) and child_node.template_name in [
            "l",
            "lien",
            "zh-lien",
            "zh-lien-t",
        ]:
            process_linkage_template(wxr, child_node, linkage_data)
        elif (
            isinstance(child_node, TemplateNode)
            and child_node.template_name == "zh-l"
        ):
            getattr(word_entry, linkage_type).extend(
                extract_zh_l_template(
                    wxr, child_node, section_tags, sense, sense_index
                )
            )
        elif (
            isinstance(child_node, TemplateNode)
            and child_node.template_name == "cf"
        ):
            return
        elif (
            isinstance(child_node, WikiNode)
            and child_node.kind == NodeKind.LINK
            and not inside_bracket
        ):
            linkage_data.word = clean_node(wxr, None, child_node)
        elif (
            isinstance(child_node, WikiNode)
            and child_node.kind == NodeKind.ITALIC
        ):
            italic_text = clean_node(wxr, None, child_node).strip("()")
            if italic_text == "":
                continue
            elif len(list(list_item.filter_empty_str_child())) == 1:
                linkage_data.word = italic_text
            elif italic_text.isdecimal():
                linkage_data.sense_index = int(italic_text)
            elif inside_bracket:
                linkage_data.raw_tags.append(italic_text)
            else:
                linkage_data.sense = italic_text
        elif (
            isinstance(child_node, TemplateNode)
            and child_node.template_name == "réf"
        ) or (
            isinstance(child_node, WikiNode)
            and child_node.kind == NodeKind.LIST
        ):
            continue
        else:
            tag_text = (
                child_node
                if isinstance(child_node, str)
                else clean_node(wxr, word_entry, child_node)
            )
            if (
                tag_text.strip() in {",", "/", "(ou"}
                and linkage_data.word != ""
            ):
                # list item has more than one word
                add_linkage_data(word_entry, linkage_type, linkage_data)
                linkage_data = Linkage(
                    word="",
                    tags=section_tags,
                    sense=sense,
                    sense_index=sense_index,
                )
                continue
            if tag_text.strip().startswith(
                "("
            ) and not tag_text.strip().endswith(")"):
                pending_tag = tag_text
                inside_bracket = True
                continue
            elif not tag_text.strip().startswith(
                "("
            ) and tag_text.strip().endswith(")"):
                tag_text = pending_tag + tag_text
                pending_tag = ""
                inside_bracket = False
            elif len(pending_tag) > 0:
                pending_tag += tag_text
                continue

            if tag_text.strip().startswith("—"):
                linkage_data.translation = clean_node(
                    wxr,
                    None,
                    list(list_item.invert_find_child(NodeKind.LIST, True))[
                        index:
                    ],
                ).strip("— \n")
                break
            elif tag_text.strip().startswith(":"):
                sense_text = tag_text.strip().removeprefix(":").strip()
                linkage_data.sense = sense_text
            else:
                tags, _ = capture_text_in_parentheses(tag_text)
                for tag in tags:
                    if tag.isdecimal():
                        linkage_data.sense_index = int(tag)
                    else:
                        linkage_data.raw_tags.append(tag)

    if len(linkage_data.word) > 0:
        add_linkage_data(word_entry, linkage_type, linkage_data)
    for child_list in list_item.find_child(NodeKind.LIST):
        for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(
                wxr,
                word_entry,
                child_list_item,
                linkage_type,
                section_tags,
                sense,
                sense_index,
            )


def add_linkage_data(
    word_entry: WordEntry, l_type: str, l_data: Linkage
) -> None:
    if l_data.word == "":
        return
    translate_raw_tags(l_data)
    if l_type == "forms":
        word_entry.forms.append(
            Form(
                form=l_data.word,
                tags=l_data.tags,
                raw_tags=l_data.raw_tags,
                roman=l_data.roman,
                sense=l_data.sense,
                sense_index=l_data.sense_index,
            )
        )
    else:
        getattr(word_entry, l_type).append(l_data)


def process_linkage_template(
    wxr: WiktextractContext, node: TemplateNode, linkage_data: Linkage
) -> None:
    if node.template_name in ["lien", "l"]:
        process_lien_template(wxr, node, linkage_data)
    elif node.template_name.startswith("zh-lien"):
        process_zh_lien_template(wxr, node, linkage_data)


def process_lien_template(
    wxr: WiktextractContext, node: TemplateNode, linkage_data: Linkage
) -> None:
    # link word template: https://fr.wiktionary.org/wiki/Modèle:lien
    ruby, without_ruby = extract_ruby(
        wxr,
        wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                node.template_parameters.get(
                    "dif", node.template_parameters.get(1)
                )
            ),
            expand_all=True,
        ),
    )
    linkage_data.word = clean_node(wxr, None, without_ruby)
    linkage_data.ruby = ruby
    linkage_data.roman = clean_node(
        wxr, None, node.template_parameters.get("tr", "")
    )
    linkage_data.translation = clean_node(
        wxr, None, node.template_parameters.get("sens", "")
    )


def process_zh_lien_template(
    wxr: WiktextractContext, node: TemplateNode, linkage_data: Linkage
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:zh-lien
    linkage_data.word = clean_node(wxr, None, node.template_parameters.get(1))
    linkage_data.roman = clean_node(
        wxr, None, node.template_parameters.get(2, "")
    )  # pinyin
    traditional_form = clean_node(
        wxr, None, node.template_parameters.get(3, "")
    )
    if len(traditional_form) > 0:
        linkage_data.alt = traditional_form


def process_voir_anagrammes_template(
    wxr: WiktextractContext, node: TemplateNode
) -> list[Linkage]:
    # https://fr.wiktionary.org/wiki/Modèle:voir_anagrammes
    results = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        for link_node in list_item.find_child(NodeKind.LINK):
            word = clean_node(wxr, None, link_node)
            if len(word) > 0:
                results.append(Linkage(word=word))
    return results


def extract_zh_l_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    raw_tags: list[str] = [],
    sense: str = "",
    sense_index: int = 0,
) -> list[Linkage]:
    # https://fr.wiktionary.org/wiki/Modèle:zh-l
    roman = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    new_sense = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
    if new_sense != "":
        sense = new_sense
    l_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value="zh"
    ):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            l_data = Linkage(
                word=word,
                sense=sense,
                sense_index=sense_index,
                raw_tags=raw_tags,
                roman=roman,
            )
            translate_raw_tags(l_data)
            l_list.append(l_data)
    if len(l_list) == 2:
        for index, l_data in enumerate(l_list):
            if index == 0:
                l_data.tags.append("Traditional-Chinese")
            else:
                l_data.tags.append("Simplified-Chinese")
    return l_list
