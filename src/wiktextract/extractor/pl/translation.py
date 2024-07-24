import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    translations = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        base_tr_data = Translation()
        for index, node in enumerate(list_item.children):
            if isinstance(node, str):
                if index == 0 and ":" in node:
                    lang_name = node[: node.index(":")].strip()
                    base_tr_data.lang = lang_name
                    lang_code = name_to_code(lang_name, "pl")
                    if lang_code == "":
                        lang_code = "unknown"
                    base_tr_data.lang_code = lang_code
                m_index = re.search(r"\(\d+\.\d+\)", node)
                if m_index is not None:
                    base_tr_data.sense_index = m_index.group(0).strip("()")
                m_roman = re.search(r"\([^()]+\)", node)
                if (
                    m_roman is not None
                    and len(translations) > 0
                    and (m_index is None or m_index.start() != m_roman.start())
                ):
                    translations[-1].roman = m_roman.group(0).strip("()")
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                if len(word) > 0:
                    new_tr_data = base_tr_data.model_copy(deep=True)
                    new_tr_data.word = word
                    translations.append(new_tr_data)
            elif isinstance(node, TemplateNode) and len(translations) > 0:
                raw_tag = clean_node(wxr, None, node)
                if len(raw_tag) > 0:
                    translations[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(translations[-1])

    for data in page_data:
        if data.lang_code == base_data.lang_code:
            data.translations = translations
    base_data.translations = translations
