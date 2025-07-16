from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_sound_list_item(wxr, word_entry, list_item)


def extract_sound_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    for t_node in list_item.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in [
            "IPA",
            "Çeviri yazı",
            "IPA-Söyleniş",
            "Çeviri Yazı",
            "IPA-Telaffuz",
            "sıfat-telaffuz",
            "Sıfat-Telaffuz",
        ]:
            extract_ipa_template(wxr, word_entry, t_node)
        elif t_node.template_name in ["h", "heceleme"]:
            extract_heceleme_template(wxr, word_entry, t_node)
        elif t_node.template_name.lower() in ["ses", "audio"]:
            extract_ses_template(wxr, word_entry, t_node)
        elif t_node.template_name in [
            "eş sesliler",
            "sesteşler",
            "eşsesli",
            "eşsesliler",
        ]:
            extract_eş_sesliler(wxr, word_entry, t_node)
        elif t_node.template_name in ["kafiyeler", "kafiye"]:
            extract_kafiyeler(wxr, word_entry, t_node)


def extract_ipa_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:IPA
    for index in [1, 2, 3]:
        ipa = clean_node(wxr, None, t_node.template_parameters.get(index, ""))
        if ipa != "":
            word_entry.sounds.append(Sound(ipa=ipa))


def extract_heceleme_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:heceleme
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_node in expanded_node.find_html(
        "span", attr_name="class", attr_value="mention-Latn"
    ):
        hyphenation = clean_node(wxr, None, span_node)
        if hyphenation != "":
            word_entry.hyphenations.append(
                Hyphenation(parts=hyphenation.split("‧"))
            )
    clean_node(wxr, word_entry, expanded_node)


def extract_ses_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:ses
    filename = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if filename != "":
        sound = Sound()
        set_sound_file_url_fields(wxr, filename, sound)
        raw_tag = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
        if raw_tag != "":
            sound.raw_tags.append(raw_tag)
            translate_raw_tags(sound)
        word_entry.sounds.append(sound)


def extract_eş_sesliler(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:eş_sesliler
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get("dil", ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        homophone = clean_node(wxr, None, span_tag)
        if homophone != "":
            word_entry.sounds.append(Sound(homophone=homophone))


def extract_kafiyeler(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:kafiyeler
    for index in range(1, 7):
        if index not in t_node.template_parameters:
            break
        rhyme = clean_node(wxr, None, t_node.template_parameters[index])
        if rhyme != "":
            rhyme = "-" + rhyme
            word_entry.sounds.append(Sound(rhymes=rhyme))
