import re

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import strip_nodes
from .models import Form, WordEntry
from .tags import TEMPLATE_TAG_ARGS, translate_raw_tags


def extract_pos_head_line_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    is_first_bold = True
    for node in nodes:
        if isinstance(node, TemplateNode):
            if node.template_name in ["tlb", "term-label"]:
                extract_tlb_template(wxr, word_entry, node)
            else:
                extract_headword_line_template(wxr, word_entry, node)
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.BOLD
            and is_first_bold
        ):
            process_headword_bold_node(wxr, word_entry, node)
            is_first_bold = False


def extract_headword_line_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # handle the first template in header line
    template_name = t_node.template_name
    if (
        template_name != "head"
        and not template_name.startswith(f"{word_entry.lang_code}-")
    ) or template_name.endswith("-see"):
        return

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    clean_node(wxr, word_entry, expanded_node)
    forms_start_index = 0
    for span_node in expanded_node.find_html(
        "span", attr_name="class", attr_value="headword-line"
    ):
        for index, span_child in span_node.find_child(NodeKind.HTML, True):
            if span_child.tag == "span":
                forms_start_index = index + 1
                class_names = span_child.attrs.get("class", "").split()
                if "headword-tr" in class_names:
                    form = clean_node(wxr, word_entry, span_child)
                    if form != "":
                        word_entry.forms.append(
                            Form(form=form, tags=["romanization"])
                        )
                elif "gender" in class_names:
                    for abbr_tag in span_child.find_html("abbr"):
                        gender = clean_node(wxr, None, abbr_tag)
                        if gender in TEMPLATE_TAG_ARGS:
                            word_entry.tags.append(TEMPLATE_TAG_ARGS[gender])
                        else:
                            word_entry.raw_tags.append(gender)
                            translate_raw_tags(word_entry)
                elif "ib-content" in class_names:
                    raw_tag = clean_node(wxr, None, span_child)
                    if raw_tag != "":
                        word_entry.raw_tags.append(raw_tag)
                        translate_raw_tags(word_entry)
                else:
                    for strong_node in span_child.find_html(
                        "strong", attr_name="class", attr_value="headword"
                    ):
                        process_headword_bold_node(wxr, word_entry, strong_node)
            elif (
                span_child.tag == "strong"
                and "headword" in span_child.attrs.get("class", "")
            ):
                forms_start_index = index + 1
                process_headword_bold_node(wxr, word_entry, span_child)
            elif span_child.tag == "b":
                # this is a form <b> tag, already inside form parentheses
                break

        extract_headword_forms(
            wxr, word_entry, span_node.children[forms_start_index:]
        )


def process_headword_bold_node(
    wxr: WiktextractContext, word_entry: WordEntry, strong_node: HTMLNode
) -> None:
    ruby_data, node_without_ruby = extract_ruby(wxr, strong_node)
    form = clean_node(wxr, word_entry, node_without_ruby)
    if (len(ruby_data) > 0 or form != word_entry.word) and len(form) > 0:
        if wxr.wtp.title.startswith("不支援的頁面名稱/"):
            # Unsupported titles:
            # https://zh.wiktionary.org/wiki/Appendix:不支援的頁面名稱
            # https://zh.wiktionary.org/wiki/Special:PrefixIndex/不支援的頁面名稱
            word_entry.word = form
            word_entry.original_title = wxr.wtp.title
        else:
            word_entry.forms.append(
                Form(
                    form=clean_node(wxr, word_entry, node_without_ruby),
                    ruby=ruby_data,
                    tags=["canonical"],
                )
            )


def extract_headword_forms(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    form_nodes: list[WikiNode | str],
) -> None:
    current_nodes = []
    for node in form_nodes:
        if isinstance(node, str) and node.startswith(("，", ",")):
            process_forms_text(wxr, word_entry, current_nodes)
            current_nodes = [node[1:]]
        else:
            current_nodes.append(node)

    if len(current_nodes) > 0:
        process_forms_text(wxr, word_entry, current_nodes)


def process_forms_text(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    form_nodes: list[WikiNode | str],
) -> None:
    tag_nodes = []
    has_forms = False
    striped_nodes = list(strip_nodes(form_nodes))
    lang_code = word_entry.lang_code
    for index, node in enumerate(striped_nodes):
        if isinstance(node, WikiNode) and node.kind == NodeKind.HTML:
            if node.tag == "b":
                has_forms = True
                ruby_data = []
                if lang_code == "ja":
                    ruby_data, node_without_ruby = extract_ruby(wxr, node)
                    form = clean_node(wxr, None, node_without_ruby)
                else:
                    form = clean_node(wxr, None, node)
                raw_form_tags = extract_headword_tags(
                    clean_node(wxr, None, tag_nodes).strip("() ")
                )
                form_tags = []
                # check if next tag has gender data
                if index < len(striped_nodes) - 1:
                    next_node = striped_nodes[index + 1]
                    if (
                        isinstance(next_node, WikiNode)
                        and next_node.kind == NodeKind.HTML
                        and next_node.tag == "span"
                        and "gender" in next_node.attrs.get("class", "")
                    ):
                        gender = clean_node(wxr, None, next_node)
                        if gender in TEMPLATE_TAG_ARGS:
                            form_tags.append(TEMPLATE_TAG_ARGS[gender])
                        else:
                            raw_form_tags.append(gender)

                for f_str in form.split("／"):
                    f_str = f_str.strip()
                    if f_str == "":
                        continue
                    form_data = Form(
                        form=f_str,
                        raw_tags=raw_form_tags,
                        tags=form_tags,
                        ruby=ruby_data,
                    )
                    translate_raw_tags(form_data)
                    word_entry.forms.append(form_data)
            elif (
                node.tag == "span"
                and "tr" in node.attrs.get("class", "")
                and len(word_entry.forms) > 0
            ):
                # romanization of the previous form <b> tag
                word_entry.forms[-1].roman = clean_node(wxr, None, node)
            elif node.tag == "sup" and lang_code == "ja":
                extract_historical_kana(wxr, word_entry, node)
            else:
                tag_nodes.append(node)
        else:
            tag_nodes.append(node)

    if not has_forms:
        tags_list = extract_headword_tags(
            clean_node(wxr, word_entry, tag_nodes).strip("() ")
        )
        if len(tags_list) > 0:
            word_entry.raw_tags.extend(tags_list)
            translate_raw_tags(word_entry)


def extract_headword_tags(tags_str: str) -> list[str]:
    tags = []
    for tag_str in filter(
        None, (s.strip() for s in re.split("&|或|和", tags_str))
    ):
        tags.append(tag_str)
    return tags


def extract_historical_kana(
    wxr: WiktextractContext, word_entry: WordEntry, sup_node: HTMLNode
) -> None:
    # https://zh.wiktionary.org/wiki/Template:ja-adj
    # "hist" parameter
    form = ""
    roman = ""
    for strong_node in sup_node.find_html("strong"):
        form = clean_node(wxr, None, strong_node)
    for span_node in sup_node.find_html(
        "span", attr_name="class", attr_value="tr"
    ):
        roman = clean_node(wxr, None, span_node).strip("()")
    if len(form) > 0:
        form_data = Form(form=form, roman=roman)
        word_entry.forms.append(form_data)


def extract_tlb_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Tlb
    # https://en.wiktionary.org/wiki/Template:term-label
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="ib-content"
    ):
        for raw_tag in clean_node(wxr, None, span_tag).split("，"):
            raw_tag = raw_tag.strip()
            if len(raw_tag) > 0:
                word_entry.raw_tags.append(raw_tag)
    clean_node(wxr, word_entry, expanded_node)
    translate_raw_tags(word_entry)
