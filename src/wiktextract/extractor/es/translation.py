import itertools

from mediawiki_langcodes import code_to_name
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "t":
            process_t_template(wxr, word_entry, template_node)


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
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:t
    lang_code = template_node.template_parameters.get(1, "")
    template_text = clean_node(wxr, word_entry, template_node)
    lang_name = template_text[: template_text.find(":")].strip("* ")
    if lang_name == "":  # in case Lua error
        lang_name = code_to_name(lang_code, "es")

    for tr_index in itertools.count(1):
        if "t" + str(tr_index) not in template_node.template_parameters:
            break
        tr_data = Translation(lang_code=lang_code, lang=lang_name, word="")
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

        if len(tr_data.word) > 0:
            translate_raw_tags(tr_data)
            word_entry.translations.append(tr_data)
