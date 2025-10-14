import itertools
import re

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import capture_text_in_parentheses, set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    sounds = []
    cats = {}
    for node in level_node.children:
        if isinstance(node, TemplateNode):
            process_sound_template(wxr, node, sounds, cats)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if base_data.lang_code == "zh":
                    extract_zh_sound_list_item(wxr, list_item, sounds, [])
                else:
                    for t_node in list_item.find_child(NodeKind.TEMPLATE):
                        process_sound_template(wxr, t_node, sounds, cats)

    if level_node.kind == NodeKind.LEVEL3:
        base_data.sounds.extend(sounds)
        base_data.categories.extend(cats.get("categories", []))
        for data in page_data:
            if data.lang_code == base_data.lang_code:
                data.sounds.extend(sounds)
                data.categories.extend(cats.get("categories", []))
    elif len(page_data) > 0:
        page_data[-1].sounds.extend(sounds)
        page_data[-1].categories.extend(cats.get("categories", []))
    else:
        base_data.sounds.extend(sounds)
        base_data.categories.extend(cats.get("categories", []))


def process_sound_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sounds: list[Sound],
    cats: dict[str, list[str]],
) -> None:
    if t_node.template_name in ["音声", "audio"]:
        extract_audio_template(wxr, t_node, sounds)
    elif t_node.template_name in ["IPA", "X-SAMPA"]:
        extract_ipa_template(wxr, t_node, sounds)
    elif t_node.template_name == "homophones":
        extract_homophones_template(wxr, t_node, sounds)
    elif t_node.template_name == "ja-pron":
        process_ja_pron_template(wxr, t_node, sounds)
    elif t_node.template_name == "ja-accent-common":
        process_ja_accent_common_template(wxr, t_node, sounds)
    elif t_node.template_name in [
        "cmn-pron",
        "yue-pron",
        "nan-pron",
        "cdo-pron",
        "hak-pron",
        "wuu-pron",
    ]:
        extract_zh_sound_template(wxr, t_node, sounds)

    clean_node(wxr, cats, t_node)


def extract_audio_template(
    wxr: WiktextractContext, t_node: TemplateNode, sounds: list[Sound]
):
    audio_file = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if audio_file not in ["", "-"]:
        sound = Sound()
        raw_tag = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
        if len(raw_tag) > 0:
            sound.raw_tags.append(raw_tag)
        set_sound_file_url_fields(wxr, audio_file, sound)
        sounds.append(sound)


def extract_ipa_template(
    wxr: WiktextractContext, t_node: TemplateNode, sounds: list[Sound]
):
    for index in itertools.count(1):
        if index not in t_node.template_parameters:
            break
        ipa = clean_node(wxr, None, t_node.template_parameters[index])
        if len(ipa) > 0:
            sound = Sound(ipa=f"/{ipa}/")
            if t_node.template_name == "X-SAMPA":
                sound.tags.append("X-SAMPA")
            sounds.append(sound)


def extract_homophones_template(
    wxr: WiktextractContext, t_node: TemplateNode, sounds: list[Sound]
):
    homophones = []
    for index in itertools.count(1):
        if index not in t_node.template_parameters:
            break
        homophone = clean_node(wxr, None, t_node.template_parameters[index])
        if len(homophone) > 0:
            homophones.append(homophone)
    if len(homophones) > 0:
        sounds.append(Sound(homophones=homophones))


JA_PRON_ACCENTS = {
    "中高型": "Nakadaka",
    "平板型": "Heiban",
    "頭高型": "Atamadaka",
    "尾高型": "Odaka",
}


def process_ja_pron_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sounds: list[Sound],
) -> None:
    # https://ja.wiktionary.org/wiki/テンプレート:ja-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        if list_item.contain_node(NodeKind.TABLE):
            continue
        else:
            sound = Sound()
            for span_tag in list_item.find_html_recursively("span"):
                span_classes = span_tag.attrs.get("class", "")
                if "qualifier-content" in span_classes:
                    raw_tag = clean_node(wxr, None, span_tag)
                    if len(raw_tag) > 0:
                        sound.raw_tags.append(raw_tag)
                elif "IPA" in span_classes:
                    sound.ipa = clean_node(wxr, None, span_tag)
                elif "Latn" in span_classes:
                    sound.roman = clean_node(wxr, None, span_tag)
                elif "Jpan" in span_classes:
                    sound.form = clean_node(wxr, None, span_tag)
            for link_node in list_item.find_child(NodeKind.LINK):
                link_text = clean_node(wxr, None, link_node)
                if link_text in JA_PRON_ACCENTS:
                    sound.tags.append(JA_PRON_ACCENTS[link_text])
            if len(sound.model_dump(exclude_defaults=True)) > 0:
                sounds.append(sound)

    for arg in ["a", "audio"]:
        audio_file = clean_node(
            wxr, None, template_node.template_parameters.get(arg, "")
        )
        if len(audio_file) > 0:
            sound = Sound()
            set_sound_file_url_fields(wxr, audio_file, sound)
            sounds.append(sound)


JA_ACCENT_COMMON_TYPES = {
    "h": "Heiban",
    "a": "Atamadaka",
    "n": "Nakadaka",
    "o": "Odaka",
}


def process_ja_accent_common_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sounds: list[Sound],
) -> None:
    # https://ja.wiktionary.org/wiki/テンプレート:ja-accent-common
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    sound = Sound()
    for link_node in expanded_node.find_child_recursively(NodeKind.LINK):
        raw_tag = clean_node(wxr, None, link_node)
        if raw_tag != "":
            sound.raw_tags.append(raw_tag)
            break
    for span_tag in expanded_node.find_html_recursively("span"):
        span_text = clean_node(wxr, None, span_tag)
        if len(span_text) > 0:
            sound.form = span_text
            break
    accent_type = clean_node(
        wxr, None, template_node.template_parameters.get(1, "")
    )
    if accent_type in JA_ACCENT_COMMON_TYPES:
        sound.tags.append(JA_ACCENT_COMMON_TYPES[accent_type])
    if sound.form != "":
        sounds.append(sound)


def extract_homophone_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    sounds = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "":
                        sounds.append(Sound(homophones=[word]))
                elif (
                    isinstance(node, TemplateNode) and node.template_name == "l"
                ):
                    from .linkage import extract_l_template

                    l_data = extract_l_template(wxr, node)
                    if l_data.word != "":
                        sounds.append(
                            Sound(
                                homophones=[l_data.word],
                                sense=l_data.sense,
                                tags=l_data.tags,
                                raw_tags=l_data.raw_tags,
                            )
                        )

    if level_node.kind == NodeKind.LEVEL3:
        base_data.sounds.extend(sounds)
        for data in page_data:
            if data.lang_code == base_data.lang_code:
                data.sounds.extend(sounds)
    elif len(page_data) > 0:
        page_data[-1].sounds.extend(sounds)
    else:
        base_data.sounds.extend(sounds)


def extract_zh_sound_template(
    wxr: WiktextractContext, t_node: TemplateNode, sounds: list[Sound]
):
    # https://ja.wiktionary.org/wiki/カテゴリ:中国語_発音テンプレート
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            raw_tag_nodes = []
            for node in list_item.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                    if len(raw_tags) == 0:
                        for raw_tag in re.split(
                            r":|,", clean_node(wxr, None, raw_tag_nodes)
                        ):
                            raw_tag = raw_tag.strip()
                            if raw_tag != "":
                                raw_tags.append(raw_tag)
                    for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                        extract_zh_sound_list_item(
                            wxr, child_list_item, sounds, raw_tags
                        )
                else:
                    raw_tag_nodes.append(node)


def extract_zh_sound_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    sounds: list[Sound],
    raw_tags: list[str],
):
    after_colon = False
    tag_nodes = []
    value_nodes = []
    for node in list_item.children:
        if isinstance(node, str) and ":" in node and not after_colon:
            tag_nodes.append(node[: node.index(":")])
            value_nodes.append(node[node.index(":") + 1 :])
            after_colon = True
        elif not after_colon:
            if isinstance(node, TemplateNode) and node.template_name in [
                "音声",
                "audio",
            ]:
                extract_audio_template(wxr, node, sounds)
            elif not (isinstance(node, HTMLNode) and node.tag == "small"):
                tag_nodes.append(node)
        else:
            value_nodes.append(node)
    for value in clean_node(wxr, None, value_nodes).split(","):
        value = value.strip()
        if value == "":
            continue
        sound = Sound(zh_pron=value, raw_tags=raw_tags)
        texts_in_p, text_out_p = capture_text_in_parentheses(
            clean_node(wxr, None, tag_nodes)
        )
        text_out_p = text_out_p.strip()
        if text_out_p != "":
            sound.raw_tags.append(text_out_p)
        for raw_tag_str in texts_in_p:
            for raw_tag in raw_tag_str.split(","):
                raw_tag = raw_tag.strip()
                if raw_tag != "":
                    sound.raw_tags.append(raw_tag)
        translate_raw_tags(sound)
        sounds.append(sound)
