from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry
from .tags import translate_raw_tags

SOUND_TAG_TEMPLATES = frozenset(["RP", "amer", "lp", "lm"])


def extract_sound_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    has_list = False
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        has_list = True
        raw_tags = []
        for template_node in list_item.find_child(NodeKind.TEMPLATE):
            process_sound_template(wxr, base_data, template_node, raw_tags)
    if not has_list:
        # could have preformatted node, can't use `find_child()`
        for template_node in level_node.find_child_recursively(
            NodeKind.TEMPLATE
        ):
            process_sound_template(wxr, base_data, template_node, [])


def process_sound_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> None:
    if template_node.template_name.startswith(("IPA", "AS", "SAMPA")):
        ipa = clean_node(
            wxr, None, template_node.template_parameters.get(1, "")
        )
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
    elif template_node.template_name in ("pinyin", "zhuyin"):
        zh_pron = template_node.template_parameters.get(1, "")
        if isinstance(zh_pron, str) and len(zh_pron) > 0:
            sound = Sound(zh_pron=zh_pron, raw_tags=raw_tags)
            if template_node.template_name == "pinyin":
                sound.tags.append("Pinyin")
            elif template_node.template_name == "zhuyin":
                sound.tags.append("Bopomofo")
            translate_raw_tags(sound)
            base_data.sounds.append(sound)


def extract_morphology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    # "preformatted" node
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name == "morfeo":
            h_str = clean_node(wxr, base_data, t_node)
            if h_str != "":
                base_data.hyphenations.append(
                    Hyphenation(parts=h_str.split("•"))
                )
