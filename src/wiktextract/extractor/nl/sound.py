from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        sound = Sound()
        for t_node in list_item.find_child(NodeKind.TEMPLATE):
            if t_node.template_name == "audio":
                extract_audio_template(wxr, word_entry, sound, t_node)
            elif t_node.template_name.startswith("IPA"):
                extract_ipa_template(wxr, word_entry, sound, t_node)
            elif t_node.template_name == "pron-reg":
                extract_pron_reg_template(wxr, sound, t_node)

        if sound.ipa != "" or sound.audio != "":
            word_entry.sounds.append(sound)


def extract_audio_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sound: Sound,
    t_node: TemplateNode,
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:audio
    audio_file = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    set_sound_file_url_fields(wxr, audio_file, sound)
    clean_node(wxr, word_entry, t_node)


def extract_ipa_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sound: Sound,
    t_node: TemplateNode,
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:IPA-nl-standaard
    # https://nl.wiktionary.org/wiki/Sjabloon:IPA
    sound.ipa = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    clean_node(wxr, word_entry, t_node)


def extract_pron_reg_template(
    wxr: WiktextractContext, sound: Sound, t_node: TemplateNode
) -> None:
    # location tag
    # https://nl.wiktionary.org/wiki/Sjabloon:pron-reg
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child_recursively(NodeKind.LINK):
        sound.raw_tags.append(clean_node(wxr, None, link_node))
