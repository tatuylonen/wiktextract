from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import WikiNodeChildrenList

from wiktextract.extractor.ru.example import process_example_template
from wiktextract.extractor.ru.models import Sense, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

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
    wxr: WiktextractContext,
    word_entry: WordEntry,
    item_node: WikiNode,
):
    sense = Sense()

    raw_gloss_children: WikiNodeChildrenList = []
    clean_gloss_children: WikiNodeChildrenList = []
    tag_templates: list[WikiNode] = []
    note_templates: list[WikiNode] = []

    for child in item_node.children:
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

    if raw_gloss_children:
        raw_gloss = clean_node(wxr, {}, raw_gloss_children).strip()
        if raw_gloss:
            sense.raw_gloss = raw_gloss

    if clean_gloss_children:
        gloss = clean_node(wxr, {}, clean_gloss_children).strip()
        if gloss:
            sense.gloss = gloss

    for tag_template in tag_templates:
        # XXX: Expanded tags are mostly still abbreviations. In Wiktionary, however, they show the full word on hover. Perhaps it's possible to extract the full word from the template?
        tag = clean_node(wxr, {}, tag_template).strip()
        if tag:
            sense.tags.append(tag)

    for note_template in note_templates:
        note = clean_node(wxr, {}, note_template).strip()
        if note:
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
