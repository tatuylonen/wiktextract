from typing import Optional

from mediawiki_langcodes import code_to_name
from wikitextprocessor import WikiNode
from wiktextract.extractor.es.models import Translation, WordEntry
from wiktextract.extractor.share import split_senseids
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_translation(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # Documentation: https://es.wiktionary.org/wiki/Plantilla:t+

    lang_code = template_node.template_parameters.get(1)  # Language code
    lang = code_to_name(lang_code, "es")
    if not lang:
        lang = f"Unknown({lang_code})"

    # Initialize variables
    current_translation: Optional[Translation] = None
    senseids: list[str] = []

    for key in template_node.template_parameters.keys():
        if key == 1:
            continue  # Skip language code

        value = clean_node(
            wxr, {}, template_node.template_parameters[key]
        ).strip()

        if isinstance(key, int):
            if value == ",":
                if current_translation:
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
                    current_translation.tags.append(value)
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
                        lang=lang,
                        senseids=list(senseids),
                    )
        elif isinstance(key, str):
            if key == "tr":
                if current_translation:
                    current_translation.roman = value

    # Add the last translation if it exists
    if current_translation:
        word_entry.translations.append(current_translation)
