import re

from typing import Dict, List, Union

from wikitextprocessor import WikiNode, NodeKind
from wiktextract.datautils import data_append, data_extend
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

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
    template_name = node.args[0][0]
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
            if child.args == "strong" and "headword" in child.attrs.get(
                "class", ""
            ):
                forms_start_index = index + 1
            elif child.args == "span":
                class_names = child.attrs.get("class", "")
                if "headword-tr" in class_names:
                    forms_start_index = index + 1
                    data_append(
                        wxr,
                        page_data[-1],
                        "forms",
                        {
                            "form": clean_node(wxr, None, child),
                            "tags": ["romanization"],
                        },
                    )
                elif "gender" in class_names:
                    forms_start_index = index + 1
                    for abbr_tag in filter(
                        lambda x: isinstance(x, WikiNode)
                        and x.kind == NodeKind.HTML
                        and x.args == "abbr",
                        child.children,
                    ):
                        gender = abbr_tag.children[0]
                        data_append(
                            wxr,
                            page_data[-1],
                            "tags",
                            GENDERS.get(gender, gender),
                        )
            elif child.args == "b":
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
    for index, node in enumerate(striped_nodes):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.HTML
            and node.args == "b"
        ):
            has_forms = True
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
                    and next_node.args == "span"
                    and "gender" in next_node.attrs.get("class", "")
                ):
                    gender = clean_node(wxr, None, next_node)
                    form_tags.append(GENDERS.get(gender, gender))
            data_append(
                wxr,
                page_data[-1],
                "forms",
                {
                    "form": form,
                    "tags": form_tags,
                },
            )
        else:
            tag_nodes.append(node)

    if not has_forms:
        data_extend(
            wxr,
            page_data[-1],
            "tags",
            extract_headword_tags(
                clean_node(wxr, None, tag_nodes).strip("() ")
            ),
        )


def extract_headword_tags(tags_str: str) -> List[str]:
    tags = []
    for tag_str in (
        s.strip() for s in re.split("&|或", tags_str) if len(s.strip()) > 0
    ):
        tags.extend(FORM_TAGS.get(tag_str, [tag_str]))
    return tags
