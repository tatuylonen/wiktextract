from typing import Optional

from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    base_translation_data = Translation()
    for level_node_child in level_node.filter_empty_str_child():
        if isinstance(level_node_child, WikiNode):
            if level_node_child.kind == NodeKind.TEMPLATE:
                # get sense from "trad-début" template
                process_translation_templates(
                    wxr, level_node_child, page_data, base_translation_data
                )
            elif level_node_child.kind == NodeKind.LIST:
                for list_item_node in level_node_child.find_child(
                    NodeKind.LIST_ITEM
                ):
                    previous_node = None
                    for child_node in list_item_node.filter_empty_str_child():
                        if isinstance(child_node, WikiNode):
                            if child_node.kind == NodeKind.TEMPLATE:
                                process_translation_templates(
                                    wxr,
                                    child_node,
                                    page_data,
                                    base_translation_data,
                                )
                            elif child_node.kind == NodeKind.ITALIC:
                                process_italic_node(
                                    wxr, child_node, previous_node, page_data
                                )
                            previous_node = child_node
            elif level_node_child.kind in LEVEL_KIND_FLAGS:
                from .page import parse_section

                parse_section(wxr, page_data, base_data, level_node_child)


def process_italic_node(
    wxr: WiktextractContext,
    italic_node: WikiNode,
    previous_node: Optional[WikiNode],
    page_data: list[WordEntry],
) -> None:
    # add italic text after a "trad" template as a tag
    tag = clean_node(wxr, None, italic_node)
    if (
        tag.startswith("(")
        and tag.endswith(")")
        and previous_node is not None
        and previous_node.kind == NodeKind.TEMPLATE
        and previous_node.template_name.startswith("trad")
        and len(page_data[-1].translations) > 0
    ):
        tag = tag.strip("()")
        if len(tag) > 0:
            page_data[-1].translations[-1].raw_tags.append(tag)
            translate_raw_tags(page_data[-1].translations[-1])


def process_translation_templates(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    page_data: list[WordEntry],
    base_translation_data: Translation,
) -> None:
    if template_node.template_name == "trad-fin":
        # ignore translation end template
        return
    elif template_node.template_name == "trad-début":
        # translation box start: https://fr.wiktionary.org/wiki/Modèle:trad-début
        sense_parameter = template_node.template_parameters.get(1, "")
        sense_text = clean_node(wxr, None, sense_parameter)
        base_translation_data.sense = sense_text
        sense_index_str = template_node.template_parameters.get(2, "0")
        if isinstance(sense_index_str, str) and sense_index_str.isdecimal():
            base_translation_data.sense_index = int(sense_index_str)

    elif template_node.template_name == "T":
        # Translation language: https://fr.wiktionary.org/wiki/Modèle:T
        base_translation_data.lang_code = template_node.template_parameters.get(
            1, ""
        )
        base_translation_data.lang = clean_node(
            wxr, page_data[-1], template_node
        )
    elif template_node.template_name.startswith("trad"):
        # Translation term: https://fr.wiktionary.org/wiki/Modèle:trad
        if 2 not in template_node.template_parameters:  # required parameter
            return
        translation_term = clean_node(
            wxr,
            None,
            template_node.template_parameters.get(
                "dif", template_node.template_parameters.get(2)
            ),
        )
        translation_roman = clean_node(
            wxr,
            None,
            (
                template_node.template_parameters.get(
                    "tr", template_node.template_parameters.get("R", "")
                )
            ),
        )
        # traditional writing of Chinese and Korean word
        translation_traditional_writing = clean_node(
            wxr, None, template_node.template_parameters.get("tradi", "")
        )
        translation_data = base_translation_data.model_copy(deep=True)
        translation_data.word = translation_term
        if len(translation_roman) > 0:
            translation_data.roman = translation_roman
        if len(translation_traditional_writing) > 0:
            translation_data.traditional_writing = (
                translation_traditional_writing
            )
        if 3 in template_node.template_parameters:
            tags = []
            for tag_character in template_node.template_parameters[3]:
                if tag_character in TRAD_TAGS:
                    tags.append(TRAD_TAGS[tag_character])
            if len(tags) > 0:
                translation_data.tags.append(" ".join(tags))
        if translation_data.lang_code == "":
            translation_data.lang_code = template_node.template_parameters.get(
                1, ""
            )
        if translation_data.lang == "":
            translation_data.lang = code_to_name(
                translation_data.lang_code, "fr"
            ).capitalize()
        if len(translation_data.word) > 0:
            page_data[-1].translations.append(translation_data)
    elif len(page_data[-1].translations) > 0:
        tag = clean_node(wxr, None, template_node).strip("()")
        if len(tag) > 0:
            page_data[-1].translations[-1].raw_tags.append(tag)
            translate_raw_tags(page_data[-1].translations[-1])


# https://fr.wiktionary.org/wiki/Modèle:trad
TRAD_TAGS: dict[str, str] = {
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",
    "s": "singular",
    "p": "plural",
    "d": "dual",
    "a": "animate",
    "i": "inanimate",
}
