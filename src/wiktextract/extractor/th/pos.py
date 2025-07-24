import itertools
import re

from wikitextprocessor import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .models import AltForm, Classifier, Form, Sense, WordEntry
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
        elif isinstance(node, TemplateNode):
            extract_headword_line_template(wxr, page_data[-1], node)


# redirect
ALT_OF_TEMPLATES = frozenset(["altform", "alt form", "alt sp", "altsp"])
FORM_OF_TEMPLATES = frozenset(["อักษรย่อ", "คำย่อ"])


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
    has_form_of_template = False
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
            or node.template_name in FORM_OF_TEMPLATES
        ):
            extract_form_of_template(wxr, word_entry, sense, node)
            has_form_of_template = True
        elif isinstance(node, TemplateNode) and node.template_name == "zh-mw":
            extract_zh_mw_template(wxr, node, sense)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    if not has_form_of_template:
        gloss_str = clean_node(wxr, sense, gloss_nodes)
        if gloss_str != "":
            sense.glosses.append(gloss_str)
            translate_raw_tags(sense)
            word_entry.senses.append(sense)

    for child_list in list_item.find_child(NodeKind.LIST):
        if child_list.sarg.startswith("#") and child_list.sarg.endswith(
            (":", "*")
        ):
            for e_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(wxr, word_entry, sense, e_list_item)
        elif child_list.sarg.startswith("#") and child_list.sarg.endswith("#"):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, word_entry, child_list_item, sense)


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
        for raw_tag in re.split(r",| หรือ ", span_str):
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
            sense.classifiers.append(Classifier(classifier=cls))
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
            word_entry.classifiers.append(Classifier(classifier=cls))

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
    word_entry: WordEntry,
    first_sense: Sense,
    t_node: TemplateNode,
) -> None:
    form = AltForm(word="")
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    senses = []
    if expanded_node.contain_node(NodeKind.LIST):
        first_list_idx = len(expanded_node.children)
        first_gloss = ""
        for index, node in enumerate(expanded_node.children):
            if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                if index < first_list_idx:
                    first_list_idx = index
                    first_gloss = clean_node(
                        wxr, first_sense, expanded_node.children[:index]
                    )
                    if first_gloss != "":
                        first_sense.glosses.append(first_gloss)
                        senses.append(first_sense)
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    sense = Sense()
                    if first_gloss != "":
                        sense.glosses.append(first_gloss)
                    gloss = clean_node(wxr, sense, list_item.children)
                    if gloss != "":
                        sense.glosses.append(gloss)
                        senses.append(sense)
    else:
        gloss = clean_node(wxr, first_sense, expanded_node)
        if gloss != "":
            first_sense.glosses.append(gloss)
            senses.append(first_sense)

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
        for sense in senses:
            if is_alt_of:
                sense.alt_of.append(form)
            else:
                sense.form_of.append(form)
            if is_alt_of and "alt-of" not in sense.tags:
                sense.tags.append("alt-of")
            if not is_alt_of and "form-of" not in sense.tags:
                sense.tags.append("form-of")
    word_entry.senses.extend(senses)


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


def extract_zh_mw_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: Sense
) -> None:
    # Chinese inline classifier template
    # copied from zh edition code
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    classifiers = []
    last_word = ""
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if span_class in ["Hani", "Hant", "Hans"]:
            word = clean_node(wxr, None, span_tag)
            if word != "／":
                classifier = Classifier(classifier=word)
                if span_class == "Hant":
                    classifier.tags.append("Traditional Chinese")
                elif span_class == "Hans":
                    classifier.tags.append("Simplified Chinese")

                if len(classifiers) > 0 and last_word != "／":
                    sense.classifiers.extend(classifiers)
                    classifiers.clear()
                classifiers.append(classifier)
            last_word = word
        elif "title" in span_tag.attrs:
            raw_tag = clean_node(wxr, None, span_tag.attrs["title"])
            if len(raw_tag) > 0:
                for classifier in classifiers:
                    classifier.raw_tags.append(raw_tag)
    sense.classifiers.extend(classifiers)
    for classifier in sense.classifiers:
        translate_raw_tags(classifier)


def extract_headword_line_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for main_span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="headword-line"
    ):
        for strong_tag in main_span_tag.find_html(
            "strong", attr_name="class", attr_value="headword"
        ):
            strong_str = clean_node(wxr, None, strong_tag)
            if strong_str not in ["", wxr.wtp.title]:
                word_entry.forms.append(
                    Form(form=strong_str, tags=["canonical"])
                )
        for roman_span in main_span_tag.find_html(
            "span", attr_name="class", attr_value="headword-tr"
        ):
            roman = clean_node(wxr, None, roman_span)
            if roman != "":
                word_entry.forms.append(
                    Form(form=roman, tags=["transliteration"])
                )
        for gender_span in main_span_tag.find_html(
            "span", attr_name="class", attr_value="gender"
        ):
            for abbr_tag in gender_span.find_html("abbr"):
                word_entry.raw_tags.append(clean_node(wxr, None, abbr_tag))
        form_raw_tag = ""
        for html_tag in main_span_tag.find_child(NodeKind.HTML):
            if html_tag.tag == "i":
                form_raw_tag = clean_node(wxr, None, html_tag)
            elif html_tag.tag == "b":
                form_str = clean_node(wxr, None, html_tag)
                if form_str != "":
                    form = Form(form=form_str)
                    if form_raw_tag != "":
                        form.raw_tags.append(form_raw_tag)
                        translate_raw_tags(form)
                    word_entry.forms.append(form)

    clean_node(wxr, word_entry, expanded_node)
    translate_raw_tags(word_entry)
