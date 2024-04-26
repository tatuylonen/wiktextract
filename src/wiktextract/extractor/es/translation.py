import itertools
from typing import Optional

from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import split_senseids
from .models import Translation, WordEntry


def extract_translation(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
):
    if template_node.template_name == "t":
        process_t_template(wxr, word_entry, template_node)
    elif template_node.template_name == "t+":
        process_t_plus_template(wxr, word_entry, template_node)


T_GENDERS = {
    "m": "masculine",
    "f": "feminine",
    "mf": ["masculine", "feminine"],
    "n": "neuter",
}
T_NUMBERS = {
    "s": "singular",
    "p": "plural",
    "d": "dual",
}


def process_t_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:t
    lang_code = template_node.template_parameters.get(1, "")
    template_text = clean_node(wxr, word_entry, template_node)
    lang_name = template_text[: template_text.find(":")].strip("* ")

    for tr_index in itertools.count(1):
        if "t" + str(tr_index) not in template_node.template_parameters:
            break
        tr_data = Translation(lang_code=lang_code, lang=lang_name, word="")
        for param_prefix, field in (
            ("t", "word"),
            ("a", "senseids"),
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
            word_entry.translations.append(tr_data)


def process_t_plus_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # obsolete template: https://es.wiktionary.org/wiki/Plantilla:t+

    lang_code = template_node.template_parameters.get(1)
    template_text = clean_node(wxr, word_entry, template_node)
    lang_name = template_text[: template_text.find(":")].strip("* ")

    # Initialize variables
    current_translation: Optional[Translation] = None
    senseids: list[str] = []

    for key in template_node.template_parameters.keys():
        if key == 1:
            continue  # Skip language code

        value = clean_node(wxr, None, template_node.template_parameters[key])
        if isinstance(key, int):
            if value == ",":
                if (
                    current_translation is not None
                    and len(current_translation.word) > 0
                ):
                    word_entry.translations.append(current_translation)

                current_translation = None
                senseids = []
            elif (
                value.isdigit()
                or (value != "," and "," in value)
                or "-" in value
            ):
                # This gives the senseids
                senseids.extend(split_senseids(value))
            elif value in [
                "m",
                "f",
                "mf",
                "n",
                "c",
                "p",
                "adj",
                "sust",
                "adj y sust",
            ]:
                if current_translation:
                    current_translation.raw_tags.append(value)
            elif value in ["nota", "tr", "nl"]:
                continue
            elif (
                key > 2
                and isinstance(
                    template_node.template_parameters.get(key - 1), str
                )
                and template_node.template_parameters.get(key - 1) == "nota"
            ):
                if current_translation:
                    current_translation.notes.append(value)
            elif (
                key > 2
                and isinstance(
                    template_node.template_parameters.get(key - 1), str
                )
                and template_node.template_parameters.get(key - 1) == "tr"
            ):
                if current_translation:
                    current_translation.roman = value
            elif value != ",":
                # This is a word
                if current_translation:
                    current_translation.word += " " + value

                else:
                    current_translation = Translation(
                        word=value,
                        lang_code=lang_code,
                        lang=lang_name,
                        senseids=list(senseids),
                    )
        elif isinstance(key, str):
            if key == "tr":
                if current_translation:
                    current_translation.roman = value

    # Add the last translation if it exists
    if current_translation is not None and len(current_translation.word) > 0:
        word_entry.translations.append(current_translation)
