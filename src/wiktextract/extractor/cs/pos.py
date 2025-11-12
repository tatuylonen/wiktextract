from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import AltForm, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
):
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    base_data.pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))
    has_child_section = level_node.contain_node(LEVEL_KIND_FLAGS)

    for list_node in level_node.find_child(NodeKind.LIST):
        if list_node.sarg != "*":
            continue
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if has_child_section:
                for italic_node in list_item.find_child(NodeKind.ITALIC):
                    italic_str = clean_node(wxr, None, italic_node)
                    for raw_tag in italic_str.split():
                        if raw_tag not in ["", "rod"]:
                            page_data[-1].raw_tags.append(raw_tag)
            else:
                for link_node in list_item.find_child(NodeKind.LINK):
                    word = clean_node(wxr, None, link_node)
                    if word != "":
                        page_data[-1].senses.append(
                            Sense(
                                glosses=[
                                    clean_node(wxr, None, list_item.children)
                                ],
                                tags=["form-of"],
                                form_of=[AltForm(word=word)],
                            )
                        )
                        if "form-of" not in page_data[-1]:
                            page_data[-1].tags.append("form-of")
                        break

    translate_raw_tags(page_data[-1])


def extract_sense_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        if list_node.sarg != "#":
            continue
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_gloss_list_item(wxr, word_entry, list_item)


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
):
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "Příznaky":
            extract_příznaky_template(wxr, sense, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            raw_tags = clean_node(wxr, None, node)
            if raw_tags.startswith("(") and raw_tags.endswith(")"):
                for raw_tag in raw_tags.strip("() ").split(","):
                    raw_tag = raw_tag.strip()
                    if raw_tag != "":
                        sense.raw_tags.append(raw_tag)
            elif node.contain_node(NodeKind.LINK):
                gloss_nodes.append(node)
                link_nodes = list(
                    node.find_child(NodeKind.LINK, with_index=True)
                )
                if (
                    len(link_nodes) == 1
                    and link_nodes[0][0] != 0
                    and link_nodes[0][0] == len(node.children) - 1
                ):
                    word = clean_node(wxr, None, link_nodes[0][1])
                    if word != "":
                        sense.form_of.append(AltForm(word=word))
                        sense.tags.append("form-of")
                    break
            else:
                gloss_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss = clean_node(wxr, sense, gloss_nodes)
    if gloss != "":
        sense.glosses.append(gloss)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)
        elif child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, sense, child_list_item)


def extract_příznaky_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    # https://cs.wiktionary.org/wiki/Šablona:Příznaky
    text = clean_node(wxr, sense, t_node).strip("() ")
    for raw_tag in text.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)


def extract_note_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    word_entry.note = clean_node(
        wxr,
        word_entry,
        list(level_node.invert_find_child(LEVEL_KIND_FLAGS, True)),
    )
