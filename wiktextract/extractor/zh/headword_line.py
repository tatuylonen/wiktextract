import re
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import strip_nodes

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


FORM_TAGS = {
    "不可數": ["uncountable"],
    "通常不可數": ["uncountable"],
    "可數": ["countable"],
    "複數": ["plural"],
    # en-verb
    "第三人稱單數簡單現在時": ["third-person", "singular", "simple", "present"],
    "現在分詞": ["present", "participle"],
    "一般過去時及過去分詞": ["past", "participle"],
    # fr-noun, fr-adj
    # https://zh.wiktionary.org/wiki/Module:Fr-headword
    "指小詞": ["diminutive"],
    "陰性": ["feminine"],
    "陽性": ["masculine"],
    "陽性複數": ["masculine", "plural"],
    "陰性複數": ["feminine", "plural"],
    "陽性單數": ["masculine", "singular"],
    "元音前陽性單數": ["masculine", "singular", "before-vowel"],
    "比較級": ["comparative"],
    "最高級": ["superlative"],
    # voice
    "主動": ["active"],
    "被動": ["passive"],
    "及物": ["transitive"],
    "不規則": ["irregular"],
}


def extract_headword_line(
    wxr: WiktextractContext,
    page_data: List[Dict],
    node: WikiNode,
    lang_code: str,
) -> None:
    template_name = node.largs[0][0]
    if template_name != "head" and not template_name.startswith(
        f"{lang_code}-"
    ):
        return

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    forms_start_index = 0
    for index, child in enumerate(expanded_node.children):
        if isinstance(child, WikiNode) and child.kind == NodeKind.HTML:
            if child.sarg == "strong" and "headword" in child.attrs.get(
                "class", ""
            ):
                forms_start_index = index + 1
            elif child.sarg == "span":
                class_names = child.attrs.get("class", "")
                if "headword-tr" in class_names:
                    forms_start_index = index + 1

                    page_data[-1]["forms"].append(
                        {
                            "form": clean_node(wxr, page_data[-1], child),
                            "tags": ["romanization"],
                        }
                    )
                elif "gender" in class_names:
                    forms_start_index = index + 1
                    for abbr_tag in filter(
                        lambda x: isinstance(x, WikiNode)
                        and x.kind == NodeKind.HTML
                        and x.sarg == "abbr",
                        child.children,
                    ):
                        gender = abbr_tag.children[0]
                        page_data[-1]["tags"].append(
                            GENDERS.get(gender, gender)
                        )
                if lang_code == "ja":
                    for span_child in child.find_child(NodeKind.HTML):
                        if (
                            span_child.sarg == "strong"
                            and "headword" in span_child.attrs.get("class", "")
                        ):
                            ruby_data, node_without_ruby = extract_ruby(
                                wxr, span_child
                            )
                            page_data[-1]["forms"].append(
                                {
                                    "form": clean_node(
                                        wxr, page_data[-1], node_without_ruby
                                    ),
                                    "ruby": ruby_data,
                                    "tags": ["canonical"],
                                }
                            )
            elif child.sarg == "b":
                # this is a form <b> tag, already inside form parentheses
                break

    extract_headword_forms(
        wxr, page_data, expanded_node.children[forms_start_index:]
    )


def extract_headword_forms(
    wxr: WiktextractContext,
    page_data: List[Dict],
    form_nodes: List[Union[WikiNode, str]],
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
    page_data: List[Dict],
    form_nodes: List[Union[WikiNode, str]],
) -> None:
    tag_nodes = []
    has_forms = False
    striped_nodes = list(strip_nodes(form_nodes))
    lang_code = page_data[-1].get("lang_code")
    for index, node in enumerate(striped_nodes):
        if isinstance(node, WikiNode) and node.kind == NodeKind.HTML:
            if node.sarg == "b":
                has_forms = True
                ruby_data = None
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
                        and next_node.sarg == "span"
                        and "gender" in next_node.attrs.get("class", "")
                    ):
                        gender = clean_node(wxr, None, next_node)
                        form_tags.append(GENDERS.get(gender, gender))

                form_data = {
                    "form": form,
                    "tags": form_tags,
                }
                if ruby_data is not None:
                    form_data["ruby"] = ruby_data
                page_data[-1]["forms"].append(form_data)
            elif node.sarg == "span" and "tr" in node.attrs.get("class", ""):
                # romanization of the previous form <b> tag
                page_data[-1]["forms"][-1]["roman"] = clean_node(
                    wxr, None, node
                )
            else:
                tag_nodes.append(node)
        else:
            tag_nodes.append(node)

    if not has_forms:
        tags_list = extract_headword_tags(
            clean_node(wxr, page_data[-1], tag_nodes).strip("() ")
        )
        if len(tags_list) > 0:
            page_data[-1]["tags"].extend(tags_list)
    else:
        clean_node(wxr, page_data[-1], tag_nodes)  # find categories


def extract_headword_tags(tags_str: str) -> List[str]:
    tags = []
    for tag_str in (
        s.strip() for s in re.split("&|或", tags_str) if len(s.strip()) > 0
    ):
        tags.extend(FORM_TAGS.get(tag_str, [tag_str]))
    return tags
