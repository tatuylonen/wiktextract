from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import WikiNodeChildrenList

from wiktextract.extractor.ru.example import process_example_template
from wiktextract.extractor.ru.models import Sense, WordEntry
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

TAGS_TEMPLATE_NAMES = {
    # XXX: This list is incomplete. There are many more tag templates. Perhaps it would be better to assume all templates that are not recognized as something else are tags?
    "жарг.",
    "зоол.",
    "искусств.",
    "истор.",
    "ихтиол.",
    "книжн.",
    "кулин.",
    "ласк.",
    "лингв.",
    "матем.",
    "мед.",
    "минер.",
    "минерал.",
    "миф.",
    "мифол.",
    "неодобр.",
    "п.",
    "перен.",
    "полит.",
    "поэт.",
    "пренебр.",
    "прост.",
    "разг.",
    "религ.",
    "техн.",
    "устар.",
    "фарм.",
    "физ.",
    "физиол.",
    "филол.",
    "филос.",
    "фолькл.",
    "хим.",
    "церк.",
    "шутл.",
    "эвф.",
    "экон.",
    "юр.",
}


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
                process_example_template(wxr, word_entry, child)

            elif child.template_name in TAGS_TEMPLATE_NAMES:
                tag_templates.append(child)
                raw_gloss_children.append(child)

            elif child.template_name == "помета":
                note_templates.append(child)
                raw_gloss_children.append(child)

            else:
                clean_gloss_children.append(child)
                raw_gloss_children.append(child)

                wxr.wtp.debug(
                    f"Found template '{child.template_name}' in gloss that could be a tag",
                    sortid="extractor/ru/gloss/extract_gloss/75",
                )
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
