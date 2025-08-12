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
from ..ruby import extract_ruby
from .models import Form, Linkage, WordEntry
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
            elif re.fullmatch(
                r"(?:col|der|rel)\d", node.template_name, re.I
            ) or node.template_name.endswith("-saurus"):
                linkage_list.extend(
                    process_linkage_col_template(wxr, node, sense)
                )
            elif node.template_name == "ja-r/multi":
                linkage_list.extend(
                    extract_ja_r_multi_template(wxr, node, sense)
                )

    if linkage_type == "alt_forms":
        forms = [
            Form(
                form=l_data.word,
                sense=l_data.sense,
                tags=l_data.tags + ["alternative"],
                raw_tags=l_data.raw_tags,
                roman=l_data.roman,
                ruby=l_data.ruby,
                attestations=l_data.attestations,
            )
            for l_data in linkage_list
        ]
        page_data[-1].forms.extend(forms)
    else:
        getattr(page_data[-1], linkage_type).extend(linkage_list)
        for data in page_data[:-1]:
            if (
                data.lang_code == page_data[-1].lang_code
                and data.sounds == page_data[-1].sounds
                and data.etymology_text == page_data[-1].etymology_text
                and data.pos_level == page_data[-1].pos_level == level_node.kind
            ):
                getattr(data, linkage_type).extend(linkage_list)


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
            elif item_child.template_name.lower() in [
                "l",
                "link",
                "alter",
                "alt",
            ]:
                linkage_list.extend(
                    process_l_template(wxr, item_child, sense, raw_tags)
                )
                raw_tags.clear()
            elif (
                item_child.template_name.lower() in ["defdate", "datedef"]
                and len(linkage_list) > 0
            ):
                from .gloss import extract_defdate_template

                extract_defdate_template(wxr, linkage_list[-1], item_child)
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
        elif (
            isinstance(item_child, WikiNode)
            and item_child.kind == NodeKind.LIST
        ):
            for child_list_item in item_child.find_child(NodeKind.LIST_ITEM):
                _, new_list = process_linkage_list_item(
                    wxr, child_list_item, sense
                )
                linkage_list.extend(new_list)

    return sense, linkage_list


def extract_zh_dial_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: str
) -> list[Linkage]:
    from .pronunciation import split_zh_pron_raw_tag

    linkage_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_node in expanded_node.find_child_recursively(NodeKind.TABLE):
        is_note_row = False
        note_tags = {}
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            for cell_node in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    is_note_row = clean_node(wxr, None, cell_node) == "註解"
                elif is_note_row:
                    for note_str in clean_node(wxr, None, cell_node).split(";"):
                        if "-" in note_str:
                            note_symbol, note = note_str.split("-", maxsplit=1)
                            note_symbol = note_symbol.strip()
                            note = note.strip()
                            if note_symbol != "" and note != "":
                                note_tags[note_symbol] = note
        lang_tags = []
        region_tags = []
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            if not row_node.contain_node(NodeKind.TABLE_CELL):
                continue  # skip header row
            for header_node in row_node.find_child(NodeKind.TABLE_HEADER_CELL):
                lang_tags = split_zh_pron_raw_tag(
                    clean_node(wxr, None, header_node)
                )
            if lang_tags == ["註解"]:  # skip last note row
                continue
            for cell_node in row_node.find_child(NodeKind.TABLE_CELL):
                for link_node in cell_node.find_child(NodeKind.LINK):
                    region_tags = split_zh_pron_raw_tag(
                        clean_node(wxr, None, link_node)
                    )
                for span_tag in cell_node.find_html("span"):
                    span_text = clean_node(wxr, None, span_tag)
                    if span_text == "":
                        continue
                    if (
                        span_tag.attrs.get("lang", "") == "zh"
                        and span_text != wxr.wtp.title
                    ):
                        l_data = Linkage(word=span_text)
                        if len(lang_tags) > 0:
                            l_data.raw_tags.extend(lang_tags)
                        if len(region_tags) > 0:
                            l_data.raw_tags.extend(region_tags)
                        translate_raw_tags(l_data)
                        linkage_list.append(l_data)
                    elif (
                        span_tag.attrs.get("style", "") == "font-size:60%"
                        and len(linkage_list) > 0
                    ):
                        for note_symbol in span_text.split(","):
                            note_symbol = note_symbol.strip()
                            raw_tag = note_symbol
                            if note_symbol in note_tags:
                                raw_tag = note_tags[note_symbol]
                            if raw_tag != "":
                                linkage_list[-1].raw_tags.append(raw_tag)
                                translate_raw_tags(linkage_list[-1])

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
            linkage_data.tags.append("Traditional-Chinese")
        elif lang_attr == "zh-Hans":
            linkage_data.tags.append("Simplified-Chinese")
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
    return process_expanded_ja_r_node(wxr, expanded_node, sense, raw_tags)


def process_expanded_ja_r_node(
    wxr: WiktextractContext,
    expanded_node: WikiNode,
    sense: str,
    raw_tags: list[str] = [],
) -> Linkage:
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
    t_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:l
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    linkage_list = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "")
        if span_lang == lang_code:
            linkage_data = Linkage(
                sense=sense,
                raw_tags=raw_tags,
                word=clean_node(wxr, None, span_tag),
            )
            if len(linkage_data.word) > 0:
                translate_raw_tags(linkage_data)
                linkage_list.append(linkage_data)
        elif span_lang.endswith("-Latn") and len(linkage_list) > 0:
            linkage_list[-1].roman = clean_node(wxr, None, span_tag)
        elif "mention-gloss" == span_class and len(linkage_list) > 0:
            linkage_list[-1].sense = clean_node(wxr, None, span_tag)

    return linkage_list


def process_linkage_col_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: str
) -> list[Linkage]:
    # https://zh.wiktionary.org/wiki/Template:Col3
    linkage_list = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for ui_tag in expanded_template.find_html_recursively("li"):
        current_data = []
        roman = ""
        raw_tags = []
        for span_tag in ui_tag.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            if span_lang.endswith("-Latn"):
                roman = clean_node(wxr, None, span_tag)
            elif "qualifier-content" in span_tag.attrs.get("class", ""):
                span_text = clean_node(wxr, None, span_tag)
                for raw_tag in re.split(r"或|、", span_text):
                    raw_tag = raw_tag.strip()
                    if raw_tag != "":
                        raw_tags.append(raw_tag)
            elif span_lang != "":
                l_data = Linkage(
                    word=clean_node(wxr, None, span_tag), sense=sense
                )
                class_names = span_tag.attrs.get("class", "")
                if class_names == "Hant":
                    l_data.tags.append("Traditional-Chinese")
                elif class_names == "Hans":
                    l_data.tags.append("Simplified-Chinese")
                if l_data.word != "":
                    current_data.append(l_data)

        for data in current_data:
            data.raw_tags.extend(raw_tags)
            data.roman = roman
            translate_raw_tags(data)
        linkage_list.extend(current_data)

    return linkage_list


def process_linkage_templates_in_gloss(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    sense: str,
) -> None:
    # https://en.wiktionary.org/wiki/Template:synonyms
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    l_list = []
    raw_tags = []
    for top_span_tag in expanded_node.find_html("span"):
        for node in top_span_tag.children:
            if isinstance(node, HTMLNode) and node.tag == "span":
                span_lang = node.attrs.get("lang", "")
                span_class = node.attrs.get("class", "")
                if span_lang == lang_code:
                    l_data = Linkage(
                        word=clean_node(wxr, None, node),
                        sense=sense,
                        raw_tags=raw_tags,
                    )
                    if span_class == "Hant":
                        l_data.tags.append("Traditional-Chinese")
                    elif span_class == "Hans":
                        l_data.tags.append("Simplified-Chinese")
                    if l_data.word != "":
                        l_list.append(l_data)
                elif span_lang == f"{lang_code}-Latn" or "tr" in span_class:
                    roman = clean_node(wxr, None, node)
                    for d in l_list:
                        d.roman = roman
                elif span_class == "mention-gloss":
                    sense = clean_node(wxr, None, node)
                    for d in l_list:
                        d.sense = sense
                elif "qualifier-content" in span_class:
                    raw_tag_str = clean_node(wxr, None, node)
                    for raw_tag in raw_tag_str.split("，"):
                        raw_tag = raw_tag.strip()
                        if raw_tag != "":
                            raw_tags.append(raw_tag)
            elif isinstance(node, str) and node.strip() == "、":
                getattr(word_entry, linkage_type).extend(l_list)
                l_list.clear()

    getattr(word_entry, linkage_type).extend(l_list)
    for data in getattr(word_entry, linkage_type):
        translate_raw_tags(data)


def extract_ja_r_multi_template(
    wxr: WiktextractContext, template_node: TemplateNode, sense: str
) -> Linkage:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    linkage_list = []
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            linkage_list.append(
                process_expanded_ja_r_node(wxr, list_item, sense, [])
            )

    return linkage_list
