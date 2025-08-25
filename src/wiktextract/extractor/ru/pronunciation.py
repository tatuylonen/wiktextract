import re

from wikitextprocessor import HTMLNode, LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def process_transcription_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription

    sound = Sound()
    template_params = template_node.template_parameters
    extract_ipa(wxr, sound, template_params, 1)
    extract_audio_file(wxr, sound, template_params, 2)
    extract_tags(wxr, sound, template_params)
    extract_homophones(wxr, sound, template_params)

    if sound.ipa != "" or sound.audio != "" or len(sound.homophones) > 0:
        word_entry.sounds.append(sound)


def process_transcriptions_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
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

    if sound_sg.ipa != "" or sound_sg.audio != "":
        sound_sg.tags.append("singular")
        word_entry.sounds.append(sound_sg)

    if sound_pl.ipa != "" or sound_pl.audio != "":
        sound_pl.tags.append("plural")
        word_entry.sounds.append(sound_pl)


def process_transcription_ru_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-ru
    sound = Sound()
    template_params = template_node.template_parameters
    sound.ipa = clean_node(wxr, None, template_params.get("вручную", ""))
    if sound.ipa == "":
        cleaned_node = clean_node(wxr, None, template_node)
        ipa_match = re.search(r"\[.+?\]", cleaned_node)
        if ipa_match is not None:
            sound.ipa = ipa_match.group()
    extract_audio_file(wxr, sound, template_params, 2)
    extract_homophones(wxr, sound, template_params)
    extract_tags(wxr, sound, template_params)

    if sound.ipa != "" or sound.audio != "" or len(sound.homophones) > 0:
        word_entry.sounds.append(sound)


def process_transcriptions_ru_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    sound_sg = Sound()
    sound_pl = Sound()
    template_params = template_node.template_parameters
    cleaned_node = clean_node(wxr, None, template_node)
    ipa_matches = re.findall(r"\[.+?\]", cleaned_node)
    if len(ipa_matches) > 0:
        sound_sg.ipa = ipa_matches[0]
    if len(ipa_matches) > 1:
        sound_pl.ipa = ipa_matches[1]
    extract_audio_file(wxr, sound_sg, template_params, 3)
    extract_audio_file(wxr, sound_pl, template_params, 4)
    extract_tags(wxr, [sound_sg, sound_pl], template_params)
    extract_homophones(wxr, sound_sg, template_params)

    if (
        sound_sg.ipa != ""
        or sound_sg.audio != ""
        or len(sound_sg.homophones) > 0
    ):
        sound_sg.tags.append("singular")
        word_entry.sounds.append(sound_sg)
    if (
        sound_pl.ipa != ""
        or sound_pl.audio != ""
        or len(sound_pl.homophones) > 0
    ):
        sound_pl.tags.append("plural")
        word_entry.sounds.append(sound_pl)


def process_transcription_la_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-la
    sound = Sound()
    cleaned_node = clean_node(wxr, None, template_node)
    ipa_match = re.search(r"\((.+?)\): (\[.+?\])", cleaned_node)
    if ipa_match is not None:
        sound.ipa = ipa_match.group(2)
        sound.raw_tags.append(ipa_match.group(1).strip())
        word_entry.sounds.append(sound)


def process_transcription_grc_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: WikiNode
):
    # https://ru.wiktionary.org/wiki/Шаблон:transcription-grc
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for node in expanded_node.children:
        if (
            isinstance(node, HTMLNode)
            and node.tag == "span"
            and node.attrs.get("class", "") == "IPA"
        ):
            ipa = clean_node(wxr, None, node)
            if ipa != "":
                word_entry.sounds.append(Sound(ipa=ipa))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                text = clean_node(wxr, None, list_item.children)
                for raw_tag, ipa in re.findall(r"(.+?): (\[.+?\])", text):
                    word_entry.sounds.append(
                        Sound(ipa=ipa, raw_tags=[raw_tag.strip()])
                    )


def extract_ipa(
    wxr: WiktextractContext,
    sound: Sound,
    template_params: dict[str, WikiNode],
    key: str | int,
):
    ipa = clean_node(wxr, {}, template_params.get(key, ""))
    if ipa != "":
        sound.ipa = f"[{ipa}]"


def extract_audio_file(
    wxr: WiktextractContext,
    sound: Sound,
    template_params: dict[str, WikiNode],
    key: str | int,
):
    audio_file = clean_node(wxr, None, template_params.get(key, ""))
    if audio_file != "":
        set_sound_file_url_fields(wxr, audio_file, sound)


def extract_tags(
    wxr: WiktextractContext,
    sounds: Sound | list[Sound],
    template_params: dict[str, WikiNode],
):
    tags = clean_node(wxr, None, template_params.get("норма", ""))
    if tags != "":
        if isinstance(sounds, list):
            for sound in sounds:
                sound.raw_tags = [tags]
        else:
            sounds.raw_tags = [tags]


def extract_homophones(
    wxr: WiktextractContext,
    sounds: Sound | list[Sound],
    template_params: dict[str, WikiNode],
):
    homophones_raw = clean_node(wxr, {}, template_params.get("омофоны", ""))
    homophones = [
        h.strip() for h in homophones_raw.split(",") if h.strip() != ""
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


def extract_pronunciation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for child in level_node.find_child(NodeKind.TEMPLATE):
        template_name = child.template_name
        if template_name in TRANSCRIPTION_TEMPLATE_PROCESSORS:
            processor = TRANSCRIPTION_TEMPLATE_PROCESSORS.get(template_name)
            if processor is not None:
                processor(wxr, word_entry, child)
        elif template_name in ["audio", "аудио", "медиа"]:
            audio_file = clean_node(
                wxr, None, child.template_parameters.get(1, "")
            ).strip()
            if audio_file != "":
                if len(word_entry.sounds) > 0:
                    set_sound_file_url_fields(
                        wxr, audio_file, word_entry.sounds[-1]
                    )
                else:
                    sound = Sound()
                    set_sound_file_url_fields(wxr, audio_file, sound)
                    word_entry.sounds.append(sound)


def extract_homophone_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    homophones = []
    for link_node in level_node.find_child_recursively(NodeKind.LINK):
        homophone = clean_node(wxr, None, link_node)
        if len(homophone) > 0:
            homophones.append(homophone)
    if len(homophones) > 0:
        sound = Sound(homophones=homophones)
        word_entry.sounds.append(sound)


def extract_rhyme_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            for node in list_item.children:
                if isinstance(node, str) and node.strip().endswith(":"):
                    for raw_tag in node.strip(": ").split(","):
                        raw_tag = raw_tag.strip()
                        if raw_tag != "":
                            raw_tags.append(raw_tag)
                elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    rhyme = clean_node(wxr, None, node)
                    if rhyme != "":
                        sound = Sound(rhymes=rhyme, raw_tags=raw_tags)
                        translate_raw_tags(sound)
                        word_entry.sounds.append(sound)
