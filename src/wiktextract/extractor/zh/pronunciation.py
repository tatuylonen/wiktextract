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


def extract_pronunciation_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: WikiNode
) -> None:
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
    elif template_name == "ja-pron":
        new_sounds, new_cats = extract_ja_pron_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
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
    is_first_small_tag = True
    for node in list_item_node.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                link_str = clean_node(wxr, None, node.largs)
                node_str = clean_node(wxr, None, node)
                if link_str.startswith("File:"):
                    filename = link_str.removeprefix("File:")
                    sound_data = Sound(raw_tags=current_tags)
                    set_sound_file_url_fields(wxr, filename, sound_data)
                    sounds.append(sound_data)
                elif node_str != "":
                    current_tags.append(node_str.strip("()"))
            elif isinstance(node, HTMLNode):
                if node.tag == "small":
                    # remove "幫助"(help) <sup> tag
                    if is_first_small_tag:
                        raw_tag_text = clean_node(
                            wxr,
                            None,
                            [
                                n
                                for n in node.children
                                if not (
                                    isinstance(n, HTMLNode) and n.tag == "sup"
                                )
                            ],
                        ).rstrip("：")
                        current_tags.extend(split_zh_pron_raw_tag(raw_tag_text))
                    elif len(sounds) > 0:
                        sounds[-1].raw_tags.extend(
                            split_zh_pron_raw_tag(clean_node(wxr, None, node))
                        )
                    is_first_small_tag = False
                elif node.tag == "span":
                    sounds.extend(extract_zh_pron_span(wxr, node, current_tags))
                elif (
                    node.tag == "table"
                    and len(current_tags) > 0
                    and current_tags[-1] == "同音詞"
                ):
                    sounds.extend(
                        extract_zh_pron_homophones_table(
                            wxr, node, current_tags
                        )
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


def split_zh_pron_raw_tag(raw_tag_text: str) -> list[str]:
    raw_tags = []
    if "(" not in raw_tag_text and "（" not in raw_tag_text:
        for raw_tag in re.split(r",|，|：|、|和", raw_tag_text):
            raw_tag = raw_tag.strip().removeprefix("包括").strip()
            if raw_tag != "":
                raw_tags.append(raw_tag)
    else:
        last_offset = 0
        for match in re.finditer(r"\([^()]+\)|（[^（）]+）", raw_tag_text):
            raw_tags.extend(
                split_zh_pron_raw_tag(raw_tag_text[last_offset : match.start()])
            )
            raw_tags.extend(
                split_zh_pron_raw_tag(
                    raw_tag_text[match.start() + 1 : match.end() - 1]
                )
            )
            last_offset = match.end()
        raw_tags.extend(split_zh_pron_raw_tag(raw_tag_text[last_offset:]))

    return raw_tags


def extract_zh_pron_span(
    wxr: WiktextractContext, span_tag: HTMLNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    small_tags = []
    pron_nodes = []
    roman = ""
    for node in span_tag.children:
        if isinstance(node, HTMLNode) and node.tag == "small":
            small_tags = split_zh_pron_raw_tag(clean_node(wxr, None, node))
        elif (
            isinstance(node, HTMLNode)
            and node.tag == "span"
            and "-Latn" in node.attrs.get("lang", "")
        ):
            roman = clean_node(wxr, None, node).strip("() ")
        else:
            pron_nodes.append(node)
    for zh_pron in split_zh_pron(clean_node(wxr, None, pron_nodes)):
        zh_pron = zh_pron.strip("[]： ")
        if len(zh_pron) > 0:
            if "IPA" in span_tag.attrs.get("class", ""):
                sounds.append(
                    Sound(ipa=zh_pron, roman=roman, raw_tags=raw_tags)
                )
            else:
                sounds.append(
                    Sound(zh_pron=zh_pron, roman=roman, raw_tags=raw_tags)
                )
    if len(sounds) > 0:
        sounds[-1].raw_tags.extend(small_tags)
    return sounds


def split_zh_pron(zh_pron: str) -> list[str]:
    # split by comma and other symbols that outside parentheses
    parentheses = 0
    pron_list = []
    pron = ""
    for c in zh_pron:
        if (
            (c in [",", ";", "→"] or (c == "/" and not zh_pron.startswith("/")))
            and parentheses == 0
            and len(pron.strip()) > 0
        ):
            pron_list.append(pron.strip())
            pron = ""
        elif c in ["(", "（"]:
            parentheses += 1
            pron += c
        elif c in [")", "）"]:
            parentheses -= 1
            pron += c
        else:
            pron += c

    if pron.strip() != "":
        pron_list.append(pron)
    return pron_list


def extract_zh_pron_homophones_table(
    wxr: WiktextractContext, table: HTMLNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    for td_tag in table.find_html_recursively("td"):
        for span_tag in td_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            span_lang = span_tag.attrs.get("lang", "")
            span_str = clean_node(wxr, None, span_tag)
            if (
                span_str not in ["", "／"]
                and span_lang != ""
                and span_class in ["Hant", "Hans", "Hani"]
            ):
                sound = Sound(homophone=span_str, raw_tags=raw_tags)
                if span_class == "Hant":
                    sound.tags.append("Traditional-Chinese")
                elif span_class == "Hans":
                    sound.tags.append("Simplified-Chinese")
                sounds.append(sound)
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


def extract_ja_pron_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    cats = {}
    sounds = []
    for li_tag in expanded_node.find_html_recursively("li"):
        sound = Sound()
        for span_tag in li_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            if "usage-label-accent" in span_class:
                raw_tag = clean_node(wxr, None, span_tag).strip("() ")
                if raw_tag != "":
                    sound.raw_tags.append(raw_tag)
            elif "IPA" in span_class:
                sound.ipa = clean_node(wxr, None, span_tag)
            elif "Latn" in span_class:
                sound.roman = clean_node(wxr, None, span_tag)
            elif span_tag.attrs.get("lang", "") == "ja":
                sound.other = clean_node(wxr, None, span_tag)
        if sound.ipa != "" or sound.other != "":
            translate_raw_tags(sound)
            sounds.append(sound)

    clean_node(wxr, cats, expanded_node)
    return sounds, cats.get("categories", [])
