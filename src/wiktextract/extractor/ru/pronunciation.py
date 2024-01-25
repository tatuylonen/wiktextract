import re
from typing import Union

from wikitextprocessor import NodeKind
from wikitextprocessor.parser import LevelNode, WikiNode, WikiNodeChildrenList
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import create_audio_url_dict
from .models import Linkage, Sound, WordEntry


def process_transcription_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription

    sound = Sound()

    template_params = template_node.template_parameters

    extract_ipa(wxr, sound, template_params, 1)

    extract_audio_file(wxr, sound, template_params, 2)

    extract_tags(wxr, sound, template_params)

    extract_homophones(wxr, sound, template_params)

    if sound.model_dump(exclude_defaults=True) != {}:
        word_entry.sounds.append(sound)


def process_transcriptions_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcriptions

    sound_sg = Sound()
    sound_pl = Sound()

    template_params = template_node.template_parameters

    extract_ipa(wxr, sound_sg, template_params, 1)
    extract_ipa(wxr, sound_pl, template_params, 2)

    extract_audio_file(wxr, sound_sg, template_params, 3)
    extract_audio_file(wxr, sound_pl, template_params, 4)

    extract_tags(wxr, [sound_sg, sound_pl], template_params)

    extract_homophones(wxr, sound_sg, template_params)

    if sound_sg.model_dump(exclude_defaults=True) != {} and (
        sound_sg.ipa or sound_sg.audio
    ):
        sound_sg.tags.append("singular")
        word_entry.sounds.append(sound_sg)

    if sound_pl.model_dump(exclude_defaults=True) != {} and (
        sound_pl.ipa or sound_pl.audio
    ):
        sound_pl.tags.append("plural")
        word_entry.sounds.append(sound_pl)


def process_transcription_ru_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-ru
    sound = Sound()

    template_params = template_node.template_parameters

    ipa = clean_node(wxr, {}, template_params.get("вручную", ""))
    if not ipa:
        cleaned_node = clean_node(wxr, {}, template_node)
        ipa_match = re.search(r"\[(.*?)\]", cleaned_node)
        if ipa_match:
            ipa = ipa_match.group(1)

    if ipa:
        sound.ipa = ipa

    extract_audio_file(wxr, sound, template_params, 2)

    extract_homophones(wxr, sound, template_params)

    extract_tags(wxr, sound, template_params)

    if sound.model_dump(exclude_defaults=True) != {}:
        word_entry.sounds.append(sound)


def process_transcriptions_ru_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: WikiNode,
):
    sound_sg = Sound()
    sound_pl = Sound()

    template_params = template_node.template_parameters

    cleaned_node = clean_node(wxr, {}, template_node)
    ipa_matches = re.findall(r"\[(.*?)\]", cleaned_node)
    if len(ipa_matches) > 0:
        sound_sg.ipa = ipa_matches[0]
    if len(ipa_matches) > 1:
        sound_pl.ipa = ipa_matches[1]

    extract_audio_file(wxr, sound_sg, template_params, 3)
    extract_audio_file(wxr, sound_pl, template_params, 4)

    extract_tags(wxr, [sound_sg, sound_pl], template_params)

    extract_homophones(wxr, sound_sg, template_params)

    if sound_sg.model_dump(exclude_defaults=True) != {}:
        sound_sg.tags.append("singular")
        word_entry.sounds.append(sound_sg)

    if sound_pl.model_dump(exclude_defaults=True) != {}:
        sound_pl.tags.append("plural")
        word_entry.sounds.append(sound_pl)


def process_transcription_la_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-la
    sound = Sound()
    cleaned_node = clean_node(wxr, {}, template_node)
    ipa_match = re.search(r"\((.*?)\): \[(.*?)\]", cleaned_node)

    if ipa_match:
        sound.ipa = ipa_match.group(2)
        sound.tags = [ipa_match.group(1).strip()]
        word_entry.sounds.append(sound)


def process_transcription_grc_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-grc
    sound = Sound()
    cleaned_node = clean_node(wxr, {}, template_node)
    ipa_with_labels = re.findall(r"\* (.*?): \[(.*?)\]", cleaned_node)
    for label, ipa in ipa_with_labels:
        sound = Sound(ipa=ipa, tags=[label.strip()])
        word_entry.sounds.append(sound)


def extract_ipa(
    wxr: WiktextractContext,
    sound: Sound,
    template_params: dict[str, WikiNode],
    key: Union[str, int],
):
    ipa = clean_node(wxr, {}, template_params.get(key, ""))
    if ipa:
        sound.ipa = ipa


def extract_audio_file(
    wxr: WiktextractContext,
    sound: Sound,
    template_params: dict[str, WikiNode],
    key: Union[str, int],
):
    audio_file = clean_node(wxr, {}, template_params.get(key, ""))
    if audio_file:
        audio_url_dict = create_audio_url_dict(audio_file)
        for dict_key, dict_value in audio_url_dict.items():
            if dict_value:
                if dict_key in sound.model_fields:
                    setattr(sound, dict_key, dict_value)
                else:
                    wxr.wtp.debug(
                        f"Unknown key {dict_key} in audio_url_dict",
                        sortid="extractor/ru/pronunciation/add_audio_file/123",
                    )


def extract_tags(
    wxr: WiktextractContext,
    sounds: Union[Sound, list[Sound]],
    template_params: dict[str, WikiNode],
):
    tags = clean_node(wxr, {}, template_params.get("норма", ""))
    if tags:
        if isinstance(sounds, list):
            for sound in sounds:
                sound.tags = [tags]
        else:
            sounds.tags = [tags]


def extract_homophones(
    wxr: WiktextractContext,
    sounds: Union[Sound, list[Sound]],
    template_params: dict[str, WikiNode],
):
    homophones_raw = clean_node(wxr, {}, template_params.get("омофоны", ""))
    homophones = [
        Linkage(word=h.strip()) for h in homophones_raw.split(",") if h.strip()
    ]
    if homophones:
        if isinstance(sounds, list):
            for sound in sounds:
                sound.homophones = homophones
        else:
            sounds.homophones = homophones


TRANSCRIPTION_TEMPLATE_PROCESSORS = {
    "transcription": process_transcription_template,
    "transcriptions": process_transcriptions_template,
    "transcription-ru": process_transcription_ru_template,
    "transcriptions-ru": process_transcriptions_ru_template,
    "transcription-la": process_transcription_la_template,
    "transcription-uk": None,
    "transcription-grc": process_transcription_grc_template,
    "transcription eo": None,
}


def extract_pronunciation(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
):
    unprocessed_nodes: WikiNodeChildrenList = []
    for child in level_node.filter_empty_str_child():
        if isinstance(child, WikiNode) and child.kind == NodeKind.TEMPLATE:
            template_name = child.template_name
            if template_name in TRANSCRIPTION_TEMPLATE_PROCESSORS:
                processor = TRANSCRIPTION_TEMPLATE_PROCESSORS.get(template_name)
                if processor:
                    processor(wxr, word_entry, child)
            elif template_name in ["audio", "аудио", "медиа"]:
                # XXX: Process simple audio file templates
                pass
            else:
                unprocessed_nodes.append(child)
        else:
            unprocessed_nodes.append(child)

    if unprocessed_nodes and clean_node(wxr, {}, unprocessed_nodes).strip():
        wxr.wtp.debug(
            f"Unprocessed nodes in pronunciation section: {unprocessed_nodes}",
            sortid="extractor/ru/pronunciation/extract_pronunciation/24",
        )
