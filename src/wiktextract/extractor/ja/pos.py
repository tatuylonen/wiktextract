from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .example import extract_example_list_item
from .header import extract_header_nodes
from .models import AltForm, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def parse_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    gloss_list_start = 0
    for list_index, list_node in level_node.find_child(NodeKind.LIST, True):
        if not list_node.sarg.endswith("#"):  # linkage list
            continue
        if gloss_list_start == 0:
            gloss_list_start = list_index
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            process_gloss_list_item(wxr, page_data[-1], list_item)
    extract_header_nodes(
        wxr, page_data[-1], level_node.children[:gloss_list_start]
    )
    if gloss_list_start == 0:
        page_data.pop()


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item_node: WikiNode,
    parent_gloss: str = "",
) -> None:
    gloss_nodes = list(
        list_item_node.invert_find_child(NodeKind.LIST, include_empty_str=True)
    )
    sense_data = Sense()
    find_form_of_data(wxr, word_entry, sense_data, list_item_node)
    if len(parent_gloss) > 0:
        sense_data.glosses.append(parent_gloss)
    gloss_only_nodes = []
    for gloss_node in gloss_nodes:
        if isinstance(gloss_node, TemplateNode):
            if gloss_node.template_name in ("context", "タグ"):
                # https://ja.wiktionary.org/wiki/テンプレート:context
                # https://ja.wiktionary.org/wiki/テンプレート:タグ
                for raw_tag in (
                    clean_node(wxr, sense_data, gloss_node)
                    .strip("()")
                    .split(",")
                ):
                    raw_tag = raw_tag.strip()
                    if len(raw_tag) > 0:
                        sense_data.raw_tags.append(raw_tag)
            elif gloss_node.template_name == "wikipedia-s":
                expanded_text = clean_node(wxr, None, gloss_node)
                gloss_only_nodes.append(
                    expanded_text.removesuffix("⁽ʷᵖ⁾").strip()
                )
            elif gloss_node.template_name == "wp":
                continue
            else:
                gloss_only_nodes.append(gloss_node)
        else:
            gloss_only_nodes.append(gloss_node)
    expanded_gloss = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(gloss_only_nodes), expand_all=True
    )
    ruby, no_ruby = extract_ruby(wxr, expanded_gloss.children)
    gloss_text = clean_node(wxr, sense_data, no_ruby)
    sense_data.ruby = ruby
    if len(gloss_text) > 0:
        sense_data.glosses.append(gloss_text)
        translate_raw_tags(sense_data)
        word_entry.senses.append(sense_data)

    for nest_gloss_list in list_item_node.find_child(NodeKind.LIST):
        if nest_gloss_list.sarg.endswith(("*", ":")):
            for example_list_item in nest_gloss_list.find_child(
                NodeKind.LIST_ITEM
            ):
                extract_example_list_item(
                    wxr, word_entry, sense_data, example_list_item
                )
        elif nest_gloss_list.sarg.endswith("#"):
            for nest_list_item in nest_gloss_list.find_child(
                NodeKind.LIST_ITEM
            ):
                process_gloss_list_item(
                    wxr, word_entry, nest_list_item, gloss_text
                )


def find_form_of_data(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item_node: WikiNode,
) -> None:
    for node in list_item_node.find_child(NodeKind.TEMPLATE):
        if node.template_name.endswith(" of"):
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node), expand_all=True
            )
            for link_node in expanded_node.find_child_recursively(
                NodeKind.LINK
            ):
                form_of = clean_node(wxr, None, link_node)
                if form_of != "":
                    sense.form_of.append(AltForm(word=form_of))
                    break
    if "form-of" in word_entry.tags and len(sense.form_of) == 0:
        for link_node in list_item_node.find_child(NodeKind.LINK):
            form_of = clean_node(wxr, None, link_node)
            if form_of != "":
                sense.form_of.append(AltForm(word=form_of))
                break


def extract_note_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    has_list = False
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        has_list = True
        note = clean_node(wxr, word_entry, list_item.children)
        if note != "":
            word_entry.notes.append(note)
    if not has_list:
        note = clean_node(
            wxr,
            word_entry,
            list(level_node.invert_find_child(LEVEL_KIND_FLAGS)),
        )
        if note != "":
            word_entry.notes.append(note)
