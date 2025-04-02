import itertools
import re

from wikitextprocessor import (
    HTMLNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> tuple[list[Sound], list[str]]:
    if len(base_data.sounds) > 0:
        base_data.sounds.clear()

    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        new_sounds, new_cats = process_pron_template(wxr, template_node)
        base_data.sounds.extend(new_sounds)
        base_data.categories.extend(new_cats)
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        new_sounds, new_cats = process_pron_item_list_item(wxr, list_item_node)
        base_data.sounds.extend(new_sounds)
        base_data.categories.extend(new_cats)


def process_pron_item_list_item(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> tuple[list[Sound], list[str]]:
    raw_tags = []
    sounds = []
    categories = []
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        new_sounds, new_cats = process_pron_template(
            wxr, template_node, raw_tags
        )
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    return sounds, categories


def process_pron_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str] = [],
) -> tuple[list[Sound], list[str]]:
    template_name = template_node.template_name.lower()
    sounds = []
    categories = []
    if template_name == "zh-pron":
        new_sounds, new_cats = process_zh_pron_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    elif template_name in ["homophones", "homophone", "hmp"]:
        sounds.extend(process_homophones_template(wxr, template_node))
    elif template_name in ["a", "accent"]:
        # https://zh.wiktionary.org/wiki/Template:Accent
        raw_tags.append(clean_node(wxr, None, template_node).strip("()"))
    elif template_name in ["audio", "音"]:
        sounds.extend(process_audio_template(wxr, template_node, raw_tags))
    elif template_name == "ipa":
        sounds.extend(process_ipa_template(wxr, template_node, raw_tags))
    elif template_name == "enpr":
        sounds.extend(process_enpr_template(wxr, template_node, raw_tags))
    return sounds, categories


def process_zh_pron_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    # https://zh.wiktionary.org/wiki/Template:Zh-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    seen_lists = set()
    sounds = []
    categories = {}
    for list_node in expanded_node.find_child_recursively(NodeKind.LIST):
        if list_node not in seen_lists:
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                sounds.extend(
                    process_zh_pron_list_item(wxr, list_item, [], seen_lists)
                )
    clean_node(wxr, categories, expanded_node)
    for sound in sounds:
        translate_raw_tags(sound)
    return sounds, categories.get("categories", [])


def process_zh_pron_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    raw_tags: list[str],
    seen_lists: set[WikiNode],
) -> list[Sound]:
    current_tags = raw_tags[:]
    sounds = []
    for node in list_item_node.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                if len(node.largs) > 0 and node.largs[0][0].startswith("File:"):
                    filename = node.largs[0][0].removeprefix("File:")
                    sound_data = Sound()
                    set_sound_file_url_fields(wxr, filename, sound_data)
                    sounds.append(sound_data)
                else:
                    current_tags.append(clean_node(wxr, None, node).strip("()"))
            elif isinstance(node, HTMLNode):
                if node.tag == "small":
                    # remove "幫助"(help) <sup> tag
                    raw_tag_text = clean_node(
                        wxr,
                        None,
                        list(node.invert_find_child(NodeKind.HTML)),
                    )
                    if raw_tag_text.startswith("(") and raw_tag_text.endswith(
                        ")"
                    ):
                        raw_tag_text = raw_tag_text.strip("()")
                    raw_tags = re.split(r"，|：", raw_tag_text)
                    current_tags.extend(
                        [t.strip() for t in raw_tags if len(t.strip()) > 0]
                    )
                elif node.tag == "span":
                    zh_pron = clean_node(wxr, None, node)
                    if len(zh_pron) > 0:
                        if "IPA" in node.attrs.get("class", ""):
                            sound = Sound(ipa=zh_pron, raw_tags=current_tags)
                        else:
                            sound = Sound(
                                zh_pron=zh_pron, raw_tags=current_tags
                            )
                        sounds.append(sound)
                elif (
                    node.tag == "table"
                    and len(current_tags) > 0
                    and current_tags[-1] == "同音詞"
                ):
                    sounds.extend(
                        process_homophones_table(wxr, node, current_tags)
                    )

            elif node.kind == NodeKind.LIST:
                seen_lists.add(node)
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    sounds.extend(
                        process_zh_pron_list_item(
                            wxr,
                            next_list_item,
                            current_tags,
                            seen_lists,
                        )
                    )
    return sounds


def process_homophones_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:homophones
    sounds = []
    for word_index in itertools.count(2):
        if word_index not in template_node.template_parameters:
            break
        homophone = clean_node(
            wxr, None, template_node.template_parameters.get(word_index, "")
        )
        if len(homophone) > 0:
            sounds.append(Sound(homophone=homophone))
    return sounds


def process_homophones_table(
    wxr: WiktextractContext,
    table_node: HTMLNode,
    raw_tags: list[str],
) -> list[Sound]:
    sounds = []
    for span_node in table_node.find_html_recursively("span", attr_name="lang"):
        sound_data = Sound(
            homophone=clean_node(wxr, None, span_node), raw_tags=raw_tags
        )
        sounds.append(sound_data)
    return sounds


def process_audio_template(
    wxr: WiktextractContext, template_node: TemplateNode, raw_tags: list[str]
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:Audio
    sound_file = clean_node(
        wxr, None, template_node.template_parameters.get(2, "")
    )
    sound_data = Sound()
    set_sound_file_url_fields(wxr, sound_file, sound_data)
    raw_tag = clean_node(
        wxr, None, template_node.template_parameters.get(3, "")
    )
    if len(raw_tag) > 0:
        sound_data.raw_tags.append(raw_tag)
    sound_data.raw_tags.extend(raw_tags)
    return [sound_data]


def process_ipa_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:IPA
    sounds = []
    for index in itertools.count(2):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            ipa=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        sounds.append(sound)
    return sounds


def process_enpr_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:enPR
    sounds = []
    for index in range(1, 4):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            enpr=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        sounds.append(sound)
    return sounds
