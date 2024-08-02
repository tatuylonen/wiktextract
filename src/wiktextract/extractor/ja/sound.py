import itertools

from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_sound_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    for template_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        process_sound_template(wxr, base_data, template_node)


def process_sound_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    if template_node.template_name == "音声":
        audio_file = template_node.template_parameters.get(2, "")
        if len(audio_file) > 0:
            sound = Sound()
            raw_tag = clean_node(
                wxr, None, template_node.template_parameters.get(3, "")
            )
            if len(raw_tag) > 0:
                sound.raw_tags.append(raw_tag)
            set_sound_file_url_fields(wxr, audio_file, sound)
            base_data.sounds.append(sound)
    elif template_node.template_name in ["IPA", "X-SAMPA"]:
        for index in itertools.count(1):
            if index not in template_node.template_parameters:
                break
            ipa = template_node.template_parameters[index]
            if len(ipa) > 0:
                sound = Sound(ipa=ipa)
                if template_node.template_name == "X-SAMPA":
                    sound.tags.append("X-SAMPA")
                base_data.sounds.append(sound)
    elif template_node.template_name == "homophones":
        homophones = []
        for index in itertools.count(1):
            if index not in template_node.template_parameters:
                break
            homophone = template_node.template_parameters[index]
            if len(homophone) > 0:
                homophones.append(homophone)
        if len(homophones) > 0:
            base_data.sounds.append(Sound(homophones=homophones))
    elif template_node.template_name == "ja-pron":
        process_ja_pron_template(wxr, base_data, template_node)

    clean_node(wxr, base_data, template_node)


def process_ja_pron_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
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
            if len(sound.model_dump(exclude_defaults=True)) > 0:
                base_data.sounds.append(sound)

    for arg in ["a", "audio"]:
        audio_file = template_node.template_parameters.get(arg, "")
        if len(audio_file) > 0:
            sound = Sound()
            set_sound_file_url_fields(wxr, audio_file, sound)
            base_data.sounds.append(sound)
