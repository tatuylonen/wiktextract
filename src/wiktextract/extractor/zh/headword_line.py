import re
from typing import Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import strip_nodes
from .models import Form, WordEntry
from .tags import TEMPLATE_TAG_ARGS, translate_raw_tags


def extract_headword_line(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    node: TemplateNode,
    lang_code: str,
) -> None:
    template_name = node.template_name
    if (
        template_name != "head"
        and not template_name.startswith(f"{lang_code}-")
    ) or template_name.endswith("-see"):
        return

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    forms_start_index = 0
    for span_node in expanded_node.find_html(
        "span", attr_name="class", attr_value="headword-line"
    ):
        for index, span_child in span_node.find_child(NodeKind.HTML, True):
            if span_child.tag == "span":
                forms_start_index = index + 1
                class_names = span_child.attrs.get("class", "")
                if "headword-tr" in class_names:
                    page_data[-1].forms.append(
                        Form(
                            form=clean_node(wxr, page_data[-1], span_child),
                            tags=["romanization"],
                        )
                    )
                elif "gender" in class_names:
                    for abbr_tag in span_child.find_html("abbr"):
                        gender = abbr_tag.children[0]
                        if gender in TEMPLATE_TAG_ARGS:
                            page_data[-1].tags.append(TEMPLATE_TAG_ARGS[gender])
                        else:
                            page_data[-1].raw_tags.append(gender)
                            translate_raw_tags(page_data[-1])
            elif (
                span_child.tag == "strong"
                and "headword" in span_child.attrs.get("class", "")
            ):
                forms_start_index = index + 1
                if lang_code == "ja":
                    ruby_data, node_without_ruby = extract_ruby(wxr, span_child)
                    page_data[-1].forms.append(
                        Form(
                            form=clean_node(
                                wxr, page_data[-1], node_without_ruby
                            ),
                            ruby=ruby_data,
                            tags=["canonical"],
                        )
                    )
            elif span_child.tag == "b":
                # this is a form <b> tag, already inside form parentheses
                break

        extract_headword_forms(
            wxr, page_data, span_node.children[forms_start_index:]
        )


def extract_headword_forms(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    form_nodes: list[Union[WikiNode, str]],
) -> None:
    current_nodes = []
    for node in form_nodes:
        if isinstance(node, str) and node.startswith("，"):
            process_forms_text(wxr, page_data, current_nodes)
            current_nodes = [node[1:]]
        else:
            current_nodes.append(node)

    if len(current_nodes) > 0:
        process_forms_text(wxr, page_data, current_nodes)


def process_forms_text(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    form_nodes: list[Union[WikiNode, str]],
) -> None:
    tag_nodes = []
    has_forms = False
    striped_nodes = list(strip_nodes(form_nodes))
    lang_code = page_data[-1].lang_code
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

                form_data = Form(
                    form=form,
                    raw_tags=raw_form_tags,
                    tags=form_tags,
                    ruby=ruby_data,
                )
                translate_raw_tags(form_data)
                page_data[-1].forms.append(form_data)
            elif (
                node.tag == "span"
                and "tr" in node.attrs.get("class", "")
                and len(page_data[-1].forms) > 0
            ):
                # romanization of the previous form <b> tag
                page_data[-1].forms[-1].roman = clean_node(wxr, None, node)
            else:
                tag_nodes.append(node)
        else:
            tag_nodes.append(node)

    if not has_forms:
        tags_list = extract_headword_tags(
            clean_node(wxr, page_data[-1], tag_nodes).strip("() ")
        )
        if len(tags_list) > 0:
            page_data[-1].raw_tags.extend(tags_list)
            translate_raw_tags(page_data[-1])
    else:
        clean_node(wxr, page_data[-1], tag_nodes)  # find categories


def extract_headword_tags(tags_str: str) -> list[str]:
    tags = []
    for tag_str in (
        s.strip() for s in re.split("&|或|和", tags_str) if len(s.strip()) > 0
    ):
        tags.append(tag_str)
    return tags
