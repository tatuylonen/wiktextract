import re
from collections import defaultdict
from typing import Dict, List, Union

from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_translation(
    wxr: WiktextractContext, page_data: List[Dict], level_node: WikiNode
) -> None:
    for level_node_child in level_node.filter_empty_str_child():
        if not (
            isinstance(level_node_child, WikiNode)
            and level_node_child.kind == NodeKind.TEMPLATE
            and level_node_child.template_name == "Ü-Tabelle"
        ):
            wxr.wtp.debug(
                f"Unexpected node type in extract_translation: {level_node_child}",
                sortid="extractor/de/translation/extract_translation/31",
            )
        else:
            sense_translations = []
            base_translation_data = defaultdict(list)
            senseid = level_node_child.template_parameters.get(1)
            if senseid == None:
                # XXX: Sense-disambiguate where senseids are in Ü-Liste (ca. 0.03% of pages), e.g.:
                # https://de.wiktionary.org/wiki/Beitrag
                # """
                # {{Ü-Tabelle|Ü-Liste=
                # *{{en}}: [1] {{Ü|en|subscription}}; [1a] {{Ü|en|dues}}, {{Ü|en|membership fee}}; [1, 2] {{Ü|en|contribution}}; [3] {{Ü|en|article}}}}
                pass

            sense_text = level_node_child.template_parameters.get("G")

            if sense_text:
                sense_text = clean_node(wxr, {}, sense_text).strip()
                if sense_text == "Übersetzungen umgeleitet":
                    # XXX: Handle cases where translations are in a separate page (ca. 1.1% of pages), e.g.:
                    # https://de.wiktionary.org/wiki/Pöpke
                    # """
                    # {{Ü-Tabelle|*|G=Übersetzungen umgeleitet|Ü-Liste=
                    # :{{Übersetzungen umleiten|1|Poppe}}
                    # }}
                    # """
                    continue

                base_translation_data["sense"] = clean_node(wxr, {}, sense_text)

            translation_list = level_node_child.template_parameters.get(
                "Ü-Liste"
            )
            if translation_list:
                process_translation_list(
                    wxr,
                    sense_translations,
                    base_translation_data,
                    translation_list,
                )

            dialect_table = level_node_child.template_parameters.get(
                "Dialekttabelle"
            )
            if dialect_table:
                process_dialect_table(wxr, base_translation_data, dialect_table)

            matched_senseid = False
            if senseid:
                for sense in page_data[-1]["senses"]:
                    if sense["senseid"] == senseid.strip():
                        sense["translations"].extend(sense_translations)
                        matched_senseid = True

            if not matched_senseid:
                wxr.wtp.debug(
                    f"Unknown senseid: {senseid}.",
                    sortid="extractor/de/translation/extract_translation/65",
                )
                page_data[-1]["translations"].extend(sense_translations)


def process_translation_list(
    wxr: WiktextractContext,
    sense_translations: List[Dict],
    base_translation_data: Dict[str, List],
    translation_list: List[Union[WikiNode, str]],
):
    modifiers = []
    for node in translation_list:
        if not is_translation_template(node):
            modifiers.append(node)

        else:
            translation_data = base_translation_data.copy()
            process_modifiers(
                wxr, sense_translations, translation_data, modifiers
            )

            lang_code = node.template_parameters.get(1)
            translation_data["code"] = lang_code
            translation_data["lang"] = code_to_name(lang_code, "de")
            if translation_data["lang"] == "":
                wxr.wtp.debug(
                    f"Unknown language code: {translation_data['lang']}",
                    sortid="extractor/de/translation/process_translation_list/70",
                )
            if node.template_name[-1] == "?":
                translation_data["uncertain"] = True

            translation_data["word"] = clean_node(
                wxr, {}, node.template_parameters.get(2)
            )

            if node.template_name.removesuffix("?") == "Ü":
                process_Ü_template(wxr, translation_data, node)

            if node.template_name.removesuffix("?") == "Üt":
                process_Üt_template(wxr, translation_data, node)

            sense_translations.append(translation_data)
    # Process modifiers at the end of the list
    process_modifiers(wxr, sense_translations, defaultdict, modifiers)


def is_translation_template(node: any) -> bool:
    return (
        isinstance(node, WikiNode)
        and node.kind == NodeKind.TEMPLATE
        and node.template_name in ["Ü", "Üt", "Ü?", "Üt?"]
    )


def process_Ü_template(
    wxr: WiktextractContext,
    translation_data: Dict[str, Union[str, List, bool]],
    template_node: TemplateNode,
):
    overwrite_word(
        wxr, translation_data, template_node.template_parameters.get(3)
    )


def process_Üt_template(
    wxr: WiktextractContext,
    translation_data: Dict[str, Union[str, List, bool]],
    template_node: TemplateNode,
):
    transcription = template_node.template_parameters.get(3)
    if transcription:
        translation_data["roman"] = clean_node(wxr, {}, transcription)
    # Look for automatic transcription
    else:
        cleaned_node = clean_node(wxr, {}, template_node)
        match = re.search(r"\(([^)]+?)\^\☆\)", cleaned_node)

        if match:
            translation_data["roman"] = match.group(1)

    overwrite_word(
        wxr, translation_data, template_node.template_parameters.get(4)
    )


def overwrite_word(
    wxr: WiktextractContext,
    translation_data: Dict[str, Union[str, List, bool]],
    nodes: Union[List[Union[WikiNode, str]], WikiNode, str, None],
):
    if nodes == None:
        return
    overwrite_word = clean_node(wxr, {}, nodes).strip()
    if overwrite_word:
        translation_data["word"] = overwrite_word


def process_modifiers(
    wxr: WiktextractContext,
    sense_translations: List[Dict],
    translation_data: Dict[str, Union[str, List, bool]],
    modifiers,
):
    # Get rid of the "*" and language template nodes that start each translation
    for i, elem in enumerate(modifiers):
        if isinstance(elem, str) and "*" in elem:
            del modifiers[i:]
            break

    clean_text = clean_node(wxr, {}, modifiers).strip()
    if clean_text:
        tags = re.split(r";|,|\(|\)|:", clean_text)
        tags = [tag.strip() for tag in tags if tag.strip()]
        if tags:
            if clean_text.endswith(":"):
                translation_data["tags"].extend(tags)
            elif sense_translations:
                sense_translations[-1]["tags"].extend(tags)
    # Reset modifiers
    modifiers.clear()


def process_dialect_table(
    wxr: WiktextractContext,
    base_translation_data: Dict[str, Union[str, List, bool]],
    dialect_table: List[Union[WikiNode, str]],
):
    wxr.wtp.debug("Dialect table not implemented yet.", sortid="TODO")
    # XXX: Extract dialect information (ca. 0.12% of pages), e.g.:
    # https://de.wiktionary.org/wiki/Bein
    # """
    # {{Ü-Tabelle|4|G=in der Medizin nur in zusammengesetzten Wörtern: Knochen|Ü-Liste=...
    # |Dialekttabelle=
    # *Berlinerisch: Been
    # *Kölsch:
    # *Mitteldeutsch:
    # **{{pfl}}: {{Lautschrift|bɛː}}, {{Lautschrift|bɛ̃ː}}
    # *Oberdeutsch:
    # **{{als}}: [1] Fuëß
    # ***Schwäbisch: [1, 2] Fuaß; [4] Boi, Boa
    # **{{bar}}: [1, 2] Fuaß; [4] Boan
    # *Thüringisch-Obersächsisch: Been, Knoche
    # }}"""

    return
