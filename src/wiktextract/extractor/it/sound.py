from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry


def extract_hyphenation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    # https://it.wiktionary.org/wiki/Aiuto:Sillabazione
    hyphenations = []
    for list_node in level_node.find_child(NodeKind.LIST):
        match list_node.sarg:
            case ";":
                for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                    h_str = clean_node(wxr, None, list_item.children)
                    if h_str != "":
                        hyphenations.append(Hyphenation(hyphenation=h_str))
                        break
            case "*":
                for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                    h_data = Hyphenation()
                    for node in list_item.find_child(
                        NodeKind.ITALIC | NodeKind.BOLD
                    ):
                        match node.kind:
                            case NodeKind.ITALIC:
                                h_data.sense = clean_node(
                                    wxr, None, node
                                ).strip("()")
                            case NodeKind.BOLD:
                                h_data.hyphenation = clean_node(wxr, None, node)
                    if h_data.hyphenation != "":
                        hyphenations.append(h_data)

    # no list
    for node in level_node.find_child(NodeKind.BOLD):
        h_str = clean_node(wxr, None, node)
        if h_str != "":
            hyphenations.append(Hyphenation(hyphenation=h_str))

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.hyphenations.extend(hyphenations)


def extract_pronunciation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    # https://it.wiktionary.org/wiki/Aiuto:Pronuncia
    sounds = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, list_item, sounds)

    # no list
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        extract_sound_template(wxr, t_node, sounds, "")

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.sounds.extend(sounds)


def extract_sound_list_item(
    wxr: WiktextractContext, list_item: WikiNode, sounds: list[Sound]
) -> None:
    sense = ""
    for node in list_item.find_child(NodeKind.ITALIC | NodeKind.TEMPLATE):
        match node.kind:
            case NodeKind.ITALIC:
                sense = clean_node(wxr, None, node).strip("()")
            case NodeKind.TEMPLATE:
                extract_sound_template(wxr, node, sounds, sense)


def extract_sound_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sounds: list[Sound],
    sense: str,
) -> None:
    match t_node.template_name:
        case "IPA" | "SAMPA":
            # https://it.wiktionary.org/wiki/Template:IPA
            # https://it.wiktionary.org/wiki/Template:SAMPA
            for arg_name in range(1, 5):
                if arg_name not in t_node.template_parameters:
                    break
                ipa = clean_node(
                    wxr, None, t_node.template_parameters.get(arg_name, "")
                )
                if ipa != "":
                    sound = Sound(ipa=ipa, sense=sense)
                    if t_node.template_name.lower() == "sampa":
                        sound.tags.append("SAMPA")
                    sounds.append(sound)
        case "Audio" | "audio":
            # https://it.wiktionary.org/wiki/Template:Audio
            sound_file = clean_node(
                wxr, None, t_node.template_parameters.get(1, "")
            )
            raw_tag = clean_node(
                wxr, None, t_node.template_parameters.get(2, "")
            )
            if sound_file != "":
                if len(sounds) > 0:
                    set_sound_file_url_fields(wxr, sound_file, sounds[-1])
                    if raw_tag != "":
                        sounds[-1].raw_tags.append(raw_tag)
                else:
                    sound = Sound(sense=sense)
                    set_sound_file_url_fields(wxr, sound_file, sound)
                    if raw_tag != "":
                        sound.raw_tags.append(raw_tag)
                    sounds.append(sound)
