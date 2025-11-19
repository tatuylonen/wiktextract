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
from ..ruby import extract_ruby
from .example import extract_example_list_item
from .linkage import (
    LINKAGE_TEMPLATES,
    extract_linkage_list_item,
    extract_linkage_template,
)
from .models import AltForm, Classifier, Form, Sense, WordEntry
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .sound import SOUND_TEMPLATES, extract_sound_template
from .tags import translate_raw_tags
from .translation import extract_translation_template


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    orig_title = pos_title
    pos_title = pos_title.removeprefix("보조 ").strip()
    if pos_title in POS_DATA:
        page_data[-1].pos_title = orig_title
        pos_data = POS_DATA[pos_title]
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))
        if (
            orig_title.startswith("보조 ")
            and "auxiliary" not in page_data[-1].tags
        ):
            page_data[-1].tags.append("auxiliary")

    has_linkage = False
    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if isinstance(node, TemplateNode):
            if node.template_name in SOUND_TEMPLATES:
                extract_sound_template(wxr, page_data[-1], node)
            elif node.template_name in LINKAGE_TEMPLATES:
                has_linkage = extract_linkage_template(
                    wxr, page_data[-1], node, "derived"
                )
            elif node.template_name == "외국어":
                extract_translation_template(
                    wxr,
                    page_data[-1],
                    node,
                    page_data[-1].senses[-1].glosses[-1]
                    if len(page_data[-1].senses) > 0
                    else "",
                )
            elif node.template_name.startswith(
                base_data.lang_code + "-"
            ) or node.template_name.endswith((" 동사", " 명사", " 고유명사")):
                extract_headword_line_template(wxr, page_data[-1], node)
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#") and node.sarg.endswith("#"):
                    extract_gloss_list_item(
                        wxr,
                        page_data[-1],
                        list_item,
                        Sense(pattern=page_data[-1].pattern),
                    )
                else:
                    extract_unorderd_list_item(wxr, page_data[-1], list_item)

    if not (
        len(page_data[-1].senses) > 0
        or len(page_data[-1].sounds) > len(base_data.sounds)
        or len(page_data[-1].translations) > len(base_data.translations)
        or has_linkage
    ):
        page_data.pop()


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    parent_sense: Sense,
) -> None:
    gloss_nodes = []
    sense = parent_sense.model_copy(deep=True)
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            gloss_text = clean_node(wxr, sense, gloss_nodes)
            if len(gloss_text) > 0:
                sense.glosses.append(gloss_text)
                translate_raw_tags(sense)
                word_entry.senses.append(sense)
                gloss_nodes.clear()
            for nested_list_item in node.find_child(NodeKind.LIST_ITEM):
                if node.sarg.startswith("#") and node.sarg.endswith("#"):
                    extract_gloss_list_item(
                        wxr, word_entry, nested_list_item, sense
                    )
                else:
                    extract_unorderd_list_item(
                        wxr, word_entry, nested_list_item
                    )
            continue
        elif isinstance(node, TemplateNode) and node.template_name.endswith(
            " of"
        ):
            extract_form_of_template(wxr, sense, node)
            gloss_nodes.append(node)
        elif isinstance(node, TemplateNode) and node.template_name == "라벨":
            sense.raw_tags.extend(
                [
                    raw_tag.strip()
                    for raw_tag in clean_node(wxr, sense, node)
                    .strip("()")
                    .split(",")
                ]
            )
        elif isinstance(node, TemplateNode) and node.template_name == "zh-mw":
            extract_zh_mw_template(wxr, node, sense)
        else:
            gloss_nodes.append(node)

    gloss_text = clean_node(wxr, sense, gloss_nodes)
    if len(gloss_text) > 0:
        sense.glosses.append(gloss_text)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def extract_unorderd_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    is_first_bold = True
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.BOLD
            and is_first_bold
        ):
            # `* '''1.''' gloss text`, terrible obsolete layout
            is_first_bold = False
            bold_text = clean_node(wxr, None, node)
            if re.fullmatch(r"\d+(?:-\d+)?\.?", bold_text):
                new_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
                new_list_item.children = list_item.children[index + 1 :]
                extract_gloss_list_item(wxr, word_entry, new_list_item, Sense())
                break
        elif isinstance(node, str) and "어원:" in node:
            etymology_nodes = []
            etymology_nodes.append(node[node.index(":") + 1 :])
            etymology_nodes.extend(list_item.children[index + 1 :])
            e_text = clean_node(wxr, None, etymology_nodes)
            if len(e_text) > 0:
                word_entry.etymology_texts.append(e_text)
            break
        elif (
            isinstance(node, str)
            and re.search(r"(?:참고|참조|활용):", node) is not None
        ):
            note_str = node[node.index(":") + 1 :].strip()
            note_str += clean_node(
                wxr,
                word_entry.senses[-1]
                if len(word_entry.senses) > 0
                else word_entry,
                list_item.children[index + 1 :],
            )
            if len(word_entry.senses) > 0:
                word_entry.senses[-1].note = note_str
            else:
                word_entry.note = note_str
            break
        elif (
            isinstance(node, str)
            and ":" in node
            and node[: node.index(":")].strip() in LINKAGE_SECTIONS
        ):
            extract_linkage_list_item(wxr, word_entry, list_item, "", False)
            break
        elif isinstance(node, str) and "문형:" in node:
            word_entry.pattern = node[node.index(":") + 1 :].strip()
            word_entry.pattern += clean_node(
                wxr, None, list_item.children[index + 1 :]
            )
            break
    else:
        if len(word_entry.senses) > 0:
            extract_example_list_item(
                wxr, word_entry.senses[-1], list_item, word_entry.lang_code
            )


def extract_form_of_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    if "form-of" not in sense.tags:
        sense.tags.append("form-of")
    word_arg = 1 if t_node.template_name == "ko-hanja form of" else 2
    word = clean_node(wxr, None, t_node.template_parameters.get(word_arg, ""))
    if len(word) > 0:
        sense.form_of.append(AltForm(word=word))


def extract_grammar_note_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        word_entry.note = clean_node(wxr, None, list_item.children)


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
                    classifier.tags.append("Traditional-Chinese")
                elif span_class == "Hans":
                    classifier.tags.append("Simplified-Chinese")

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
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for main_span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="headword-line"
    ):
        i_tags = []
        for html_node in main_span_tag.find_child(NodeKind.HTML):
            class_names = html_node.attrs.get("class", "").split()
            if html_node.tag == "strong" and "headword" in class_names:
                ruby, no_ruby = extract_ruby(wxr, html_node)
                strong_str = clean_node(wxr, None, no_ruby)
                if strong_str not in ["", wxr.wtp.title] or len(ruby) > 0:
                    forms.append(
                        Form(form=strong_str, tags=["canonical"], ruby=ruby)
                    )
            elif html_node.tag == "span":
                if "headword-tr" in class_names or "tr" in class_names:
                    roman = clean_node(wxr, None, html_node)
                    if roman != "":
                        if len(forms) == 0:
                            forms.append(
                                Form(form=roman, tags=["romanization"])
                            )
                        else:
                            forms[-1].roman = roman
                elif "gender" in class_names:
                    for abbr_tag in html_node.find_html("abbr"):
                        gender_tag = clean_node(wxr, None, abbr_tag)
                        if len(forms) > 0 and "canonical" not in forms[-1].tags:
                            forms[-1].raw_tags.append(gender_tag)
                            translate_raw_tags(forms[-1])
                        else:
                            word_entry.raw_tags.append(gender_tag)
            elif html_node.tag == "i":
                if len(i_tags) > 0:
                    word_entry.raw_tags.extend(i_tags)
                i_tags.clear()
                for i_child in html_node.children:
                    raw_tag = clean_node(wxr, None, i_child)
                    if raw_tag != "":
                        i_tags.append(raw_tag)
            elif html_node.tag == "b":
                ruby, no_ruby = extract_ruby(wxr, html_node)
                for form_str in filter(
                    None,
                    map(str.strip, clean_node(wxr, None, no_ruby).split(",")),
                ):
                    form = Form(form=form_str, ruby=ruby, raw_tags=i_tags)
                    translate_raw_tags(form)
                    forms.append(form)
                i_tags.clear()

        if len(i_tags) > 0:
            word_entry.raw_tags.extend(i_tags)
    word_entry.forms.extend(forms)
    clean_node(wxr, word_entry, expanded_node)
    translate_raw_tags(word_entry)
