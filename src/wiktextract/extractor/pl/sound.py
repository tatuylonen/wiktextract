import re
from functools import partial
from itertools import chain, count

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
    sense_index = ""
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        has_list = True
        raw_tags = []
        for node in list_item.children:
            if isinstance(node, TemplateNode):
                process_sound_template(
                    wxr, base_data, node, raw_tags, sense_index
                )
            elif isinstance(node, str):
                m = re.search(r"\(([\d\s,-.]+)\)", node)
                if m is not None:
                    sense_index = m.group(1)

    if not has_list:
        # could have preformatted node, can't use `find_child()`
        for template_node in level_node.find_child_recursively(
            NodeKind.TEMPLATE
        ):
            process_sound_template(
                wxr, base_data, template_node, [], sense_index
            )


def process_sound_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
    raw_tags: list[str],
    sense_index: str,
) -> None:
    if template_node.template_name.startswith(("IPA", "AS", "SAMPA")):
        ipa = clean_node(
            wxr, None, template_node.template_parameters.get(1, "")
        )
        if isinstance(ipa, str) and len(ipa) > 0:
            sound = Sound(ipa=ipa, raw_tags=raw_tags, sense_index=sense_index)
            if template_node.template_name.startswith("AS"):
                sound.tags.append("Slavic-alphabet")
            elif template_node.template_name == "SAMPA":
                sound.tags.append("SAMPA")
            translate_raw_tags(sound)
            base_data.sounds.append(sound)
    elif template_node.template_name.startswith("audio"):
        audio_file = template_node.template_parameters.get(1, "")
        if isinstance(audio_file, str) and len(audio_file) > 0:
            sound = Sound(raw_tags=raw_tags, sense_index=sense_index)
            set_sound_file_url_fields(wxr, audio_file, sound)
            translate_raw_tags(sound)
            base_data.sounds.append(sound)
            raw_tags.clear()
    elif template_node.template_name in SOUND_TAG_TEMPLATES:
        raw_tags.append(clean_node(wxr, None, template_node))
    elif template_node.template_name in ("pinyin", "zhuyin"):
        zh_pron = template_node.template_parameters.get(1, "")
        if isinstance(zh_pron, str) and len(zh_pron) > 0:
            sound = Sound(
                zh_pron=zh_pron, raw_tags=raw_tags, sense_index=sense_index
            )
            if template_node.template_name == "pinyin":
                sound.tags.append("Pinyin")
            elif template_node.template_name == "zhuyin":
                sound.tags.append("Bopomofo")
            translate_raw_tags(sound)
            base_data.sounds.append(sound)
    elif template_node.template_name == "dzielenie":
        extract_dzielenie_template(wxr, base_data, template_node)
    elif template_node.template_name == "homofony":
        extract_homofony_template(wxr, base_data, template_node, sense_index)


def extract_morphology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    # "preformatted" node
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name == "morfeo":
            h_str = clean_node(wxr, base_data, t_node)
            if h_str != "":
                base_data.hyphenations.append(
                    Hyphenation(
                        parts=list(
                            chain.from_iterable(
                                map(partial(str.split, sep="•"), h_str.split())
                            )
                        )
                    )
                )


def extract_dzielenie_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_str = clean_node(wxr, base_data, t_node)
    h_str = expanded_str[expanded_str.find(":") + 1 :].strip()
    base_data.hyphenations.append(
        Hyphenation(
            parts=list(
                chain.from_iterable(
                    map(partial(str.split, sep="•"), h_str.split())
                )
            )
        )
    )


def extract_homofony_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    sense_index: str,
):
    for arg in count(1):
        if arg not in t_node.template_parameters:
            break
        word = clean_node(wxr, None, t_node.template_parameters[arg])
        if word != "":
            base_data.sounds.append(
                Sound(homophone=word, sense_index=sense_index)
            )
