import itertools
from collections import defaultdict

from wikitextprocessor.parser import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Linkage, WordEntry
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    sense = ""
    linkage_list = []
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        if node.kind == NodeKind.LIST:
            for item_node in node.find_child(NodeKind.LIST_ITEM):
                sense, new_linkage_list = process_linkage_list_item(
                    wxr, item_node, sense
                )
                linkage_list.extend(new_linkage_list)
        elif isinstance(node, TemplateNode):
            if node.template_name in ["s", "sense"]:
                sense = clean_node(wxr, None, node).strip("()： ")
            elif node.template_name == "zh-dial":
                linkage_list.extend(extract_zh_dial_template(wxr, node, sense))
            elif node.template_name.endswith("-saurus"):
                linkage_list.extend(
                    extract_saurus_template(
                        wxr, page_data, node, linkage_type, sense
                    )
                )
            elif node.template_name.startswith("col"):
                linkage_list.extend(
                    process_linkage_col_template(wxr, node, sense)
                )

    if level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                pre_linkage_list = getattr(data, linkage_type)
                pre_linkage_list.extend(linkage_list)
    elif len(page_data) > 0:
        pre_linkage_list = getattr(page_data[-1], linkage_type)
        pre_linkage_list.extend(linkage_list)


def process_linkage_list_item(
    wxr: WiktextractContext, list_item: WikiNode, sense: str
) -> tuple[str, list[Linkage]]:
    raw_tags = []
    linkage_list = []
    for item_child in list_item.children:
        if isinstance(item_child, TemplateNode):
            if item_child.template_name in ["s", "sense"]:
                sense = clean_node(wxr, None, item_child).strip("()： ")
            elif item_child.template_name in ["qualifier", "qual"]:
                raw_tags.append(clean_node(wxr, None, item_child).strip("()"))
            elif item_child.template_name == "zh-l":
                linkage_list.extend(
                    process_zh_l_template(wxr, item_child, sense, raw_tags)
                )
                raw_tags.clear()
            elif item_child.template_name == "ja-r":
                linkage_list.append(
                    process_ja_r_template(wxr, item_child, sense, raw_tags)
                )
                raw_tags.clear()
            elif item_child.template_name in ["l", "link", "alter"]:
                linkage_list.extend(
                    process_l_template(wxr, item_child, sense, raw_tags)
                )
                raw_tags.clear()
        elif (
            isinstance(item_child, WikiNode)
            and item_child.kind == NodeKind.LINK
        ):
            word = clean_node(wxr, None, item_child)
            if len(word) > 0:
                linkage_data = Linkage(
                    word=word, sense=sense, raw_tags=raw_tags
                )
                translate_raw_tags(linkage_data)
                linkage_list.append(linkage_data)
                raw_tags.clear()
    return sense, linkage_list


def extract_saurus_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    node: TemplateNode,
    linkage_type: str,
    sense: str,
) -> list[Linkage]:
    """
    Extract data from template names end with "-saurus", like "zh-syn-saurus"
    and "zh-ant-saurus". These templates get data from thesaurus pages, search
    the thesaurus database to avoid parse these pages again.

    https://zh.wiktionary.org/wiki/Template:Syn-saurus
    """
    from wiktextract.thesaurus import search_thesaurus

    linkage_data = []
    if node.template_name in ("zh-syn-saurus", "zh-ant-saurus"):
        # obsolete templates
        thesaurus_page_title = node.template_parameters.get(1)
    else:
        thesaurus_page_title = node.template_parameters.get(2)

    for thesaurus in search_thesaurus(
        wxr.thesaurus_db_conn,
        thesaurus_page_title,
        page_data[-1].lang_code,
        page_data[-1].pos,
        linkage_type,
    ):
        if thesaurus.term == wxr.wtp.title:
            continue
        linkage_data.append(
            Linkage(
                word=thesaurus.term,
                roman=thesaurus.roman,
                tags=thesaurus.tags,
                raw_tags=thesaurus.raw_tags,
                sense=sense,
            )
        )

    return linkage_data


def extract_zh_dial_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: str
) -> list[Linkage]:
    linkage_list = []
    dial_data = defaultdict(set)
    tag_data = defaultdict(set)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_node in expanded_node.find_child_recursively(NodeKind.TABLE):
        lang_tag = ""
        region_tag = ""
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            if not row_node.contain_node(NodeKind.TABLE_CELL):
                continue  # skip header row
            for header_node in row_node.find_child(NodeKind.TABLE_HEADER_CELL):
                lang_tag = clean_node(wxr, None, header_node)
            if lang_tag == "註解":  # skip last note row
                continue
            for cell_node in row_node.find_child(NodeKind.TABLE_CELL):
                for link_node in cell_node.find_child(NodeKind.LINK):
                    region_tag = clean_node(wxr, None, link_node)
                word = ""
                for span_tag in cell_node.find_html("span"):
                    span_text = clean_node(wxr, None, span_tag)
                    if span_text == "":
                        continue
                    if (
                        span_tag.attrs.get("lang", "") == "zh"
                        and span_text != wxr.wtp.title
                    ):
                        word = span_text
                        if lang_tag != "":
                            dial_data[span_text].add(lang_tag)
                        if region_tag != "":
                            dial_data[span_text].add(region_tag)
                    elif (
                        span_tag.attrs.get("style", "") == "font-size:60%"
                        and word != ""
                    ):
                        tag_data[word].add(span_text)

    for term, lang_tags in dial_data.items():
        linkage_data = Linkage(word=term, sense=sense, raw_tags=list(lang_tags))
        linkage_data.raw_tags.extend(list(tag_data.get(term, {})))
        translate_raw_tags(linkage_data)
        linkage_list.append(linkage_data)
    return linkage_list


def process_zh_l_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> list[Linkage]:
    # https://zh.wiktionary.org/wiki/Template:Zh-l
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    roman = ""
    linkage_list = []
    for i_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="Latn"
    ):
        roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value="zh"
    ):
        linkage_data = Linkage(
            sense=sense,
            raw_tags=raw_tags,
            roman=roman,
            word=clean_node(wxr, None, span_tag),
        )
        lang_attr = span_tag.attrs.get("lang", "")
        if lang_attr == "zh-Hant":
            linkage_data.tags.append("Traditional Chinese")
        elif lang_attr == "zh-Hans":
            linkage_data.tags.append("Simplified Chinese")
        if len(linkage_data.word) > 0 and linkage_data.word != "／":
            translate_raw_tags(linkage_data)
            linkage_list.append(linkage_data)
    return linkage_list


def process_ja_r_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> Linkage:
    # https://zh.wiktionary.org/wiki/Template:Ja-r
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    linkage_data = Linkage(sense=sense, raw_tags=raw_tags)
    for span_node in expanded_node.find_html("span"):
        span_class = span_node.attrs.get("class", "")
        if "lang" in span_node.attrs:
            ruby_data, no_ruby_nodes = extract_ruby(wxr, span_node)
            linkage_data.word = clean_node(wxr, None, no_ruby_nodes)
            linkage_data.ruby = ruby_data
        elif "tr" in span_class:
            linkage_data.roman = clean_node(wxr, None, span_node)
        elif "mention-gloss" == span_class:
            linkage_data.sense = clean_node(wxr, None, span_node)

    translate_raw_tags(linkage_data)
    return linkage_data


def process_l_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:l
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    linkage_list = []
    for span_tag in expanded_node.find_html("span", attr_name="lang"):
        linkage_data = Linkage(
            sense=sense, raw_tags=raw_tags, word=clean_node(wxr, None, span_tag)
        )
        if len(linkage_data.word) > 0:
            translate_raw_tags(linkage_data)
            linkage_list.append(linkage_data)
    return linkage_list


def process_linkage_col_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: str
) -> list[Linkage]:
    from .thesaurus import process_col_template

    linkage_list = []
    for data in process_col_template(wxr, "", "", "", "", "", template_node):
        linkage_data = Linkage(
            word=data.term,
            roman=data.roman,
            tags=data.tags,
            raw_tags=data.raw_tags,
            sense=sense,
        )
        if len(linkage_data.word) > 0:
            translate_raw_tags(linkage_data)
            linkage_list.append(linkage_data)
    return linkage_list


def process_linkage_templates_in_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
    linkage_type: str,
    sense: str,
) -> None:
    for word_index in itertools.count(2):
        if word_index not in template_node.template_parameters:
            break
        word = clean_node(
            wxr, None, template_node.template_parameters[word_index]
        )
        if len(word) == 0:
            continue
        if word.startswith(wxr.wtp.NAMESPACE_DATA["Thesaurus"]["name"] + ":"):
            continue
        linkage = Linkage(word=word, sense=sense)
        pre_data = getattr(page_data[-1], linkage_type)
        pre_data.append(linkage)
