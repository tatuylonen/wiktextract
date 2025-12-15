from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags

SOUND_TEMPLATES = frozenset(["발음 듣기", "IPA", "ko-IPA", "ja-pron", "audio"])


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
    elif node.template_name == "audio":
        extract_audio_template(wxr, word_entry, node)


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
            translate_raw_tags(word_entry.sounds[-1])


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
            for raw_tag in value.split(","):
                raw_tag = raw_tag.strip()
                if raw_tag != "":
                    word_entry.sounds[-1].raw_tags.append(raw_tag.strip())
            translate_raw_tags(word_entry.sounds[-1])


def extract_ko_ipa_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://ko.wiktionary.org/wiki/틀:ko-IPA
    sounds = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    clean_node(wxr, word_entry, expanded_node)
    for ul_node in expanded_node.find_html("ul"):
        for li_node in ul_node.find_html("li"):
            if "ko-pron__ph" in li_node.attrs.get("class", ""):
                for span_node in li_node.find_html(
                    "span", attr_name="lang", attr_value="ko"
                ):
                    hangeul_str = clean_node(wxr, None, span_node).strip("[]")
                    for hangeul in hangeul_str.split("/"):
                        if hangeul != "":
                            sounds.append(
                                Sound(hangeul=hangeul, tags=["phonetic"])
                            )
            else:
                raw_tags = []
                for link_node in li_node.find_child(NodeKind.LINK):
                    raw_tag = clean_node(wxr, None, link_node)
                    if raw_tag not in ["", "IPA"]:
                        raw_tags.append(raw_tag)
                for span_node in li_node.find_html(
                    "span", attr_name="class", attr_value="IPA"
                ):
                    ipas = clean_node(wxr, None, span_node)
                    for ipa in ipas.split("~"):
                        ipa = ipa.strip()
                        if ipa != "":
                            sound = Sound(ipa=ipa, raw_tags=raw_tags)
                            translate_raw_tags(sound)
                            sounds.append(sound)

    for table in expanded_node.find_html("table"):
        for tr in table.find_html("tr"):
            raw_tag = ""
            for th in tr.find_html("th"):
                raw_tag = clean_node(wxr, None, th)
            for td in tr.find_html("td"):
                roman = clean_node(wxr, None, td)
                if roman != "":
                    sound = Sound(roman=roman)
                    if raw_tag != "":
                        sound.raw_tags.append(raw_tag)
                        translate_raw_tags(sound)
                    sounds.append(sound)

    audio_file = clean_node(
        wxr,
        None,
        t_node.template_parameters.get(
            "a", t_node.template_parameters.get("audio", "")
        ),
    )
    if audio_file != "":
        sound = Sound()
        set_sound_file_url_fields(wxr, audio_file, sound)
        sounds.append(sound)
    word_entry.sounds.extend(sounds)


def extract_ja_pron_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://ko.wiktionary.org/wiki/틀:ja-pron
    JA_PRON_ACCENTS = {
        "중고형": "Nakadaka",
        "평판형": "Heiban",
        "두고형": "Atamadaka",
        "미고형": "Odaka",
    }
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for ul_tag in expanded_node.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            sound = Sound()
            for span_tag in li_tag.find_html("span"):
                span_class = span_tag.attrs.get("class", "").split()
                if "usage-label-accent" in span_class:
                    sound.raw_tags.append(
                        clean_node(wxr, None, span_tag).strip("()")
                    )
                elif "Jpan" in span_class:
                    sound.other = clean_node(wxr, None, span_tag)
                elif "Latn" in span_class:
                    sound.roman = clean_node(wxr, None, span_tag)
                elif "IPA" in span_class:
                    sound.ipa = clean_node(wxr, None, span_tag)
            for link_node in li_tag.find_child(NodeKind.LINK):
                link_text = clean_node(wxr, None, link_node)
                if link_text in JA_PRON_ACCENTS:
                    sound.tags.append(JA_PRON_ACCENTS[link_text])
            if sound.ipa != "" or sound.roman != "":
                translate_raw_tags(sound)
                word_entry.sounds.append(sound)
    audio_file = node.template_parameters.get(
        "a", node.template_parameters.get("audio", "")
    ).strip()
    if audio_file != "":
        sound = Sound()
        set_sound_file_url_fields(wxr, audio_file, sound)
        word_entry.sounds.append(sound)
    clean_node(wxr, word_entry, expanded_node)


def extract_audio_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    sound = Sound()
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if filename != "":
        set_sound_file_url_fields(wxr, filename, sound)
        caption = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
        if caption != "":
            sound.raw_tags.append(caption)
        expanded_node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(t_node), expand_all=True
        )
        for span_node in expanded_node.find_html_recursively(
            "span", attr_name="class", attr_value="ib-content"
        ):
            for raw_tag in clean_node(wxr, None, span_node).split(","):
                if raw_tag != "":
                    sound.raw_tags.append(raw_tag)
        translate_raw_tags(sound)
        base_data.sounds.append(sound)
        clean_node(wxr, base_data, t_node)
