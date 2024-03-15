from typing import Optional, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import (
    capture_text_in_parentheses,
    split_chinese_variants,
    strip_nodes,
)
from .descendant import DESCENDANT_TEMPLATES, extract_descendant_list_item
from .models import Linkage, WordEntry
from .tags import translate_raw_tags


def extract_linkages(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    nodes: list[Union[WikiNode, str]],
    linkage_type: str,
    sense: str,
) -> Optional[str]:
    """
    Return linkage sense text for `sense` template inside a list item node.
    """
    strip_sense_chars = "()（）:："
    sense_template_names = {"s", "sense"}
    for node in strip_nodes(nodes):
        if isinstance(node, str) and len(sense) == 0:
            sense = node.strip(strip_sense_chars)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.LIST_ITEM:
                not_term_indexes = set()
                filtered_children = list(node.filter_empty_str_child())
                linkage_data = Linkage()
                for index, item_child in enumerate(filtered_children):
                    if (
                        isinstance(item_child, WikiNode)
                        and item_child.kind == NodeKind.TEMPLATE
                    ):
                        template_name = item_child.template_name
                        if template_name in sense_template_names:
                            not_term_indexes.add(index)
                            sense = clean_node(wxr, None, item_child).strip(
                                strip_sense_chars
                            )
                            if index == len(filtered_children) - 1:
                                # sense template before entry list
                                return sense
                        elif template_name in {"qualifier", "qual"}:
                            not_term_indexes.add(index)
                            linkage_data.raw_tags.append(
                                clean_node(wxr, None, item_child).strip("()")
                            )
                            translate_raw_tags(linkage_data)
                        elif template_name.lower() in DESCENDANT_TEMPLATES:
                            not_term_indexes.add(index)
                            extract_descendant_list_item(
                                wxr, node, page_data[-1]
                            )
                            break
                        elif template_name == "ja-r":
                            not_term_indexes.add(index)
                            process_ja_r_template(
                                wxr, page_data, item_child, linkage_type, sense
                            )

                if len(not_term_indexes) == len(filtered_children):
                    continue
                # sense template before entry and they are inside the same
                # list item
                terms = clean_node(
                    wxr,
                    None,
                    [
                        n
                        for n_index, n in enumerate(filtered_children)
                        if n_index not in not_term_indexes
                    ],
                )
                roman, terms = capture_text_in_parentheses(terms)
                roman = roman[0] if len(roman) > 0 else None
                if roman is not None:
                    linkage_data.roman = roman
                if len(sense) > 0:
                    linkage_data.sense = sense
                for term in terms.split("、"):
                    for variant_type, variant_term in split_chinese_variants(
                        term
                    ):
                        final_linkage_data = linkage_data.model_copy(deep=True)
                        final_linkage_data.word = variant_term
                        if variant_type is not None:
                            final_linkage_data.language_variant = variant_type
                        if len(final_linkage_data.word) > 0:
                            pre_data = getattr(page_data[-1], linkage_type)
                            pre_data.append(final_linkage_data)
            elif node.kind == NodeKind.TEMPLATE:
                template_name = node.template_name.lower()
                if template_name in sense_template_names:
                    sense = clean_node(wxr, None, node).strip(strip_sense_chars)
                elif template_name.endswith("-saurus"):
                    extract_saurus_template(
                        wxr, node, page_data, linkage_type, sense
                    )
                elif template_name == "zh-dial":
                    extract_zh_dial_template(
                        wxr, page_data, node, linkage_type, sense
                    )
                else:
                    expanded_node = wxr.wtp.parse(
                        wxr.wtp.node_to_wikitext(node), expand_all=True
                    )
                    extract_linkages(
                        wxr, page_data, [expanded_node], linkage_type, sense
                    )
            elif node.kind in LEVEL_KIND_FLAGS:
                from .page import parse_section

                base_data = WordEntry(
                    lang_code=page_data[-1].lang_code,
                    lang=page_data[-1].lang,
                    word=page_data[-1].word,
                    pos=page_data[-1].pos,
                )
                parse_section(wxr, page_data, base_data, node)
            elif len(node.children) > 0:
                returned_sense = extract_linkages(
                    wxr,
                    page_data,
                    node.children,
                    linkage_type,
                    sense,
                )
                if returned_sense is not None:
                    sense = returned_sense
    return None


def extract_saurus_template(
    wxr: WiktextractContext,
    node: WikiNode,
    page_data: list[WordEntry],
    linkage_type: str,
    sense: str,
) -> None:
    """
    Extract data from template names end with "-saurus", like "zh-syn-saurus"
    and "zh-ant-saurus". These templates get data from thesaurus pages, search
    the thesaurus database to avoid parse these pages again.
    """
    from wiktextract.thesaurus import search_thesaurus

    thesaurus_page_title = node.template_parameters.get(1)
    for thesaurus in search_thesaurus(
        wxr.thesaurus_db_conn,
        thesaurus_page_title,
        page_data[-1].lang_code,
        page_data[-1].pos,
        linkage_type,
    ):
        if thesaurus.term == wxr.wtp.title:
            continue
        linkage_data = Linkage(word=thesaurus.term)
        if thesaurus.roman is not None:
            linkage_data.roman = thesaurus.roman
        if thesaurus.tags is not None:
            linkage_data.raw_tags = thesaurus.tags.split("|")
        if thesaurus.language_variant is not None:
            linkage_data.language_variant = thesaurus.language_variant
        if len(sense) > 0:
            linkage_data.sense = sense
        elif thesaurus.sense is not None:
            linkage_data.sense = thesaurus.sense

        pre_data = getattr(page_data[-1], linkage_type)
        pre_data.append(linkage_data)


def extract_zh_dial_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    node: Union[WikiNode, str],
    linkage_type: str,
    sense: str,
) -> None:
    dial_data = {}
    node = wxr.wtp.parse(wxr.wtp.node_to_wikitext(node), expand_all=True)
    extract_zh_dial_recursively(wxr, node, dial_data, None)
    for term, tags in dial_data.items():
        linkage_data = Linkage(word=term)
        if len(sense) > 0:
            linkage_data.sense = sense
        if len(tags) > 0:
            linkage_data.raw_tags = tags
        pre_data = getattr(page_data[-1], linkage_type)
        pre_data.append(linkage_data)


def extract_zh_dial_recursively(
    wxr: WiktextractContext,
    node: Union[WikiNode, str],
    dial_data: dict[str, list[str]],
    header_lang: Optional[str],
) -> str:
    if isinstance(node, WikiNode) and node.kind == NodeKind.TABLE_ROW:
        tags = []
        for child in node.children:
            if isinstance(child, WikiNode):
                if child.kind == NodeKind.TABLE_HEADER_CELL:
                    header_lang = clean_node(wxr, None, child)
                    if header_lang == "註解":
                        return
                elif child.kind == NodeKind.TABLE_CELL:
                    tags.append(clean_node(wxr, None, child))
        if len(tags) < 1:  # table header
            return
        terms = tags[-1].removesuffix(" dated")
        tags = tags[:-1]
        if header_lang is not None:
            tags = [header_lang] + tags
        for term in terms.split("、"):
            if term == wxr.wtp.title:
                continue
            if term.endswith(" 比喻"):
                term = term.removesuffix(" 比喻")
                if "比喻" not in tags:
                    tags.append("比喻")
            old_tags = dial_data.get(term, [])
            old_tag_set = set(old_tags)
            new_tags = old_tags
            for tag in tags:
                if tag not in old_tag_set:
                    new_tags.append(tag)
            dial_data[term] = new_tags
    elif isinstance(node, WikiNode):
        for child in node.children:
            returned_lang = extract_zh_dial_recursively(
                wxr, child, dial_data, header_lang
            )
            if returned_lang is not None:
                header_lang = returned_lang
    return header_lang


def process_ja_r_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    linkage_type: str,
    sense: str,
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Ja-r
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    linkage_data = Linkage(sense=sense)
    for span_node in expanded_node.find_html("span"):
        if "lang" in span_node.attrs:
            ruby_data, no_ruby_nodes = extract_ruby(wxr, span_node)
            linkage_data.word = clean_node(wxr, None, no_ruby_nodes)
            linkage_data.ruby = ruby_data
        elif "tr" in span_node.attrs.get("class", ""):
            linkage_data.roman = clean_node(wxr, None, span_node)

    if len(linkage_data.word) > 0:
        pre_data = getattr(page_data[-1], linkage_type)
        pre_data.append(linkage_data)
