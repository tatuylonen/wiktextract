from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_hyphenation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    hyphenation = ""
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            hyphenation = clean_node(wxr, None, list_item.children)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.hyphenation = hyphenation


def extract_pronunciation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    sounds = []
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        match t_node.template_name.lower():
            case "ipa":
                ipa = clean_node(
                    wxr, None, t_node.template_parameters.get(1, "")
                )
                if ipa != "":
                    sounds.append(Sound(ipa=ipa))
            case "audio":
                sound_file = clean_node(
                    wxr, None, t_node.template_parameters.get(1, "")
                )
                if sound_file != "":
                    if len(sounds) > 0:
                        set_sound_file_url_fields(wxr, sound_file, sounds[-1])
                    else:
                        sound = Sound()
                        set_sound_file_url_fields(wxr, sound_file, sound)
                        sounds.append(sound)

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.sounds.extend(sounds)
