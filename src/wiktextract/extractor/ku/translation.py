import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    sense = ""
    sense_index = 0
    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "werger-ser"
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
            sense_i_str = clean_node(
                wxr, None, node.template_parameters.get(2, "")
            )
            if re.fullmatch(r"\d+", sense_i_str):
                sense_index = int(sense_i_str)
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, list_item, sense, sense_index
                )


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    sense_index: int,
) -> None:
    lang_name = "unknown"
    before_colon = True
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = clean_node(
                wxr,
                None,
                list_item.children[:index] + [node[: node.index(":")]],
            )
            before_colon = False
        elif isinstance(node, TemplateNode) and node.template_name in [
            "W",
            "W+",
            "W-",
        ]:
            extract_w_template(
                wxr, word_entry, node, sense, sense_index, lang_name
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense, sense_index
                )
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and not before_colon
        ):
            tr_data = Translation(
                word=clean_node(wxr, None, node),
                lang=lang_name,
                lang_code=name_to_code(lang_name, "ku") or "unknown",
                sense=sense,
                sense_index=sense_index,
            )
            if tr_data.word != "":
                word_entry.translations.append(tr_data)


def extract_w_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
    sense_index: int,
    lang_name: str,
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:W
    tr_data = Translation(
        lang=lang_name,
        lang_code=clean_node(
            wxr, None, t_node.template_parameters.get(1, "unknown")
        ),
        word=clean_node(
            wxr,
            None,
            t_node.template_parameters.get(
                "cuda", t_node.template_parameters.get(2, "")
            ),
        ),
    )
    tag_args = {
        "n": "masculine",
        "m": "feminine",
        "f": "feminine",
        "nt": "gender-neutral",
        "mn": ["feminine", "masculine"],
        "g": "common-gender",
        "p": "plural",
        "y": "singular",
    }
    for tag_arg in [3, 4]:
        tag_arg_value = clean_node(
            wxr, None, t_node.template_parameters.get(tag_arg, "")
        )
        if tag_arg_value in tag_args:
            tr_data.tags.append(tag_args[tag_arg_value])
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        if "Latn" in span_tag.attrs.get("class", ""):
            roman = clean_node(wxr, None, span_tag)
            if roman not in ["", tr_data.word]:
                tr_data.roman = roman
                break
    if tr_data.word != "":
        word_entry.translations.append(tr_data)
