from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_pronunciation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for sound in extract_pron_list_item(wxr, list_item):
                word_entry.sounds.append(sound)
                word_entry.categories.extend(sound.categories)


def extract_pron_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Sound]:
    raw_tags = []
    sounds = []
    for node in list_item.find_child(
        NodeKind.TEMPLATE | NodeKind.ITALIC | NodeKind.LIST
    ):
        match node.kind:
            case NodeKind.ITALIC:
                node_text = clean_node(wxr, None, node)
                if node_text.endswith(":"):
                    raw_tags.append(node_text.removesuffix(":"))
            case NodeKind.LIST:
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    sounds.extend(extract_pron_list_item(wxr, next_list_item))
            case NodeKind.TEMPLATE:
                match node.template_name:
                    case "Lautschrift":
                        ipa = clean_node(
                            wxr,
                            None,
                            node.template_parameters.get(1, ""),
                        )
                        if ipa != "":
                            sounds.append(Sound(ipa=ipa))
                            clean_node(wxr, sounds[-1], node)
                    case "Audio":
                        new_sound = extract_audio_template(wxr, node)
                        if new_sound is not None:
                            sounds.append(new_sound)
                    case "Reim":
                        rhyme = clean_node(
                            wxr,
                            None,
                            node.template_parameters.get(1, ""),
                        )
                        if rhyme != "":
                            sounds.append(Sound(rhymes=rhyme))
                            clean_node(wxr, sounds[-1], node)

    for sound in sounds:
        sound.raw_tags.extend(raw_tags)
        translate_raw_tags(sound)
    return sounds


def extract_audio_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> Sound | None:
    # https://de.wiktionary.org/wiki/Vorlage:Audio
    filename = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if filename.strip() == "":
        return None
    sound = Sound()
    set_sound_file_url_fields(wxr, filename, sound)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        link_str = clean_node(wxr, None, link_node)
        if "(" in link_str:
            sound.raw_tags.append(link_str[link_str.index("(") + 1:].strip(")"))
    clean_node(wxr, sound, expanded_node)
    return sound
