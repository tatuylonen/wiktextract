import re
from dataclasses import dataclass

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Hyphenation, Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        extract_sound_template(wxr, base_data, t_node)
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                extract_sound_template(wxr, base_data, t_node)


def extract_sound_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    if t_node.template_name == "IPA":
        extract_ipa_template(wxr, base_data, t_node)
    elif t_node.template_name == "X-SAMPA":
        extract_x_sampa_template(wxr, base_data, t_node)
    elif t_node.template_name == "enPR":
        extract_enpr_template(wxr, base_data, t_node)
    elif t_node.template_name == "audio":
        extract_audio_template(wxr, base_data, t_node)
    elif t_node.template_name == "th-pron":
        extract_th_pron_template(wxr, base_data, t_node)
    elif t_node.template_name == "lo-pron":
        extract_lo_pron_template(wxr, base_data, t_node)
    elif t_node.template_name in ["ja-pron", "ja-IPA"]:
        extract_ja_pron_template(wxr, base_data, t_node)


def extract_ipa_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    extract_ipa_li_tag(wxr, base_data, expanded_node)
    clean_node(wxr, base_data, expanded_node)


def extract_ipa_li_tag(
    wxr: WiktextractContext, base_data: WordEntry, li_tag: HTMLNode
):
    raw_tag = ""
    for span_tag in li_tag.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "").split()
        if "qualifier-content" in span_class:
            raw_tag = clean_node(wxr, None, span_tag)
        elif "IPA" in span_class:
            sound = Sound(ipa=clean_node(wxr, None, span_tag))
            if raw_tag != "":
                sound.raw_tags.append(raw_tag)
                translate_raw_tags(sound)
            if sound.ipa != "":
                base_data.sounds.append(sound)
        elif "Latn" in span_class:
            sound = Sound(roman=clean_node(wxr, None, span_tag))
            if raw_tag != "":
                sound.raw_tags.append(raw_tag)
                translate_raw_tags(sound)
            if sound.roman != "":
                base_data.sounds.append(sound)


def extract_ja_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for li_tag in expanded_node.find_html_recursively("li"):
        extract_ipa_li_tag(wxr, base_data, li_tag)
    clean_node(wxr, base_data, expanded_node)


def extract_x_sampa_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    sound = Sound(
        ipa=clean_node(wxr, None, t_node.template_parameters.get(1, "")),
        tags=["X-SAMPA"],
    )
    if sound.ipa != "":
        base_data.sounds.append(sound)


def extract_enpr_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    sound = Sound(
        enpr=clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    )
    if sound.enpr != "":
        base_data.sounds.append(sound)


def extract_audio_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    sound = Sound()
    filename = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if filename != "":
        set_sound_file_url_fields(wxr, filename, sound)
        for raw_tag in clean_node(
            wxr, None, t_node.template_parameters.get("a", "")
        ).split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                sound.raw_tags.append(raw_tag)
        translate_raw_tags(sound)
        base_data.sounds.append(sound)
        clean_node(wxr, base_data, t_node)


@dataclass
class TableHeader:
    text: str
    rowspan: int


def extract_th_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://th.wiktionary.org/wiki/แม่แบบ:th-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table_tag in expanded_node.find_html("table"):
        row_headers = []
        for tr_tag in table_tag.find_html("tr"):
            field = "other"
            new_headers = []
            for header in row_headers:
                if header.rowspan > 1:
                    header.rowspan -= 1
                    new_headers.append(header)
            row_headers = new_headers
            for th_tag in tr_tag.find_html("th"):
                header_str = clean_node(wxr, None, th_tag)
                if header_str.startswith("(มาตรฐาน) สัทอักษรสากล"):
                    field = "ipa"
                elif header_str.startswith("คำพ้องเสียง"):
                    field = "homophone"
                elif header_str == "ไฟล์เสียง":
                    field = "audio"
                elif header_str != "":
                    rowspan = 1
                    rowspan_str = th_tag.attrs.get("rowspan", "1")
                    if re.fullmatch(r"\d+", rowspan_str):
                        rowspan = int(rowspan_str)
                    row_headers.append(TableHeader(header_str, rowspan))

            for td_tag in tr_tag.find_html("td"):
                if field == "audio":
                    for link_node in td_tag.find_child(NodeKind.LINK):
                        filename = clean_node(wxr, None, link_node.largs[0])
                        if filename != "":
                            sound = Sound()
                            set_sound_file_url_fields(wxr, filename, sound)
                            base_data.sounds.append(sound)
                elif field == "homophone":
                    for span_tag in td_tag.find_html_recursively(
                        "span", attr_name="lang", attr_value="th"
                    ):
                        word = clean_node(wxr, None, span_tag)
                        if word != "":
                            base_data.sounds.append(Sound(homophone=word))
                else:
                    data = clean_node(wxr, None, td_tag)
                    if data != "":
                        sound = Sound()
                        setattr(sound, field, data)
                        for header in row_headers:
                            sound.raw_tags.append(header.text)
                        translate_raw_tags(sound)
                        base_data.sounds.append(sound)

    clean_node(wxr, base_data, expanded_node)


def extract_lo_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://th.wiktionary.org/wiki/แม่แบบ:lo-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            field = "other"
            raw_tag = ""
            for node in list_item.children:
                if isinstance(node, HTMLNode) and node.tag == "span":
                    span_class = node.attrs.get("class", "")
                    if "qualifier-content" in span_class:
                        raw_tag = clean_node(wxr, None, node)
                    elif span_class == "IPA":
                        ipa = clean_node(wxr, None, node)
                        if ipa != "":
                            sound = Sound(ipa=ipa)
                            if raw_tag != "":
                                sound.raw_tags.append(raw_tag)
                                translate_raw_tags(sound)
                            base_data.sounds.append(sound)
                    else:
                        span_lang = node.attrs.get("lang", "")
                        if span_lang == "lo" and field == "hyphenation":
                            span_str = clean_node(wxr, None, node)
                            if span_str != "":
                                base_data.hyphenations.append(
                                    Hyphenation(parts=span_str.split("-"))
                                )
                elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    link_str = clean_node(wxr, None, node)
                    if link_str == "สัทอักษรสากล":
                        field = "ipa"
                    elif link_str != "" and field == "rhymes":
                        base_data.sounds.append(Sound(rhymes=link_str))
                elif isinstance(node, str) and node.strip().endswith(":"):
                    node = node.strip()
                    if node == "การแบ่งพยางค์:":
                        field = "hyphenation"
                    elif node == "สัมผัส:":
                        field = "rhymes"

    clean_node(wxr, base_data, expanded_node)
