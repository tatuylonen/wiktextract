from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags

SOUND_TEMPLATES = frozenset(["발음 듣기", "IPA", "ko-IPA", "ja-pron"])


def extract_sound_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        extract_sound_template(wxr, word_entry, t_node)


def extract_sound_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    if node.template_name == "발음 듣기":
        extract_listen_pronunciation_template(wxr, word_entry, node)
    elif node.template_name == "IPA":
        extract_ipa_template(wxr, word_entry, node)
    elif node.template_name == "ko-IPA":
        extract_ko_ipa_template(wxr, word_entry, node)
    elif node.template_name == "ja-pron":
        extract_ja_pron_template(wxr, word_entry, node)


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


def extract_ko_ipa_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://ko.wiktionary.org/wiki/틀:ko-IPA
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for ul_tag in expanded_node.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            sound = Sound()
            for i_tag in li_tag.find_html("i"):
                sound.raw_tags.append(clean_node(wxr, None, i_tag))
                break
            for span_tag in li_tag.find_html("span"):
                span_class = span_tag.attrs.get("class", "")
                if span_class == "IPA":
                    sound.ipa = clean_node(wxr, None, span_tag)
                elif span_class == "Kore":
                    sound.hangul = clean_node(wxr, None, span_tag)
            if sound.hangul != "" or sound.ipa != "":
                translate_raw_tags(sound)
                word_entry.sounds.append(sound)

    for table in expanded_node.find_html("table"):
        for tr_tag in table.find_html("tr"):
            sound = Sound()
            for th_tag in tr_tag.find_html("th"):
                for span_tag in th_tag.find_html("span"):
                    sound.raw_tags.append(clean_node(wxr, None, span_tag))
                break
            for td_tag in tr_tag.find_html(
                "td", attr_name="class", attr_value="IPA"
            ):
                sound.roman = clean_node(wxr, None, td_tag)
                break
            if sound.roman != "":
                translate_raw_tags(sound)
                word_entry.sounds.append(sound)

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)


def extract_ja_pron_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://ko.wiktionary.org/wiki/틀:ja-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for ul_tag in expanded_node.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            sound = Sound()
            for span_tag in li_tag.find_html("span"):
                span_class = span_tag.attrs.get("class", "")
                if span_class == "usage-label-accent":
                    sound.raw_tags.append(
                        clean_node(wxr, None, span_tag).strip("()")
                    )
                elif span_class == "Jpan":
                    sound.other = clean_node(wxr, None, span_tag)
                elif span_class == "Latn":
                    sound.roman = clean_node(wxr, None, span_tag)
                elif span_class == "IPA":
                    sound.ipa = clean_node(wxr, None, span_tag)
            if sound.ipa != "" or sound.roman != "":
                word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, expanded_node)
