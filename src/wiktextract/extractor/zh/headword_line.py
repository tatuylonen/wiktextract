import re
from typing import Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import strip_nodes
from .models import Form, WordEntry

# https://zh.wiktionary.org/wiki/Module:Gender_and_number
GENDERS = {
    "f": "feminine",
    "m": "masculine",
    "n": "neuter",
    "c": "common",
    # Animacy
    "an": "animate",
    "in": "inanimate",
    # Animal (for Ukrainian, Belarusian, Polish)
    "anml": "animal",
    # Personal (for Ukrainian, Belarusian, Polish)
    "pr": "personal",
    # Nonpersonal not currently used
    "np": "nonpersonal",
    # Virility (for Polish)
    "vr": "virile",
    "nv": "nonvirile",
    # Numbers
    "s": "singular number",
    "d": "dual number",
    "p": "plural number",
    # Verb qualifiers
    "impf": "imperfective aspect",
    "pf": "perfective aspect",
}


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
    for index, child in expanded_node.find_child(NodeKind.HTML, True):
        if child.tag == "strong" and "headword" in child.attrs.get("class", ""):
            forms_start_index = index + 1
        elif child.tag == "span":
            class_names = child.attrs.get("class", "")
            if "headword-tr" in class_names:
                forms_start_index = index + 1

                page_data[-1].forms.append(
                    Form(
                        form=clean_node(wxr, page_data[-1], child),
                        tags=["romanization"],
                    )
                )
            elif "gender" in class_names:
                forms_start_index = index + 1
                for abbr_tag in child.find_html("abbr"):
                    gender = abbr_tag.children[0]
                    page_data[-1].tags.append(GENDERS.get(gender, gender))
            if lang_code == "ja":
                for span_child in child.find_html(
                    "strong", attr_name="class", attr_value="headword"
                ):
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
        elif child.tag == "b":
            # this is a form <b> tag, already inside form parentheses
            break

    extract_headword_forms(
        wxr, page_data, expanded_node.children[forms_start_index:]
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
                form_tags = extract_headword_tags(
                    clean_node(wxr, None, tag_nodes).strip("() ")
                )
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
                        form_tags.append(GENDERS.get(gender, gender))

                form_data = Form(form=form, tags=form_tags, ruby=ruby_data)
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
            page_data[-1].tags.extend(tags_list)
    else:
        clean_node(wxr, page_data[-1], tag_nodes)  # find categories


def extract_headword_tags(tags_str: str) -> list[str]:
    tags = []
    for tag_str in (
        s.strip() for s in re.split("&|或", tags_str) if len(s.strip()) > 0
    ):
        tags.append(tag_str)
    return tags
