from typing import Union

from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode

from wiktextract.extractor.de.models import Sound, WordEntry
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_pronunciation(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
):
    for list_node in level_node.find_child(NodeKind.LIST):
        sound_data: list[Sound] = [Sound()]

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
                sound_data.append(Sound())
                process_hoerbeispiele(wxr, sound_data, rest)
            elif head_template.template_name == "Reime":
                process_rhymes(wxr, sound_data, rest)
            else:
                wxr.wtp.debug(
                    f"Found unexpected template in pronunciation section: {head_template} with content {rest}",
                    sortid="extractor/de/pronunciation/extract_pronunciation/45)",
                )

        # Remove empty entries
        sound_data = [
            entry
            for entry in sound_data
            if entry.model_dump(exclude_defaults=True) != {}
        ]
        if len(sound_data) > 0:
            word_entry.sounds.extend(sound_data)

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in pronunciation section: {non_list_node}",
            sortid="extractor/de/pronunciation/extract_pronunciation/64",
        )


def process_ipa(
    wxr: WiktextractContext,
    sound_data: list[Sound],
    nodes: list[Union[WikiNode, str]],
):
    for node in nodes:
        if is_template_node_with_name(node, "Lautschrift"):
            process_lautschrift_template(wxr, sound_data, node)
        elif is_tag_node(node):
            append_tag(wxr, sound_data[-1], node)
        elif is_new_sound_data_entry_sep(node):
            sound_data.append(Sound())
        else:
            wxr.wtp.debug(
                f"Found unexpected non-Lautschrift node in IPA section: {node}",
                sortid="extractor/de/pronunciation/process_ipa/57",
            )


def process_lautschrift_template(
    wxr: WiktextractContext, sound_data: list[Sound], node: WikiNode
):
    template_parameters = node.template_parameters

    ipa = template_parameters.get(1)

    lang_code = template_parameters.get("spr")
    if lang_code:
        lang_name = code_to_name(lang_code, "de")
        add_sound_data_without_appending_to_existing_properties(
            wxr,
            sound_data,
            {
                "ipa": [ipa],
                "lang_code": lang_code,
                "lang_name": lang_name,
            },
        )
    else:
        sound_data[-1].ipa.append(ipa)


def process_hoerbeispiele(
    wxr: WiktextractContext, sound_data: list[Sound], nodes: list[WikiNode]
):
    for node in nodes:
        if is_template_node_with_name(node, "Audio"):
            process_audio_template(wxr, sound_data, node)
        elif is_tag_node(node):
            append_tag(wxr, sound_data[-1], node)
        elif is_new_sound_data_entry_sep(node):
            sound_data.append(Sound())
        else:
            wxr.wtp.debug(
                f"Found unexpected node in Hoerbeispiele section: {node}",
                sortid="extractor/de/pronunciation/process_hoerbeispiele/193",
            )


def process_audio_template(
    wxr: WiktextractContext, sound_data: list[Sound], node: WikiNode
):
    audio_file = node.template_parameters.get(1)
    if audio_file:
        add_sound_data_without_appending_to_existing_properties(
            wxr, sound_data, create_audio_url_dict(audio_file)
        )


def process_rhymes(
    wxr: WiktextractContext, sound_data: list[Sound], nodes: list[WikiNode]
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
    wxr: WiktextractContext,
    sound_data: list[Sound],
    new_sound_data: list[dict],
):
    """Creates a new IPA data entry if properties exist in previous entry."""
    if any(
        [
            key in sound_data[-1].model_dump(exclude_defaults=True)
            for key in new_sound_data.keys()
        ]
    ):
        sound_data.append(Sound())

    for key, value in new_sound_data.items():
        if key in sound_data[-1].model_fields:
            if isinstance(value, str):
                getattr(sound_data[-1], key).append(value)
            else:
                getattr(sound_data[-1], key).extend(value)
        else:
            wxr.wtp.debug(
                f"Unexpected key {key} for Sound",
                sortid="extractor/de/pronunciation/add_sound_data_without_appending_to_existing_properties/167",
            )


def is_tag_node(node: Union[WikiNode, str]):
    return isinstance(node, WikiNode) and node.kind in [
        NodeKind.TEMPLATE,
        NodeKind.ITALIC,
    ]


def append_tag(wxr: WiktextractContext, sound_data: Sound, node: WikiNode):
    tag = clean_node(wxr, {}, node).strip()
    if tag:
        sound_data.tags.append(tag)


def is_new_sound_data_entry_sep(node: Union[WikiNode, str]):
    return isinstance(node, str) and node.strip() in [",", ";"]
