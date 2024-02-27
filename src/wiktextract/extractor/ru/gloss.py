from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, WikiNodeChildrenList
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .example import process_example_template
from .models import Sense, WordEntry

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


def extract_gloss(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_gloss_nodes(wxr, word_entry, list_item.children)
    if len(word_entry.senses) == 0:
        # no list or empty list
        process_gloss_nodes(
            wxr,
            word_entry,
            list(level_node.invert_find_child(LEVEL_KIND_FLAGS)),
        )


def process_gloss_nodes(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    gloss_nodes: WikiNodeChildrenList,
) -> None:
    sense = Sense()

    raw_gloss_children: WikiNodeChildrenList = []
    clean_gloss_children: WikiNodeChildrenList = []
    tag_templates: list[WikiNode] = []
    note_templates: list[WikiNode] = []

    for child in gloss_nodes:
        if isinstance(child, WikiNode) and child.kind == NodeKind.TEMPLATE:
            if child.template_name == "пример":
                process_example_template(wxr, sense, child)

            elif child.template_name == "семантика":
                # https://ru.wiktionary.org/wiki/Шаблон:семантика
                # XXX: Extract semantic templates to linkages
                continue
            elif child.template_name in NOTE_TEMPLATES:
                note_templates.append(child)
                raw_gloss_children.append(child)

            elif child.template_name in META_TEMPLATES:
                continue

            elif child.template_name in GLOSS_TEMPLATES:
                clean_gloss_children.append(child)
                raw_gloss_children.append(child)
            else:
                # Assume node is tag template
                tag_templates.append(child)
                raw_gloss_children.append(child)

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
        # XXX: Expanded tags are mostly still abbreviations. In Wiktionary,
        # however, they show the full word on hover. Perhaps it's possible to
        # extract the full word from the template?
        tag = clean_node(wxr, None, tag_template)
        if tag != "":
            sense.raw_tags.append(tag)

    for note_template in note_templates:
        note = clean_node(wxr, None, note_template)
        if note != "":
            sense.notes.append(note)

    if sense.model_dump(exclude_defaults=True) != {}:
        word_entry.senses.append(sense)


def remove_obsolete_leading_nodes(nodes: WikiNodeChildrenList):
    while (
        nodes
        and isinstance(nodes[0], str)
        and nodes[0].strip() in ["", "и", "или", ",", ".", ";", ":", "\n"]
    ):
        nodes.pop(0)
