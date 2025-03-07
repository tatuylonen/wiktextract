import re

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import AltForm, Example, Form, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import translate_raw_tags


def extract_pos_section(
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

    gloss_list_index = len(level_node.children)
    for index, node in enumerate(level_node.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg == "#" or (
                    node.sarg == ":"
                    and len(list_item.children) > 0
                    and isinstance(list_item.children[0], str)
                    and re.search(r"\[\d+\]", list_item.children[0]) is not None
                ):
                    extract_gloss_list_item(wxr, page_data[-1], list_item)
                    if index < gloss_list_index:
                        gloss_list_index = index

    extract_pos_header_nodes(
        wxr, page_data[-1], level_node.children[:gloss_list_index]
    )
    translate_raw_tags(page_data[-1])


FORM_OF_TEMPLATES = {
    "çekim",
    "karşılaştırma",
    "Komp.",
    "artıklık",
    "üstünlük",
    "Sup.",
    "tr-çekim",
    "ad-hâl",
    "hâl",
    "çoğul ad",
    "çoğulu",
    "çoğul isim",
    "ota-çekim",
    "ikil ad",
    "ikil",
    "çoğul kısaltma",
    "el-ortaç çekimi",
    "kısaltma",
}


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense | None = None,
) -> None:
    sense = (
        parent_sense.model_copy(deep=True)
        if parent_sense is not None
        else Sense()
    )
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "terim",
        ]:
            extract_terim_template(wxr, sense, node)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in FORM_OF_TEMPLATES
        ):
            extract_form_of_template(wxr, word_entry, sense, node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss_str = clean_node(wxr, sense, gloss_nodes)
    gloss_str = re.sub(r"^\[\d+\]\s*", "", gloss_str)
    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)
        elif child_list.sarg.startswith(
            ("#", ":")
        ) and child_list.sarg.endswith((":", "*")):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                example = Example(text="")
                extract_example_list_item(
                    wxr, word_entry, child_list_item, example
                )
                if example.text != "":
                    sense.examples.append(example)


def extract_terim_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:terim
    raw_tags_str = clean_node(wxr, sense, t_node).strip("() ")
    for raw_tag in raw_tags_str.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)


def extract_pos_header_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    for node in nodes:
        if isinstance(node, TemplateNode) and (
            node.template_name.startswith((word_entry.lang_code + "-"))
            or node.template_name == "başlık başı"
        ):
            extract_pos_header_template(wxr, word_entry, node)


def extract_pos_header_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # Şablon:başlık_başı, Şablon:tr-ad
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    form_raw_tag = ""
    for node in expanded_node.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            form_raw_tag = clean_node(wxr, None, node)
        elif isinstance(node, HTMLNode) and node.tag == "b":
            word = clean_node(wxr, None, node)
            if word != "":
                form = Form(form=word)
                if form_raw_tag != "":
                    form.raw_tags.append(form_raw_tag)
                    translate_raw_tags(form)
                word_entry.forms.append(form)
        elif (
            isinstance(node, HTMLNode)
            and node.tag == "span"
            and "gender" in node.attrs.get("class", "")
        ):
            gender_raw_tag = clean_node(wxr, None, node)
            if gender_raw_tag != "":
                word_entry.raw_tags.append(gender_raw_tag)

    clean_node(wxr, word_entry, expanded_node)


def extract_form_of_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:çekim
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    if t_node.template_name == "kısaltma":
        sense.tags.append("abbreviation")
        for bold_node in expanded_node.find_child(NodeKind.BOLD):
            word = clean_node(wxr, None, bold_node)
            if word != "":
                sense.form_of.append(AltForm(word=word))
            break
    else:
        for i_tag in expanded_node.find_html_recursively("i"):
            word = clean_node(wxr, None, i_tag)
            if word != "":
                sense.form_of.append(AltForm(word=word))
            break

    sense.tags.append("form-of")
    clean_node(wxr, sense, expanded_node)
    if expanded_node.contain_node(NodeKind.LIST):
        for index, list_node in expanded_node.find_child(
            NodeKind.LIST, with_index=True
        ):
            gloss = clean_node(wxr, None, expanded_node.children[:index])
            if gloss != "":
                sense.glosses.append(gloss)
                translate_raw_tags(sense)
                word_entry.senses.append(sense)
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, list_item, sense)
            break
    else:
        gloss = clean_node(wxr, None, expanded_node)
        if gloss != "":
            sense.glosses.append(gloss)
            translate_raw_tags(sense)
            word_entry.senses.append(sense)
