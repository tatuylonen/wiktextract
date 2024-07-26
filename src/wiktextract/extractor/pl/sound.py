from wikitextprocessor.parser import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags

SOUND_TAG_TEMPLATES = frozenset(["RP", "amer", "lp", "lm"])


def extract_sound_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        raw_tags = []
        for template_node in list_item.find_child(NodeKind.TEMPLATE):
            if template_node.template_name.startswith(("IPA", "AS", "SAMPA")):
                ipa = template_node.template_parameters.get(1, "")
                if isinstance(ipa, str) and len(ipa) > 0:
                    sound = Sound(ipa=ipa, raw_tags=raw_tags)
                    if template_node.template_name.startswith("AS"):
                        sound.tags.append("Slavic-alphabet")
                    elif template_node.template_name == "SAMPA":
                        sound.tags.append("SAMPA")
                    translate_raw_tags(sound)
                    base_data.sounds.append(sound)
            elif template_node.template_name.startswith("audio"):
                audio_file = template_node.template_parameters.get(1, "")
                if isinstance(audio_file, str) and len(audio_file) > 0:
                    sound = Sound(raw_tags=raw_tags)
                    set_sound_file_url_fields(wxr, audio_file, sound)
                    translate_raw_tags(sound)
                    base_data.sounds.append(sound)
                    raw_tags.clear()
            elif template_node.template_name in SOUND_TAG_TEMPLATES:
                raw_tags.append(clean_node(wxr, None, template_node))
