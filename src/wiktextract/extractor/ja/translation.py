from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


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
            for list_item in node.find_child_recursively(NodeKind.LIST_ITEM):
                process_translation_list_item(
                    wxr, word_entry, list_item, sense_text
                )


def process_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense_text: str,
) -> None:
    lang_name = ""
    lang_code = ""
    after_collon = False
    for node_index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and not after_collon:
            after_collon = True
            if lang_name == "":
                lang_nodes = list_item.children[:node_index]
                lang_nodes.append(node[:node.index(":")])
                lang_name = clean_node(wxr, None, lang_nodes)
                lang_code = name_to_code(lang_name, "ja")
        elif isinstance(node, TemplateNode):
            if not after_collon:
                lang_name = clean_node(wxr, None, node)
                if node.template_name == "T":
                    lang_code = node.template_parameters.get(1, "")
                else:
                    lang_code = node.template_name
            elif node.template_name.lower() in ["t+", "t", "t-", "l", "lang"]:
                process_t_template(
                    wxr, word_entry, node, sense_text, lang_name, lang_code
                )
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and after_collon
        ):
            tr_word = clean_node(wxr, None, node)
            if len(tr_word) > 0:
                word_entry.translations.append(
                    Translation(
                        word=tr_word,
                        sense=sense_text,
                        lang_code=lang_code,
                        lang=lang_name,
                    )
                )


def process_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    node: TemplateNode,
    sense_text: str,
    lang_name: str,
    lang_code: str,
) -> None:
    tr_word = clean_node(wxr, None, node.template_parameters.get(2, ""))
    if "alt" in node.template_parameters:
        tr_word = clean_node(wxr, None, node.template_parameters["alt"])
    roman = clean_node(wxr, None, node.template_parameters.get("tr", ""))
    if len(tr_word) > 0:
        word_entry.translations.append(
            Translation(
                word=tr_word,
                roman=roman,
                sense=sense_text,
                lang_code=lang_code,
                lang=lang_name,
            )
        )
