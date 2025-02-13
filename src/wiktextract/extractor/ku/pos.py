import re
from itertools import count

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import extract_example_list_item
from .form_table import (
    extract_ku_tewîn_lk_template,
    extract_ku_tewîn_nav_template,
)
from .models import AltForm, Form, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import TAGS, translate_raw_tags


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
    for index, list_node in level_node.find_child(NodeKind.LIST, True):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if list_node.sarg.startswith("#") and list_node.sarg.endswith("#"):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
                if index < gloss_list_index:
                    gloss_list_index = index

    extract_pos_header_nodes(
        wxr, page_data[-1], level_node.children[:gloss_list_index]
    )


FORM_OF_TEMPLATES = frozenset(
    [
        "formeke peyvê",
        "inflection of",
        "dem2",
        "guherto",
        "guharto",
        "rastnivîs",
        "şaşnivîs",
        "şaşî",
        "kevnbûyî",
        "binêre",
        "bnr",
        "binêre2",
        "bnr2",
        "awayekî din",
        "ad",
        "komparatîv",
        "kom",
        "sûperlatîv",
        "sûp",
        "ku-dema-bê",
        "ku-dema-niha",
        "ku-fermanî",
        "dem",
        "dema-bê",
        "dema-fireh",
        "raboriya-sade",
        "rehê dema niha",
    ]
)


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
            "f",
            "ferhengok",
        ]:
            extract_ferhengok_template(wxr, sense, node)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in FORM_OF_TEMPLATES
        ):
            extract_form_of_template(wxr, sense, node)
            gloss_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

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


def extract_ferhengok_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:ferhengok
    node_str = clean_node(wxr, sense, t_node).strip("() ")
    for raw_tag in re.split(r",| an | û ", node_str):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            sense.raw_tags.append(raw_tag)


# https://ku.wiktionary.org/wiki/Alîkarî:Cureyên_peyvan
POS_HEADER_TEMPLATES = frozenset(
    [
        "navdêr",
        "serenav",
        "lêker",
        "rengdêr",
        "hoker",
        "cînav",
        "baneşan",
        "daçek",
        "pêşdaçek",
        "paşdaçek",
        "bazinedaçek",
        "girêdek",
        "artîkel",
        "pirtik",
        "navgir",
        "paşgir",
        "pêşgir",
        "reh",
        "biwêj",
        "hevok",
        "gp",
        "hejmar",
        "tîp",
        "sembol",
        "kurtenav",
    ]
)


def extract_pos_header_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    for node in nodes:
        if (
            isinstance(node, TemplateNode)
            and node.template_name in POS_HEADER_TEMPLATES
        ):
            form = Form(
                form=clean_node(
                    wxr, None, node.template_parameters.get("tr", "")
                ),
                tags=["romanization"],
            )
            if form.form not in ["", "-"]:
                word_entry.forms.append(form)
                clean_node(wxr, word_entry, node)
        if isinstance(node, TemplateNode) and node.template_name in [
            "navdêr",
            "serenav",
        ]:
            extract_navdêr_template(wxr, word_entry, node)
        elif isinstance(node, TemplateNode) and node.template_name == "lêker":
            extract_lêker_template(wxr, word_entry, node)
        elif isinstance(node, TemplateNode) and node.template_name in [
            "ku-tewîn-nav",
            "ku-tew-nav",
            "ku-tewîn-rd",
        ]:
            extract_ku_tewîn_nav_template(wxr, word_entry, node)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name == "ku-tewîn-lk"
        ):
            extract_ku_tewîn_lk_template(wxr, word_entry, node)


def extract_navdêr_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:navdêr
    # Şablon:serenav
    GENDERS = {
        "n": "masculine",
        "n+": "masculine-usually",
        "m": "feminine",
        "m+": "feminine-usually",
        "nt": "gender-neutral",
        "mn": ["feminine", "masculine"],
        "m/n": ["feminine", "masculine"],
        "g": "common-gender",
    }
    z_arg = clean_node(wxr, None, t_node.template_parameters.get("z", ""))
    if z_arg in GENDERS:
        tag = GENDERS[z_arg]
        if isinstance(tag, str):
            word_entry.tags.append(tag)
        elif isinstance(tag, list):
            word_entry.tags.extend(tag)
    NUMBERS = {
        "p": "plural",
        "p+": "plural-normally",
        "tp": "plural-only",
        "y": "singular",
        "nj": "uncountable",
        "j/nj": ["countable", "uncountable"],
    }
    j_arg = clean_node(wxr, None, t_node.template_parameters.get("j", ""))
    if j_arg in NUMBERS:
        tag = NUMBERS[j_arg]
        if isinstance(tag, str):
            word_entry.tags.append(tag)
        elif isinstance(tag, list):
            word_entry.tags.extend(tag)

    FORMS = {
        "m": "feminine",
        "n": "masculine",
        "nt": "gender-neutral",
        "y": "singular",
        "p": "plural",
        "np": ["masculine", "plural"],
        "mp": ["feminine", "plural"],
        "lk": "verb-from-noun",
    }
    for form_arg, tag in FORMS.items():
        if form_arg not in t_node.template_parameters:
            return
        extract_navdêr_template_form(wxr, word_entry, t_node, form_arg, tag)
        for index in count(2):
            form_arg += str(index)
            if form_arg not in t_node.template_parameters:
                break
            extract_navdêr_template_form(wxr, word_entry, t_node, form_arg, tag)


def extract_navdêr_template_form(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    arg_name: str,
    tag: str | list[str],
) -> None:
    if arg_name not in t_node.template_parameters:
        return
    form = Form(form=t_node.template_parameters[arg_name])
    if isinstance(tag, str):
        form.tags.append(tag)
    elif isinstance(tag, list):
        form.tags.extend(tag)
    if form.form != "":
        word_entry.forms.append(form)


def extract_lêker_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:lêker
    TAGS = {
        "gh": "transitive",
        "ngh": "intransitive",
        "x": "proper-noun",
        "p": "compound",
        "h": "compound",
        "b": "idiomatic",
    }
    c_arg_value = clean_node(wxr, None, t_node.template_parameters.get("c", ""))
    for c_arg in c_arg_value.split("-"):
        if c_arg in TAGS:
            word_entry.tags.append(TAGS[c_arg])
    FORM_TAGS = {
        "nd": "noun-from-verb",
        "niha": "present",
        "borî": "past",
        "subj": "subjunctive",
    }
    for form_arg, tag in FORM_TAGS.items():
        extract_lêker_template_form(wxr, word_entry, t_node, form_arg, tag)


def extract_lêker_template_form(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    arg_name: str,
    tag: str,
) -> None:
    if arg_name not in t_node.template_parameters:
        return
    form = Form(
        form=clean_node(wxr, None, t_node.template_parameters[arg_name]),
        tags=[tag],
        roman=clean_node(
            wxr, None, t_node.template_parameters.get(arg_name + "tr", "")
        ),
    )
    if form.form != "":
        word_entry.forms.append(form)
    if arg_name != "nd" and not arg_name.endswith("2"):
        extract_lêker_template_form(
            wxr, word_entry, t_node, arg_name + "2", tag
        )


def extract_form_of_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # Şablon:formeke peyvê
    match t_node.template_name:
        case "formeke peyvê" | "inflection of":
            form_args = ["cude", 3, 2]
        case (
            "dem2"
            | "guherto"
            | "guharto"
            | "rastnivîs"
            | "şaşnivîs"
            | "şaşî"
            | "kevnbûyî"
            | "binêre"
            | "bnr"
            | "binêre2"
            | "bnr2"
            | "awayekî din"
            | "ad"
            | "komparatîv"
            | "kom"
            | "sûperlatîv"
            | "sûp"
            | "dema-bê"
            | "dema-fireh"
            | "raboriya-sade"
        ):
            form_args = [2]
        case "ku-dema-bê" | "ku-dema-niha" | "ku-fermanî":
            form_args = [1]
        case "dem":
            form_args = [3]
        case "rehê dema niha":
            extract_rehê_dema_niha_template(wxr, sense, t_node)
            return
        case _:
            form_args = []
    for arg in form_args:
        form_str = clean_node(
            wxr, None, t_node.template_parameters.get(arg, "")
        )
        if form_str != "":
            sense.form_of.append(AltForm(word=form_str))
            if "form-of" not in sense.tags:
                sense.tags.append("form-of")
            if t_node.template_name in ["formeke peyvê", "inflection of"]:
                for tag_arg in count(4):
                    if tag_arg not in t_node.template_parameters:
                        break
                    raw_tag = clean_node(
                        wxr, None, t_node.template_parameters[tag_arg]
                    ).capitalize()
                    if raw_tag in TAGS:
                        tr_tag = TAGS[raw_tag]
                        if isinstance(tr_tag, str):
                            sense.tags.append(tr_tag)
                        elif isinstance(tr_tag, list):
                            sense.tags.extend(tr_tag)
            break


def extract_rehê_dema_niha_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for bold_node in expanded_node.find_child(NodeKind.BOLD):
        word = clean_node(wxr, None, bold_node)
        if word != "":
            sense.form_of.append(AltForm(word=word))
            if "form-of" not in sense.tags:
                sense.tags.append("form-of")
