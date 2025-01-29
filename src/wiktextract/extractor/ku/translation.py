import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def is_translation_page(title: str) -> bool:
    return re.search(r"/Werger(?:\d+)?$", title) is not None


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
    source: str = "",
) -> None:
    sense = ""
    sense_index = 0
    for node in level_node.find_child(
        NodeKind.LIST | NodeKind.TEMPLATE | NodeKind.ITALIC | NodeKind.BOLD
    ):
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
                    wxr, word_entry, list_item, sense, sense_index, source
                )
        elif node.kind in (NodeKind.ITALIC | NodeKind.BOLD):
            for link_node in node.find_child(NodeKind.LINK):
                link_str = clean_node(wxr, None, link_node)
                if is_translation_page(link_str):
                    extract_translation_page(wxr, word_entry, link_str)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name == "werger-bnr"
        ):
            page_title = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            if is_translation_page(page_title):
                extract_translation_page(wxr, word_entry, page_title)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    sense_index: int,
    source: str,
) -> None:
    lang_name = "unknown"
    lang_code = "unknown"
    before_colon = True
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = clean_node(
                wxr,
                None,
                list_item.children[:index] + [node[: node.index(":")]],
            )
            before_colon = False
        elif isinstance(node, TemplateNode) and node.template_name == "Z":
            lang_code = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
        elif isinstance(node, TemplateNode) and node.template_name in [
            "W",
            "W+",
            "W-",
        ]:
            extract_w_template(
                wxr, word_entry, node, sense, sense_index, lang_name, source
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense, sense_index, source
                )
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and not before_colon
        ):
            if lang_code in ["", "unknown"]:
                new_code = name_to_code(lang_name, "ku")
                if new_code != "":
                    lang_code = new_code
            tr_data = Translation(
                word=clean_node(wxr, None, node),
                lang=lang_name,
                lang_code=lang_code,
                sense=sense,
                sense_index=sense_index,
                source=source,
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
    source: str,
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
        source=source,
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


def extract_translation_page(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    page_title: str,
) -> None:
    page = wxr.wtp.get_page(page_title, 0)
    if page is None or page.body is None:
        return
    root = wxr.wtp.parse(page.body)
    for level2_node in root.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        if lang_name != word_entry.lang:
            continue
        for child_level in level2_node.find_child_recursively(LEVEL_KIND_FLAGS):
            child_level_str = clean_node(wxr, None, child_level.largs)
            if child_level_str == "Werger":
                extract_translation_section(
                    wxr, word_entry, child_level, page_title
                )
