import itertools

from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_sound_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    if not level_node.contain_node(NodeKind.LIST):
        level_node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(level_node.children), expand_all=True
        )
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_sound_list_item(wxr, base_data, list_item)


def process_sound_list_item(
    wxr: WiktextractContext,
    base_data: WordEntry,
    list_item: WikiNode,
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            process_sound_template(wxr, base_data, node)


def process_sound_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    if template_node.template_name == "音声":
        audio_file = template_node.template_parameters.get(2, "")
        if len(audio_file) > 0:
            sound = Sound()
            raw_tag = clean_node(
                wxr, None, template_node.template_parameters.get(3, "")
            )
            if len(raw_tag) > 0:
                sound.raw_tags.append(raw_tag)
            set_sound_file_url_fields(wxr, audio_file, sound)
            base_data.sounds.append(sound)
    elif template_node.template_name in ["IPA", "X-SAMPA"]:
        for index in itertools.count(1):
            if index not in template_node.template_parameters:
                break
            ipa = template_node.template_parameters[index]
            if len(ipa) > 0:
                sound = Sound(ipa=ipa)
                if template_node.template_name == "X-SAMPA":
                    sound.tags.append("X-SAMPA")
                base_data.sounds.append(sound)
    elif template_node.template_name == "homophones":
        homophones = []
        for index in itertools.count(1):
            if index not in template_node.template_parameters:
                break
            homophone = template_node.template_parameters[index]
            if len(homophone) > 0:
                homophones.append(homophone)
        if len(homophones) > 0:
            base_data.sounds.append(Sound(homophones=homophones))

    clean_node(wxr, base_data, template_node)
