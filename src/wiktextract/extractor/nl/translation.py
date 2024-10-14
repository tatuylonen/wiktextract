import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    sense = ""
    sense_index = 0
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        if isinstance(node, TemplateNode) and node.template_name == "trans-top":
            first_arg = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            m = re.match(r"(\d+)\.", first_arg)
            if m is not None:
                sense_index = int(m.group(1))
                sense = first_arg[m.end() :].strip()
            else:
                sense = first_arg
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, list_item, sense, sense_index
                )


TR_TEMPLATES = {
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",
    "s": "singular",
    "p": "plural",
    "a": "animate",
    "i": "inanimate",
}


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    sense_index: int,
) -> None:
    before_colon = True
    lang_name = ""
    brackets = 0
    roman_str = ""
    for index, node in enumerate(list_item.children):
        if before_colon and isinstance(node, str) and ":" in node:
            before_colon = False
            lang_name = clean_node(wxr, None, list_item.children[:index])
        elif not before_colon:
            if brackets == 0 and isinstance(node, TemplateNode):
                if node.template_name == "trad":
                    word_entry.translations.append(
                        Translation(
                            lang=lang_name,
                            lang_code=node.template_parameters.get(1, ""),
                            word=node.template_parameters.get(2, ""),
                            sense=sense,
                            sense_index=sense_index,
                        )
                    )
                elif (
                    node.template_name in TR_TEMPLATES
                    and len(word_entry.translations) > 0
                ):
                    word_entry.translations[-1].tags.append(
                        TR_TEMPLATES[node.template_name]
                    )
            elif isinstance(node, str):
                for c in node:
                    if c == "(":
                        brackets += 1
                    elif c == ")":
                        brackets -= 1
                        if brackets == 0:
                            if len(word_entry.translations) > 0:
                                word_entry.translations[-1].roman = roman_str
                            roman_str = ""
                    elif brackets > 0:
                        roman_str += c
            elif brackets > 0:
                roman_str += clean_node(wxr, None, node)
