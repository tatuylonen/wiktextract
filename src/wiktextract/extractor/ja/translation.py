from typing import Optional

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    sense_text = ""
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        if isinstance(node, TemplateNode) and node.template_name == "trans-top":
            sense_text = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                process_translation_list_item(
                    wxr, word_entry, list_item, sense_text, "", ""
                )


def process_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense_text: str,
    lang_name: str,
    lang_code: str,
) -> None:
    after_collon = False
    last_tr: Optional[Translation] = None
    for node_index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and not after_collon:
            after_collon = True
            lang_nodes = list_item.children[:node_index]
            lang_nodes.append(node[: node.index(":")])
            new_lang_name = clean_node(wxr, None, lang_nodes)
            new_lang_code = name_to_code(new_lang_name, "ja")
            if new_lang_code != "":
                lang_code = new_lang_code
                lang_name = new_lang_name
        elif isinstance(node, TemplateNode):
            if not after_collon:
                lang_name = clean_node(wxr, None, node)
                if node.template_name == "T":
                    lang_code = node.template_parameters.get(1, "")
                else:
                    lang_code = node.template_name
            elif node.template_name.lower() in ["t+", "t", "t-", "l", "lang"]:
                last_tr = process_t_template(
                    wxr, word_entry, node, sense_text, lang_name, lang_code
                )
            elif node.template_name.lower() == "archar":
                tr_data = Translation(
                    word=clean_node(wxr, None, node),
                    sense=sense_text,
                    lang_code=lang_code,
                    lang=lang_name,
                )
                word_entry.translations.append(tr_data)
                last_tr = tr_data
            elif (
                node.template_name.lower()
                in [
                    "m",
                    "f",
                    "p",
                    "n",
                    "c",
                    "s",
                    "mf",
                    "mpl",
                    "fpl",
                    "npl",
                    "inv",
                ]
                and last_tr is not None
            ):
                last_tr.raw_tags.append(clean_node(wxr, None, node))
                translate_raw_tags(last_tr)
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and after_collon
        ):
            tr_word = clean_node(wxr, None, node)
            if len(tr_word) > 0:
                tr_data = Translation(
                    word=tr_word,
                    sense=sense_text,
                    lang_code=lang_code,
                    lang=lang_name,
                )
                word_entry.translations.append(tr_data)
                last_tr = tr_data
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for nested_list_item in node.find_child_recursively(
                NodeKind.LIST_ITEM
            ):
                process_translation_list_item(
                    wxr,
                    word_entry,
                    nested_list_item,
                    sense_text,
                    lang_name,
                    lang_code,
                )


T_TAGS = {
    "m": "masculine",
    "f": "feminine",
    "mf": ["masculine", "feminine"],
    "n": "neuter",
    "c": "common",
    "impf": "imperfective",
    "pf": "perfective",
    "s": "singular",
    "p": "plural",
}


def process_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    node: TemplateNode,
    sense_text: str,
    lang_name: str,
    lang_code: str,
) -> Optional[Translation]:
    # https://ja.wiktionary.org/wiki/テンプレート:t
    tr_word = clean_node(wxr, None, node.template_parameters.get(2, ""))
    if "alt" in node.template_parameters:
        tr_word = clean_node(wxr, None, node.template_parameters["alt"])
    roman = clean_node(wxr, None, node.template_parameters.get("tr", ""))
    tags = []
    for arg_index in [3, 4]:
        if arg_index in node.template_parameters:
            tag_arg = clean_node(
                wxr, None, node.template_parameters.get(arg_index, "")
            )
            tag_value = T_TAGS.get(tag_arg, [])
            if isinstance(tag_value, str):
                tags.append(tag_value)
            elif isinstance(tag_value, list):
                tags.extend(tag_value)
    if len(tr_word) > 0:
        tr_data = Translation(
            word=tr_word,
            roman=roman,
            sense=sense_text,
            lang_code=lang_code,
            lang=lang_name,
            tags=tags,
        )
        word_entry.translations.append(tr_data)
        return tr_data
    return None
