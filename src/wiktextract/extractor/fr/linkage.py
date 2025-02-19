import re

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import capture_text_in_parentheses
from .models import Form, Linkage, WordEntry
from .section_types import LINKAGE_SECTIONS, LINKAGE_TAGS
from .tags import translate_raw_tags


def extract_linkage(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    section_type: str,
) -> None:
    if section_type == "dérivés autres langues":
        process_derives_autres_list(wxr, page_data, level_node)
    elif section_type == "anagrammes":
        for node in level_node.find_child(NodeKind.TEMPLATE):
            if node.template_name == "voir anagrammes":
                anagram_list = process_voir_anagrammes_template(wxr, node)
                for data in page_data:
                    if data.lang_code == page_data[-1].lang_code:
                        data.anagrams.extend(anagram_list)
    else:
        process_linkage_list(
            wxr,
            page_data,
            level_node,
            LINKAGE_SECTIONS[section_type],
            LINKAGE_TAGS.get(section_type, []),
        )


def process_derives_autres_list(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
):
    # drrive to other languages list
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        lang_code = ""
        lang_name = ""
        for node in list_item.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
            if isinstance(node, TemplateNode) and node.template_name == "L":
                lang_code = node.template_parameters.get(1)
                lang_name = clean_node(wxr, None, node)
            elif node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                page_data[-1].derived.append(
                    Linkage(lang_code=lang_code, lang=lang_name, word=word)
                )
            elif isinstance(node, TemplateNode) and node.template_name in [
                "l",
                "lien",
                "zh-lien",
                "zh-lien-t",
            ]:
                linkage_data = Linkage(
                    lang_code=lang_code, lang=lang_name, word=""
                )
                process_linkage_template(wxr, node, linkage_data)
                page_data[-1].derived.append(linkage_data)


def process_linkage_list(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    linkage_type: str,
    section_tags: list[str] = [],
) -> None:
    sense_text = ""
    sense_index = 0
    for template_or_list_node in level_node.find_child_recursively(
        NodeKind.LIST_ITEM | NodeKind.TEMPLATE
    ):
        # list table start template: https://fr.wiktionary.org/wiki/Modèle:(
        if (
            isinstance(template_or_list_node, TemplateNode)
            and template_or_list_node.template_name == "("
        ):
            sense_text = clean_node(
                wxr, None, template_or_list_node.template_parameters.get(1, "")
            )
            sense_index_text = template_or_list_node.template_parameters.get(
                2, "0"
            )
            if (
                isinstance(sense_index_text, str)
                and sense_index_text.isdecimal()
            ):
                sense_index = int(sense_index_text)
            continue
        # sense could also be in ";" description list
        if (
            template_or_list_node.kind == NodeKind.LIST_ITEM
            and template_or_list_node.sarg in {";", ":"}
        ):
            sense_text = clean_node(wxr, None, template_or_list_node.children)
            index_pattern = r"\s*\((?:sens\s*)?(\d+)\)$"
            m = re.search(index_pattern, sense_text)
            if m is not None:
                sense_text = re.sub(index_pattern, "", sense_text)
                sense_index = int(m.group(1))
            continue

        linkage_data = Linkage(word="", tags=section_tags)
        if len(sense_text) > 0:
            linkage_data.sense = sense_text
        if sense_index != 0:
            linkage_data.sense_index = sense_index
        pending_tag = ""
        inside_bracket = False
        for index, child_node in enumerate(  # remove nested lists
            template_or_list_node.invert_find_child(NodeKind.LIST, True)
        ):
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
                isinstance(child_node, WikiNode)
                and child_node.kind == NodeKind.LINK
                and not inside_bracket
            ):
                linkage_data.word = clean_node(wxr, None, child_node)
            elif (
                isinstance(child_node, WikiNode)
                and child_node.kind == NodeKind.ITALIC
            ):
                current_sense = clean_node(wxr, None, child_node).strip("()")
                if (
                    len(list(template_or_list_node.filter_empty_str_child()))
                    == 1
                ):
                    linkage_data.word = current_sense
                elif current_sense.isdecimal():
                    linkage_data.sense_index = int(current_sense)
                else:
                    linkage_data.sense = current_sense
            elif (
                isinstance(child_node, TemplateNode)
                and child_node.template_name == "réf"
            ):
                continue
            else:
                tag_text = (
                    child_node
                    if isinstance(child_node, str)
                    else clean_node(wxr, page_data[-1], child_node)
                )
                if (
                    tag_text.strip() in {",", "/", "(ou"}
                    and linkage_data.word != ""
                ):
                    # list item has more than one word
                    add_linkage_data(page_data[-1], linkage_type, linkage_data)
                    linkage_data = Linkage(word="", tags=section_tags)
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
                        list(
                            template_or_list_node.invert_find_child(
                                NodeKind.LIST, True
                            )
                        )[index:],
                    ).strip("— ")
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
            add_linkage_data(page_data[-1], linkage_type, linkage_data)


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
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
) -> None:
    if node.template_name in ["lien", "l"]:
        process_lien_template(wxr, node, linkage_data)
    elif node.template_name.startswith("zh-lien"):
        process_zh_lien_template(wxr, node, linkage_data)


def process_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
) -> None:
    # link word template: https://fr.wiktionary.org/wiki/Modèle:lien
    word = clean_node(
        wxr,
        None,
        node.template_parameters.get("dif", node.template_parameters.get(1)),
    )
    linkage_data.word = word
    if "tr" in node.template_parameters:
        linkage_data.roman = clean_node(
            wxr, None, node.template_parameters.get("tr")
        )
    if "sens" in node.template_parameters:
        linkage_data.translation = clean_node(
            wxr, None, node.template_parameters.get("sens")
        )


def process_zh_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
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
