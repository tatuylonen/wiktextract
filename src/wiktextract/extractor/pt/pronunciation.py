from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_pronunciation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
) -> None:
    raw_tags = []
    sounds = []
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text not in ["", "Pronúncia"]:
        raw_tags.append(title_text)

    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sounds.extend(
                extract_pronunciation_list_item(
                    wxr, list_item, page_data[-1].lang_code, raw_tags
                )
            )

    for child_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        extract_pronunciation_section(wxr, page_data, child_level_node)

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            for sound in sounds:
                data.sounds.append(sound)


def extract_pronunciation_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    lang_code: str,
    parent_raw_tags: list[str],
) -> list[Sound]:
    raw_tags = parent_raw_tags[:]
    sounds = []
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node:
            raw_tag = clean_node(wxr, None, list_item.children[:index])
            if raw_tag != "":
                raw_tags.append(raw_tag)
            sound_value = clean_node(
                wxr,
                None,
                [node[node.index(":") + 1 :]]
                + [
                    n
                    for n in list_item.children[index + 1 :]
                    if not (isinstance(n, WikiNode) and n.kind == NodeKind.LIST)
                ],
            )
            if sound_value != "":
                sound = Sound(raw_tags=raw_tags)
                if lang_code == "zh":
                    sound.zh_pron = sound_value
                else:
                    sound.ipa = sound_value
                translate_raw_tags(sound)
                sounds.append(sound)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                sounds.extend(
                    extract_pronunciation_list_item(
                        wxr, child_list_item, lang_code, raw_tags
                    )
                )

    return sounds
