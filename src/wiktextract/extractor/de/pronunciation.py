from collections import defaultdict
from typing import Dict, List, Union

from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: List[Dict],
    level_node: LevelNode,
):
    for list_node in level_node.find_child(NodeKind.LIST):
        sound_data = [defaultdict(list)]

        for not_list_item_node in list_node.invert_find_child(
            NodeKind.LIST_ITEM
        ):
            wxr.wtp.debug(
                f"Found unexpected non-list-item node in pronunciation section: {not_list_item_node}",
                sortid="extractor/de/pronunciation/extract_pronunciation/28",
            )

        for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
            children = list(list_item_node.filter_empty_str_child())
            if len(children) == 0:
                continue

            head_template, rest = children[0], children[1:]
            if (
                not isinstance(head_template, WikiNode)
                or head_template.kind != NodeKind.TEMPLATE
                or not rest
            ):
                wxr.wtp.debug(
                    f"Found unexpected non-template node in pronunciation section: {head_template}",
                    sortid="extractor/de/pronunciation/extract_pronunciation/37",
                )
                continue
            if head_template.template_name == "IPA":
                process_ipa(wxr, sound_data, rest)
            elif head_template.template_name == "Hörbeispiele":
                sound_data.append(defaultdict(list))
                process_hoerbeispiele(wxr, sound_data, rest)
            elif head_template.template_name == "Reime":
                process_rhymes(wxr, sound_data, rest)
            else:
                wxr.wtp.debug(
                    f"Found unexpected template in pronunciation section: {head_template} with content {rest}",
                    sortid="extractor/de/pronunciation/extract_pronunciation/45)",
                )

        # Remove empty entries
        sound_data = [entry for entry in sound_data if entry != {}]
        if len(sound_data) > 0:
            page_data[-1]["sounds"].extend(sound_data)

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in pronunciation section: {non_list_node}",
            sortid="extractor/de/pronunciation/extract_pronunciation/64",
        )


def process_ipa(
    wxr: WiktextractContext,
    sound_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
):
    for node in nodes:
        if is_template_node_with_name(node, "Lautschrift"):
            process_lautschrift_template(wxr, sound_data, node)
        elif is_tag_node(node):
            append_tag(wxr, sound_data, node)
        elif is_new_sound_data_entry_sep(node):
            sound_data.append(defaultdict(list))
        else:
            wxr.wtp.debug(
                f"Found unexpected non-Lautschrift node in IPA section: {node}",
                sortid="extractor/de/pronunciation/process_ipa/57",
            )


def process_lautschrift_template(
    wxr: WiktextractContext, sound_data: List[Dict], node
):
    template_parameters = node.template_parameters

    ipa = template_parameters.get(1)

    lang_code = template_parameters.get("spr")
    if lang_code:
        language = code_to_name(lang_code, "de")
        add_sound_data_without_appending_to_existing_properties(
            sound_data,
            {
                "ipa": [ipa],
                "lang_code": lang_code,
                "language": language,
            },
        )
    else:
        sound_data[-1]["ipa"].append(ipa)


def process_hoerbeispiele(
    wxr: WiktextractContext, sound_data: List[Dict], nodes: List[WikiNode]
):
    for node in nodes:
        if is_template_node_with_name(node, "Audio"):
            process_audio_template(wxr, sound_data, node)
        elif is_tag_node(node):
            append_tag(wxr, sound_data, node)
        elif is_new_sound_data_entry_sep(node):
            sound_data.append(defaultdict(list))
        else:
            wxr.wtp.debug(
                f"Found unexpected node in Hoerbeispiele section: {node}",
                sortid="extractor/de/pronunciation/process_hoerbeispiele/193",
            )


def process_audio_template(
    wxr: WiktextractContext, sound_data: List[Dict], node
):
    audio_file = node.template_parameters.get(1)
    if audio_file:
        add_sound_data_without_appending_to_existing_properties(
            sound_data, create_audio_url_dict(audio_file)
        )


def process_rhymes(
    wxr: WiktextractContext, sound_data: List[Dict], nodes: List[WikiNode]
):
    # XXX: Extract rhymes from the referenced rhymes page
    pass


def is_template_node_with_name(node: Union[WikiNode, str], template_name: str):
    return (
        isinstance(node, WikiNode)
        and node.kind == NodeKind.TEMPLATE
        and node.template_name == template_name
    )


def add_sound_data_without_appending_to_existing_properties(
    sound_data: List[Dict],
    new_sound_data: Dict,
):
    """Creates a new IPA data entry if properties exist in previous entry."""
    if any([key in sound_data[-1] for key in new_sound_data.keys()]):
        sound_data.append(defaultdict(list))

    for key, value in new_sound_data.items():
        if isinstance(value, str):
            sound_data[-1][key] = value
        else:
            sound_data[-1][key].extend(value)


def is_tag_node(node: Union[WikiNode, str]):
    return isinstance(node, WikiNode) and node.kind in [
        NodeKind.TEMPLATE,
        NodeKind.ITALIC,
    ]


def append_tag(wxr: WiktextractContext, sound_data: Dict, node: WikiNode):
    tag = clean_node(wxr, {}, node).strip()
    if tag:
        sound_data[-1]["tags"].append(tag)


def is_new_sound_data_entry_sep(node: Union[WikiNode, str]):
    return isinstance(node, str) and node.strip() in [",", ";"]
