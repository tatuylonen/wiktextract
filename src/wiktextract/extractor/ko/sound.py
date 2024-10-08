from wikitextprocessor import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry


def extract_listen_pronunciation_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://ko.wiktionary.org/wiki/틀:발음_듣기
    for key in range(1, 9):
        if key not in node.template_parameters:
            break
        value = clean_node(wxr, None, node.template_parameters[key])
        if value == "":
            continue
        elif key % 2 == 1:
            sound = Sound()
            set_sound_file_url_fields(wxr, value, sound)
            word_entry.sounds.append(sound)
        elif len(word_entry.sounds) > 0:
            word_entry.sounds[-1].raw_tags.append(value)


def extract_ipa_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://ko.wiktionary.org/wiki/틀:IPA
    for key in range(1, 5):
        if key not in node.template_parameters:
            break
        value = clean_node(wxr, None, node.template_parameters[key])
        if value == "":
            continue
        elif key % 2 == 1:
            sound = Sound(ipa=value)
            word_entry.sounds.append(sound)
        elif len(word_entry.sounds) > 0:
            word_entry.sounds[-1].raw_tags.append(value)
