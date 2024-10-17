from mediawiki_langcodes import name_to_code
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Descendant, WordEntry


def extract_descendant_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    # https://nl.wiktionary.org/wiki/WikiWoordenboek:Overerving_en_ontlening
    desc_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            desc_list.extend(extract_descendant_list_item(wxr, list_item))
    word_entry.descendants.extend(desc_list)


def extract_descendant_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Descendant]:
    desc_list = []
    before_colon = True
    lang_code = "unknown"
    lang_name = "unknown"
    for index, node in enumerate(list_item.children):
        if before_colon and isinstance(node, str) and ":" in node:
            before_colon = False
            lang_name = clean_node(wxr, None, list_item.children[:index]).strip(
                "→ "
            )
            new_lang_code = name_to_code(lang_name, "nl")
            if new_lang_code != "":
                lang_code = new_lang_code
        elif not before_colon and (
            (isinstance(node, TemplateNode) and node.template_name == "Q")
            or (isinstance(node, WikiNode) and node.kind == NodeKind.LINK)
        ):
            desc_list.append(
                Descendant(
                    lang=lang_name,
                    lang_code=lang_code,
                    word=clean_node(wxr, None, node),
                )
            )

    for nested_list in list_item.find_child(NodeKind.LIST):
        for nested_list_item in nested_list.find_child(NodeKind.LIST_ITEM):
            child_data = extract_descendant_list_item(wxr, nested_list_item)
            for parent_data in desc_list:
                parent_data.descendants.extend(child_data)

    return desc_list
