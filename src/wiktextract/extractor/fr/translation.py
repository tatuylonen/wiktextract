from mediawiki_langcodes import code_to_name
from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: WikiNode
) -> None:
    base_translation_data = Translation()
    for level_node_child in level_node.filter_empty_str_child():
        if isinstance(level_node_child, WikiNode):
            if level_node_child.kind == NodeKind.TEMPLATE:
                # get sense from "trad-début" template
                process_translation_templates(
                    wxr,
                    level_node_child,
                    page_data,
                    base_translation_data,
                    None,
                )
            elif level_node_child.kind == NodeKind.LIST:
                for list_item_node in level_node_child.find_child(
                    NodeKind.LIST_ITEM
                ):
                    previous_node = None
                    translation_data = None
                    for child_node in list_item_node.filter_empty_str_child():
                        if isinstance(child_node, WikiNode):
                            if child_node.kind == NodeKind.TEMPLATE:
                                translation_data = (
                                    process_translation_templates(
                                        wxr,
                                        child_node,
                                        page_data,
                                        base_translation_data,
                                        translation_data,
                                    )
                                )
                            elif child_node.kind == NodeKind.ITALIC:
                                process_italic_node(
                                    wxr,
                                    child_node,
                                    previous_node,
                                    translation_data,
                                )
                            previous_node = child_node


def process_italic_node(
    wxr: WiktextractContext,
    italic_node: WikiNode,
    previous_node: WikiNode | None,
    translation_data: Translation | None,
) -> None:
    # add italic text after a "trad" template as a tag
    tag = clean_node(wxr, None, italic_node)
    if (
        tag.startswith("(")
        and tag.endswith(")")
        and previous_node is not None
        and previous_node.kind == NodeKind.TEMPLATE
        and previous_node.template_name.startswith("trad")
        and translation_data is not None
    ):
        tag = tag.strip("()")
        if len(tag) > 0:
            translation_data.raw_tags.append(tag)
            translate_raw_tags(translation_data)


def process_translation_templates(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    page_data: list[WordEntry],
    base_translation_data: Translation,
    translation_data: Translation | None,
) -> Translation | None:
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
        translation_data = base_translation_data.model_copy(deep=True)
        term_nodes = template_node.template_parameters.get(
            "dif", template_node.template_parameters.get(2)
        )
        if base_translation_data.lang_code == "ja":
            expanded_term_nodes = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(term_nodes), expand_all=True
            )
            ruby_data, node_without_ruby = extract_ruby(
                wxr, expanded_term_nodes.children
            )
            translation_data.ruby = ruby_data
            translation_data.word = clean_node(wxr, None, node_without_ruby)
        else:
            translation_data.word = clean_node(wxr, None, term_nodes)
        translation_data.roman = clean_node(
            wxr,
            None,
            (
                template_node.template_parameters.get(
                    "tr", template_node.template_parameters.get("R", "")
                )
            ),
        )
        # traditional writing of Chinese and Korean word
        translation_data.traditional_writing = clean_node(
            wxr, None, template_node.template_parameters.get("tradi", "")
        )
        if 3 in template_node.template_parameters:
            for tag_character in template_node.template_parameters[3]:
                if tag_character in TRAD_TAGS:
                    translation_data.tags.append(TRAD_TAGS[tag_character])
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
    elif translation_data is not None:
        tag = clean_node(wxr, None, template_node).strip("()")
        if len(tag) > 0:
            translation_data.raw_tags.append(tag)
            translate_raw_tags(translation_data)
    return translation_data


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
