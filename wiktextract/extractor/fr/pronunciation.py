from collections import defaultdict
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


def process_pron_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    page_data: List[Dict],
    sound_data: Dict[str, Union[str, List[str]]],
) -> List[Dict[str, Union[str, List[str]]]]:
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in {
            "pron",
            "prononciation",
            "phon",
            "lang",  # used in template "cmn-pron"
        }:
            sound_data["ipa"] = clean_node(wxr, None, template_node)
        elif template_node.template_name in {"écouter", "audio", "pron-rég"}:
            process_ecouter_template(template_node, sound_data)
        else:
            sound_data["tags"].append(
                clean_node(wxr, None, template_node).strip("() ")
            )

    if list_item_node.contain_node(NodeKind.LIST):
        returned_data = []
        for nest_list_item in list_item_node.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            new_sound_data = sound_data.copy()
            process_pron_list_item(
                wxr, nest_list_item, page_data, new_sound_data
            )
            returned_data.append(new_sound_data)
        return returned_data
    elif len(sound_data) > 0:
        return [sound_data]


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
