import re
import string
from collections import defaultdict

from wikitextprocessor import WikiNode

from wiktextract.extractor.es.models import Sound, Spelling, WordEntry
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def group_and_subgroup_keys(data):
    pattern = re.compile(r"(\d*)(\D+)(\d*)")

    grouped = defaultdict(lambda: defaultdict(list))

    for key in data.copy().keys():
        if isinstance(key, str):
            match = pattern.match(key)
            if match:
                initial_digit = match.group(1) or "0"
                last_digit = match.group(3) or "1"
                grouped[initial_digit][last_digit].append(key)

        elif isinstance(key, int) and key == 1:
            data["fone"] = data[key]
            grouped["0"]["1"].append("fone")

    return grouped


def process_pron_graf_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:pron-graf
    sound_data: list[Sound] = []
    spelling_data: list[Spelling] = []

    sound_keys_grouped = group_and_subgroup_keys(
        template_node.template_parameters
    )

    for sound_keys in sound_keys_grouped.values():
        sound = Sound()
        for variant_keys in sound_keys.values():
            spelling_g = Spelling(
                same_pronunciation=True
            )  # Collect different grafía
            spelling_v = Spelling(
                same_pronunciation=False
            )  # Collect different variants
            for key in variant_keys:
                key_plain = key.strip(string.digits)
                value_raw = template_node.template_parameters.get(key)
                value = clean_node(wxr, {}, value_raw).strip()
                if key_plain == "fone" and value != "...":
                    sound.ipa.append(value)
                elif key_plain == "fono":
                    sound.phonetic_transcription.append(value)
                elif key_plain == "tl":
                    sound.roman.append(value)
                elif key_plain == "ts":
                    sound.syllabic.append(value)
                elif key_plain == "pron":
                    if value != "no":
                        sound.tag.append(value)
                elif key_plain == "audio":
                    audio_url_dict = create_audio_url_dict(value)
                    for dict_key, dict_value in audio_url_dict.items():
                        if dict_value and dict_key in sound.model_fields:
                            getattr(sound, dict_key).append(dict_value)
                elif key_plain in ["g", "ga", "grafía alternativa"]:
                    spelling_g.alternative = value
                elif key_plain == "gnota":
                    spelling_g.note = value
                elif key_plain in ["v", "variante"]:
                    spelling_v.alternative = value
                elif key_plain == "vnota":
                    spelling_v.note = value
                elif key not in ["leng"]:
                    wxr.wtp.debug(
                        f"Skipped extracting key {key} from pron-graf template",
                        sortid="extractor/es/pronunciation/extract_pronunciation/77",
                    )

            if len(spelling_g.model_dump(exclude_defaults=True)) > 1:
                spelling_data.append(spelling_g)
            if len(spelling_v.model_dump(exclude_defaults=True)) > 1:
                spelling_data.append(spelling_v)

        if len(sound.model_dump(exclude_defaults=True)) > 0:
            sound_data.append(sound)

    if len(sound_data) > 0:
        word_entry.sounds = sound_data
    if len(spelling_data) > 0:
        word_entry.spellings = spelling_data


def process_audio_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: WikiNode
):
    # https://es.wiktionary.org/wiki/Plantilla:audio
    sound = Sound()
    audio = template_node.template_parameters.get(1)
    if audio:
        audio_url_dict = create_audio_url_dict(audio)
        for dict_key, dict_value in audio_url_dict.items():
            if dict_value and dict_key in sound.model_fields:
                getattr(sound, dict_key).append(dict_value)

    # XXX: Extract other parameters from the Spanish audio template

    if len(sound.model_dump(exclude_defaults=True)) > 0:
        word_entry.sounds.append(sound)
