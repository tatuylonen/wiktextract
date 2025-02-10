import itertools

from wikitextprocessor import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import AltForm, Form, Sense, WordEntry
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
    base_data.pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))

    gloss_list_index = len(level_node.children)
    for index, list_node in level_node.find_child(NodeKind.LIST, True):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if list_node.sarg.startswith("#") and list_node.sarg.endswith("#"):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
                if index < gloss_list_index:
                    gloss_list_index = index

    for node in level_node.children[:gloss_list_index]:
        if isinstance(node, TemplateNode) and node.template_name == "th-noun":
            extract_th_noun_template(wxr, page_data[-1], node)
        elif isinstance(node, TemplateNode) and node.template_name in [
            "th-verb",
            "th-adj",
        ]:
            extract_th_verb_adj_template(wxr, page_data[-1], node)


# redirect
ALT_OF_TEMPLATES = frozenset(["altform", "alt form", "alt sp", "altsp"])


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    sense = Sense()
    gloss_nodes = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "label",
            "lb",
            "lbl",
        ]:
            extract_label_template(wxr, sense, node)
        elif isinstance(node, TemplateNode) and node.template_name == "cls":
            extract_cls_template(wxr, sense, node)
        elif isinstance(node, TemplateNode) and (
            node.template_name.endswith(" of")
            or node.template_name.startswith("alternate ")
            or node.template_name in ALT_OF_TEMPLATES
        ):
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node), expand_all=True
            )
            extract_form_of_template(wxr, sense, expanded_node, node)
            gloss_nodes.append(expanded_node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss_str = clean_node(wxr, sense, gloss_nodes)
    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for e_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, word_entry, sense, e_list_item)

    if gloss_str != "":
        sense.glosses.append(gloss_str)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def extract_label_template(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    # https://th.wiktionary.org/wiki/แม่แบบ:label
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="ib-content"
    ):
        span_str = clean_node(wxr, None, span_tag)
        for raw_tag in span_str.split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                sense.raw_tags.append(raw_tag)
    clean_node(wxr, sense, expanded_node)


def extract_cls_template(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    # https://th.wiktionary.org/wiki/แม่แบบ:cls
    for arg_name in itertools.count(2):
        if arg_name not in t_node.template_parameters:
            break
        cls = clean_node(wxr, None, t_node.template_parameters[arg_name])
        if cls != "":
            sense.classifiers.append(cls)
    clean_node(wxr, sense, t_node)


def extract_th_noun_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://th.wiktionary.org/wiki/แม่แบบ:th-noun
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for b_tag in expanded_node.find_html_recursively("b"):
        cls = clean_node(wxr, None, b_tag)
        if cls != "":
            word_entry.classifiers.append(cls)

    clean_node(wxr, word_entry, expanded_node)


def extract_th_verb_adj_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://th.wiktionary.org/wiki/แม่แบบ:th-noun
    # https://th.wiktionary.org/wiki/แม่แบบ:th-adj
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for b_tag in expanded_node.find_html_recursively("b"):
        form_str = clean_node(wxr, None, b_tag)
        if form_str != "":
            word_entry.forms.append(
                Form(
                    form=form_str,
                    tags=[
                        "abstract-noun"
                        if t_node.template_name == "th-verb"
                        else "noun-from-adj"
                    ],
                )
            )

    clean_node(wxr, word_entry, expanded_node)


def extract_note_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            note_str = clean_node(
                wxr,
                word_entry,
                list(list_item.invert_find_child(NodeKind.LIST)),
            )
            if note_str != "":
                word_entry.notes.append(note_str)


def extract_form_of_template(
    wxr: WiktextractContext,
    sense: Sense,
    expanded_node: WikiNode,
    t_node: TemplateNode,
) -> None:
    form = AltForm(word="")
    for i_tag in expanded_node.find_html_recursively("i"):
        form.word = clean_node(wxr, None, i_tag)
        break
    for span_tag in expanded_node.find_html_recursively("span"):
        if "mention-tr" in span_tag.attrs.get("class", ""):
            form.roman = clean_node(wxr, None, span_tag)
            break
    is_alt_of = (
        t_node.template_name.startswith(("alternative ", "alternate "))
        or t_node.template_name in ALT_OF_TEMPLATES
    )
    if form.word != "":
        if is_alt_of:
            sense.alt_of.append(form)
        else:
            sense.form_of.append(form)
        if is_alt_of and "alt-of" not in sense.tags:
            sense.tags.append("alt-of")
        if not is_alt_of and "form-of" not in sense.tags:
            sense.tags.append("form-of")


def extract_usage_note_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            note_str = clean_node(wxr, None, list_item.children)
            if note_str != "":
                word_entry.notes.append(note_str)
