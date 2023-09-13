from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_pronunciation(
    wxr: WiktextractContext, page_data: List[Dict], level_node: WikiNode
) -> None:
    sound_data = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
            sound_data.extend(
                process_pron_list_item(
                    wxr, list_item_node, page_data, defaultdict(list)
                )
            )

    if len(sound_data) == 0:
        return

    if level_node.kind == NodeKind.LEVEL3:
        # Add extracted sound data to all sense dictionaries that have the same
        # language code when the prononciation subtitle is a level 3 title node.
        # Otherwise only add to the last one.
        lang_code = page_data[-1].get("lang_code")
        for sense_data in page_data:
            if sense_data.get("lang_code") == lang_code:
                sense_data["sounds"].extend(sound_data)
    else:
        page_data[-1]["sounds"].extend(sound_data)


# "lang" is used in template "cmn-pron"
PRON_TEMPLATES = frozenset(["pron", "prononciation", "//", "phon", "lang"])


def process_pron_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    page_data: List[Dict],
    sound_data: Dict[str, Union[str, List[str]]],
) -> List[Dict[str, Union[str, List[str]]]]:
    pron_key = "zh-pron" if page_data[-1].get("lang_code") == "zh" else "ipa"

    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in PRON_TEMPLATES:
            pron_text = process_pron_template(wxr, template_node)
            if len(pron_text) > 0:
                sound_data[pron_key] = pron_text
        elif template_node.template_name in {"écouter", "audio", "pron-rég"}:
            process_ecouter_template(template_node, sound_data)
        else:
            sound_data["tags"].append(
                clean_node(wxr, None, template_node).strip("() ")
            )

    if list_item_node.contain_node(NodeKind.LIST):
        returned_data = []
        for bold_node in list_item_node.find_child(NodeKind.BOLD):
            sound_data["tags"].append(clean_node(wxr, None, bold_node))

        for nest_list_item in list_item_node.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            new_sound_data = deepcopy(sound_data)
            process_pron_list_item(
                wxr, nest_list_item, page_data, new_sound_data
            )
            if pron_key in new_sound_data:
                returned_data.append(new_sound_data)

        return returned_data
    elif len(sound_data) > 0:
        if pron_key not in sound_data:
            for child in list_item_node.filter_empty_str_child():
                if isinstance(child, str):
                    if child.strip().startswith(": "):
                        # IPA text after "language : "
                        sound_data[pron_key] = (
                            child.strip().removeprefix(": ").strip()
                        )
                    elif len(child.strip()) > 0 and child.strip() != ":":
                        # language text before ":"
                        sound_data["tags"].append(child.strip())

        if pron_key in sound_data:
            return [sound_data]
        else:
            return []


def process_pron_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> str:
    if (
        template_node.template_name in {"pron", "prononciation", "//"}
        and len(template_node.template_parameters.get(1, "").strip()) == 0
    ):
        # some pages don't pass IPA parameter to the "pron" template
        # and expand to an edit link for adding the missing data.
        return ""
    return clean_node(wxr, None, template_node)


def process_ecouter_template(
    template_node: TemplateNode, sound_data: Dict[str, Union[str, List[str]]]
) -> None:
    # sound file template: https://fr.wiktionary.org/wiki/Modèle:écouter
    location = template_node.template_parameters.get(1, "")
    ipa = template_node.template_parameters.get(
        2, template_node.template_parameters.get("pron", "")
    )
    audio_file = template_node.template_parameters.get("audio", "")
    if len(location) > 0:
        sound_data["tags"].append(location)
    if len(ipa) > 0:
        sound_data["ipa"] = ipa
    if len(audio_file) > 0:
        sound_data.update(create_audio_url_dict(audio_file))


def is_ipa_text(text: str) -> bool:
    # check if the text is IPA, used for inflection table cell text
    if text.startswith("\\") and text.endswith("\\"):
        return True
    if text.startswith("ou ") and text.endswith("\\"):
        # some inflection table template like "en-nom-rég" might have a second
        # ipa text in a new line
        return True
    return False


def split_ipa(text: str) -> list[str] | str:
    # break IPA text if it contains "ou"(or)
    if " ou " in text:
        # two ipa texts in the same line: "en-conj-rég" template
        return text.split(" ou ")
    if text.startswith("ou "):
        return text.removeprefix("ou ")
    return text


def insert_ipa(target_dict: dict[str, str | list[str]], ipa_text: str) -> None:
    # insert IPA text to a dictionary, and merge values of the key "ipa" and
    # "ipas", `target_dict` is created by `defaultdict(list)`.
    ipa_data = split_ipa(ipa_text)
    if isinstance(ipa_data, str):
        if "ipas" in target_dict:
            target_dict["ipas"].append(ipa_data)
        elif "ipa" in target_dict:
            target_dict["ipas"].append(target_dict["ipa"])
            target_dict["ipas"].append(ipa_data)
            del target_dict["ipa"]
        else:
            target_dict["ipa"] = ipa_data
    elif isinstance(ipa_data, list):
        if "ipa" in target_dict:
            target_dict["ipas"].append(target_dict["ipa"])
            del target_dict["ipa"]

        target_dict["ipas"].extend(ipa_data)
