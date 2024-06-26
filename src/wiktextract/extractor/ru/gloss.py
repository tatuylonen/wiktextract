import re
from typing import Optional

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    TemplateNode,
    WikiNodeChildrenList,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import process_example_template
from .linkage import process_semantics_template
from .models import Linkage, Sense, WordEntry
from .section_titles import LINKAGE_TITLES
from .tags import translate_raw_tags

# Wiktioniary intern templates that can be ignores
META_TEMPLATES = {
    "помета.",
    "Нужен перевод",
    "?",
}

# Templates that are part of the clean gloss when expanded
GLOSS_TEMPLATES = {
    "-",
    "=",
    "===",
    "english surname example",
    "lang",
    "аббр.",
    "выдел",
    "гипокор.",
    "дееприч.",
    "действие",
    "женск.",
    "ласк.",
    "мн",
    "морфема",
    "нареч.",
    "наречие",
    "однокр.",
    "отн.",
    "по.",
    "по",
    "превосх.",
    "прич.",
    "свойство",
    "совершить",
    "сокр.",
    "сокращ",
    "соотн.",
    "сравн.",
    "страд.",
    "то же",
    "увелич.",
    "уменьш.",
    "умласк",
    "умласк.",
    "унич.",
    "уничиж.",
    "хим-элем",
    "элемент",
}

# Templates that specify a note for the gloss
NOTE_TEMPLATES = {"пример", "помета", "??", "as ru"}

IGNORED_TEMPLATES = {"нужен перевод"}

TAG_GLOSS_TEMPLATES = {
    "многокр.": "iterative",
    "нареч.": "adverb",
    "наречие": "adverb",  # redirect to "нареч."
    "однокр.": "semelefactive",
    "превосх.": "superlative",
    "прич.": "participle",
    "сокр.": "abbreviation",
    "сравн.": "comparative",
    "страд.": "passive",
    "счётн.": "numeral",
}


def extract_gloss(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    has_gloss_list = False
    for sense_index, list_item in enumerate(
        level_node.find_child_recursively(NodeKind.LIST_ITEM), 1
    ):
        process_gloss_nodes(wxr, word_entry, list_item.children, sense_index)
        has_gloss_list = True
    if not has_gloss_list:
        # no list or empty list
        process_gloss_nodes(
            wxr,
            word_entry,
            list(level_node.invert_find_child(LEVEL_KIND_FLAGS)),
            1,
        )


def process_gloss_nodes(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    gloss_nodes: WikiNodeChildrenList,
    sense_index: int,
) -> None:
    sense = Sense()

    raw_gloss_children: WikiNodeChildrenList = []
    clean_gloss_children: WikiNodeChildrenList = []
    tag_templates: list[WikiNode] = []
    note_templates: list[WikiNode] = []

    for child in gloss_nodes:
        if isinstance(child, TemplateNode):
            if child.template_name.lower() in IGNORED_TEMPLATES:
                continue
            elif child.template_name == "пример":
                process_example_template(wxr, sense, child)
            elif child.template_name == "семантика":
                process_semantics_template(wxr, word_entry, child, sense_index)
            elif child.template_name in NOTE_TEMPLATES:
                note_templates.append(child)
                raw_gloss_children.append(child)

            elif child.template_name in META_TEMPLATES:
                continue

            elif child.template_name in GLOSS_TEMPLATES:
                clean_gloss_children.append(child)
                raw_gloss_children.append(child)
            elif child.template_name in TAG_GLOSS_TEMPLATES:
                sense.tags.append(TAG_GLOSS_TEMPLATES[child.template_name])
                clean_gloss_children.append(child)
                raw_gloss_children.append(child)
            elif (
                child.template_name.endswith(".")
                or child.template_name == "помета"
            ):
                # Assume node is tag template
                tag_templates.append(child)
                raw_gloss_children.append(child)
            elif child.template_name == "значение":
                process_meaning_template(wxr, sense, word_entry, child)
        else:
            clean_gloss_children.append(child)
            raw_gloss_children.append(child)

    remove_obsolete_leading_nodes(raw_gloss_children)
    remove_obsolete_leading_nodes(clean_gloss_children)

    gloss = clean_node(wxr, None, clean_gloss_children)
    if len(gloss) > 0:
        sense.glosses.append(gloss)
    raw_gloss = clean_node(wxr, None, raw_gloss_children)
    if len(raw_gloss) > 0 and raw_gloss != gloss:
        sense.raw_glosses.append(raw_gloss)

    for tag_template in tag_templates:
        raw_tag = clean_node(wxr, None, tag_template)
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)

    for note_template in note_templates:
        note = clean_node(wxr, None, note_template)
        if note != "":
            sense.notes.append(note)

    if sense != Sense():
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def remove_obsolete_leading_nodes(nodes: WikiNodeChildrenList):
    while (
        nodes
        and isinstance(nodes[0], str)
        and nodes[0].strip() in ["", "и", "или", ",", ".", ";", ":", "\n"]
    ):
        nodes.pop(0)


def process_meaning_template(
    wxr: WiktextractContext,
    sense: Optional[Sense],
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> Sense:
    # https://ru.wiktionary.org/wiki/Шаблон:значение
    if sense is None:
        sense = Sense()

    gloss = ""
    for param_name, param_value in template_node.template_parameters.items():
        if param_name == "определение":
            gloss = clean_node(wxr, None, param_value)
            if len(gloss) > 0:
                sense.glosses.append(gloss)
        elif param_name == "пометы":
            raw_tag = clean_node(wxr, None, param_value)
            if len(raw_tag) > 0:
                sense.raw_tags.append(raw_tag)
        elif param_name == "примеры" and isinstance(param_value, list):
            for t_node in param_value:
                if isinstance(t_node, TemplateNode):
                    process_example_template(wxr, sense, t_node)
        elif param_name in LINKAGE_TITLES:
            linkage_type = LINKAGE_TITLES[param_name]
            if isinstance(param_value, str) and len(param_value.strip()) > 0:
                for linkage_word in re.split(r",|;", param_value):
                    linkage_word = linkage_word.strip()
                    if len(linkage_word) > 0 and linkage_word != "-":
                        linkage_list = getattr(word_entry, linkage_type)
                        linkage_list.append(
                            Linkage(word=linkage_word, sense=gloss)
                        )
            elif isinstance(param_value, list):
                for param_node in param_value:
                    if (
                        isinstance(param_node, WikiNode)
                        and param_node.kind == NodeKind.LINK
                    ):
                        linkage_word = clean_node(wxr, None, param_node)
                        if len(linkage_word) > 0:
                            linkage_list = getattr(word_entry, linkage_type)
                            linkage_list.append(
                                Linkage(word=linkage_word, sense=gloss)
                            )

    if len(sense.glosses) > 0:
        translate_raw_tags(sense)

    clean_node(wxr, sense, template_node)
    return sense
