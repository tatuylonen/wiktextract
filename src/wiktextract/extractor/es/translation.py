import itertools
import re

from mediawiki_langcodes import code_to_name
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    tr_data = []
    cats = []
    sense = ""
    sense_index = ""
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "t":
            new_tr_list, new_cats = process_t_template(
                wxr, t_node, sense, sense_index
            )
            tr_data.extend(new_tr_list)
            cats.extend(new_cats)
        elif t_node.template_name == "trad-arriba":
            sense = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
            m = re.match(r"\[([\d.a-z]+)\]", sense)
            if m is not None:
                sense_index = m.group(1)
                sense = sense[m.end() :].strip()

    for data in page_data:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.etymology_text == page_data[-1].etymology_text
        ):
            data.translations.extend(tr_data)
            data.categories.extend(cats)


# https://es.wiktionary.org/wiki/Módulo:t
T_GENDERS = {
    "m": "masculine",
    "f": "feminine",
    "mf": ["masculine", "feminine"],
    "n": "neuter",
    "c": "common",
}
T_NUMBERS = {
    "s": "singular",
    "sg": "singular",
    "p": "plural",
    "pl": "plural",
    "d": "dual",
    "du": "dual",
}


def process_t_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    sense_index: str,
) -> tuple[list[Translation], list[str]]:
    # https://es.wiktionary.org/wiki/Plantilla:t
    tr_list = []
    cats = {}
    lang_code = template_node.template_parameters.get(1, "")
    template_text = clean_node(wxr, cats, template_node)
    lang_name = template_text[: template_text.find(":")].strip("* ")
    if lang_name == "":  # in case Lua error
        lang_name = code_to_name(lang_code, "es")

    for tr_index in itertools.count(1):
        if "t" + str(tr_index) not in template_node.template_parameters:
            break
        tr_data = Translation(
            lang_code=lang_code,
            lang=lang_name,
            word="",
            sense=sense,
            sense_index=sense_index,
        )
        for param_prefix, field in (
            ("t", "word"),
            ("a", "sense_index"),
            ("tl", "roman"),
            ("nota", "raw_tags"),
            ("g", "tags"),
            ("n", "tags"),
        ):
            param = param_prefix + str(tr_index)
            if param not in template_node.template_parameters:
                continue
            value = clean_node(
                wxr, None, template_node.template_parameters[param]
            )
            if param_prefix == "g":
                value = T_GENDERS.get(value)
            elif param_prefix == "n":
                value = T_NUMBERS.get(value)
            elif param_prefix == "a" and value != "":
                sense_index = value
            if value is None:
                continue

            pre_value = getattr(tr_data, field)
            if isinstance(pre_value, list):
                if isinstance(value, list):
                    pre_value.extend(value)
                else:
                    pre_value.append(value)
            else:
                setattr(tr_data, field, value)

        if tr_data.sense_index == "" and sense_index != "":
            # usually only first word has index param
            tr_data.sense_index = sense_index

        if len(tr_data.word) > 0:
            translate_raw_tags(tr_data)
            tr_list.append(tr_data)
    return tr_list, cats.get("categories", [])
