import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
) -> None:
    # https://it.wiktionary.org/wiki/Aiuto:Traduzioni
    sense = ""
    translations = []
    cats = {}
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name == "Trad1":
            sense = clean_node(wxr, cats, node.template_parameters.get(1, ""))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                translations.extend(
                    extract_translation_list_item(wxr, list_item, sense)
                )

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.translations.extend(translations)
            data.categories.extend(cats.get("categories", []))


TR_GENDER_TAGS = {
    "c": "common",
    "f": "feminine",
    "m": "masculine",
    "n": "neuter",
}


def extract_translation_list_item(
    wxr: WiktextractContext, list_item: WikiNode, sense: str
) -> list[Translation]:
    translations = []
    lang_name = "unknown"
    lang_code = "unknown"
    before_colon = True
    for index, node in enumerate(list_item.children):
        if before_colon and isinstance(node, str) and ":" in node:
            before_colon = False
            lang_name = clean_node(wxr, None, list_item.children[:index])
            for n in list_item.children[:index]:
                if isinstance(n, TemplateNode):
                    lang_code = n.template_name
                    break
            if lang_code == "unknown":
                new_lang_code = name_to_code(lang_name, "it")
                if new_lang_code != "":
                    lang_code = new_lang_code
        elif not before_colon and isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "":
                        translations.append(
                            Translation(
                                word=word,
                                sense=sense,
                                lang=lang_name,
                                lang_code=lang_code,
                            )
                        )
                case NodeKind.ITALIC:
                    raw_tag = clean_node(wxr, None, node)
                    if raw_tag in TR_GENDER_TAGS and len(translations) > 0:
                        translations[-1].tags.append(TR_GENDER_TAGS[raw_tag])
                    elif raw_tag != "" and len(translations) > 0:
                        translations[-1].raw_tags.append(raw_tag)
        elif not before_colon and isinstance(node, str):
            m = re.search(r"\((.+)\)", node)
            if m is not None and len(translations) > 0:
                translations[-1].roman = m.group(1)

    return translations
