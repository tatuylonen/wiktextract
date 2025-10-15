from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Descendant, Linkage, WordEntry


def extract_desc_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    desc_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            desc_list.extend(extract_desc_list_item(wxr, list_item, []))
    word_entry.descendants.extend(desc_list)


def extract_desc_list_item(
    wxr: WiktextractContext, list_item: WikiNode, parent_data: list[Descendant]
) -> list[Descendant]:
    lang_code = "unknown"
    lang_name = "unknown"
    desc_list = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "L":
            lang_code = node.template_parameters.get(1)
            lang_name = clean_node(wxr, None, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                desc_list.append(
                    Descendant(lang_code=lang_code, lang=lang_name, word=word)
                )
        elif isinstance(node, TemplateNode) and node.template_name in [
            "l",
            "lien",
            "zh-lien",
            "zh-lien-t",
        ]:
            from .linkage import process_linkage_template

            l_data = Linkage(word="")
            process_linkage_template(wxr, node, l_data)
            desc_list.append(
                Descendant(
                    lang=lang_name,
                    lang_code=lang_code,
                    word=l_data.word,
                    roman=l_data.roman,
                    ruby=l_data.ruby,
                    tags=l_data.tags,
                    raw_tags=l_data.raw_tags,
                )
            )
        elif isinstance(node, TemplateNode) and node.template_name == "zh-l":
            from .linkage import extract_zh_l_template

            l_list = extract_zh_l_template(wxr, node)
            for l_data in l_list:
                desc_list.append(
                    Descendant(
                        lang=lang_name,
                        lang_code=lang_code,
                        word=l_data.word,
                        roman=l_data.roman,
                        tags=l_data.tags,
                        raw_tags=l_data.raw_tags,
                    )
                )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_desc_list_item(wxr, child_list_item, desc_list)

    for p_desc in parent_data:
        p_desc.descendants.extend(desc_list)
    return desc_list
