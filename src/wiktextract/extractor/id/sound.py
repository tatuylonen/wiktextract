from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, word_entry, list_item)


def extract_sound_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    raw_tags = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_sound_list_item(wxr, word_entry, child_list_item)
        elif isinstance(node, TemplateNode):
            if node.template_name == "IPA":
                extract_ipa_template(wxr, word_entry, node, raw_tags)
            elif node.template_name == "audio":
                extract_audio_template(wxr, word_entry, node, raw_tags)
            elif node.template_name == "ejaan:id":
                extract_ejaan_id_template(wxr, word_entry, node, raw_tags)
            elif node.template_name == "a":
                raw_tag = clean_node(wxr, None, node).strip("()")
                if raw_tag != "":
                    raw_tags.append(raw_tag)


def extract_ipa_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    sound = Sound(
        ipa=clean_node(wxr, None, t_node.template_parameters.get(1, "")),
        raw_tags=raw_tags,
    )
    if sound.ipa != "":
        translate_raw_tags(sound)
        word_entry.sounds.append(sound)


def extract_audio_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    sound = Sound(raw_tags=raw_tags)
    if filename != "":
        set_sound_file_url_fields(wxr, filename, sound)
        raw_tag = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
        if raw_tag != "":
            sound.raw_tags.append(raw_tag)
        translate_raw_tags(sound)
        word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, t_node)


def extract_ejaan_id_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    sound = Sound(ipa=clean_node(wxr, None, t_node), raw_tags=raw_tags)
    if sound.ipa != "":
        translate_raw_tags(sound)
        word_entry.sounds.append(sound)
