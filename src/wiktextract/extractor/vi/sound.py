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
    for node in level_node.children:
        if isinstance(node, TemplateNode):
            if node.template_name == "vie-pron":
                extract_vie_pron_template(wxr, base_data, node)
            elif node.template_name in [
                "âm thanh-IPA",
                "pron-audio",
                "audio-for-pron",
            ]:
                extract_pron_audio_template(wxr, base_data, node)
            elif node.template_name == "tyz-IPA":
                extract_tyz_ipa_template(wxr, base_data, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_sound_list_item(wxr, base_data, list_item)


def extract_sound_list_item(
    wxr: WiktextractContext, base_data: WordEntry, list_item: WikiNode
):
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["âm thanh", "Audio", "Âm thanh"]:
                extract_audio_template(wxr, base_data, node, 1)
            elif node.template_name in ["âm thanh-2", "audio"]:
                extract_audio_template(wxr, base_data, node, 2)
            elif node.template_name in [
                "IPA",
                "IPA2",
                "IPA3",
                "IPA4",
                "fra-IPA",
                "fr-IPA",
            ]:
                extract_ipa_template(wxr, base_data, node, "IPA")
            elif node.template_name in ["enPR", "AHD"]:
                extract_ipa_template(wxr, base_data, node, "enPR")
            elif node.template_name in ["rhymes", "rhyme"]:
                extract_rhymes_template(wxr, base_data, node)
            elif node.template_name in ["hyphenation", "hyph"]:
                extract_hyphenation_template(wxr, base_data, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_sound_list_item(wxr, base_data, child_list_item)


@dataclass
class TableHeader:
    text: str
    index: int
    span: int


def extract_vie_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if col_index == 0:
                        col_headers.clear()
                    colspan = int(cell.attrs.get("colspan", "1"))
                    col_headers.append(
                        TableHeader(
                            clean_node(wxr, None, cell), col_index, colspan
                        )
                    )
                    col_index += colspan
                else:
                    colspan = int(cell.attrs.get("colspan", "1"))
                    for span_tag in cell.find_html(
                        "span", attr_name="class", attr_value="IPA"
                    ):
                        extract_vie_pron_span_tag(
                            wxr,
                            base_data,
                            span_tag,
                            col_index,
                            colspan,
                            col_headers,
                        )
                        col_index += colspan
                    for td_tag in cell.find_html("td"):
                        colspan = int(td_tag.attrs.get("colspan", "1"))
                        for span_tag in td_tag.find_html(
                            "span", attr_name="class", attr_value="IPA"
                        ):
                            extract_vie_pron_span_tag(
                                wxr,
                                base_data,
                                span_tag,
                                col_index,
                                colspan,
                                col_headers,
                            )
                        col_index += colspan

    for link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link)


def extract_vie_pron_span_tag(
    wxr: WiktextractContext,
    base_data: WordEntry,
    span_tag: HTMLNode,
    index: str,
    colspan: int,
    col_headers: list[TableHeader],
):
    ipa = clean_node(wxr, None, span_tag)
    if ipa != "":
        sound = Sound(ipa=ipa)
        for header in col_headers:
            if (
                index < header.index + header.span
                and index + colspan > header.index
            ):
                sound.raw_tags.append(header.text)
        translate_raw_tags(sound)
        base_data.sounds.append(sound)


def extract_pron_audio_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    file = clean_node(wxr, None, t_node.template_parameters.get("file", ""))
    if file == "":
        return
    sound = Sound()
    set_sound_file_url_fields(wxr, file, sound)
    place = clean_node(wxr, None, t_node.template_parameters.get("place", ""))
    if place != "":
        sound.raw_tags.append(place)
    sound.ipa = clean_node(
        wxr, None, t_node.template_parameters.get("pron", "")
    )
    translate_raw_tags(sound)
    base_data.sounds.append(sound)


def extract_audio_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    start_arg: int,
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:âm_thanh
    # https://vi.wiktionary.org/wiki/Bản_mẫu:âm_thanh-2
    file = clean_node(wxr, None, t_node.template_parameters.get(start_arg, ""))
    if file == "":
        return
    sound = Sound()
    set_sound_file_url_fields(wxr, file, sound)
    raw_tag = clean_node(
        wxr, None, t_node.template_parameters.get(start_arg + 1, "")
    )
    if raw_tag != "":
        sound.raw_tags.append(raw_tag)
    translate_raw_tags(sound)
    base_data.sounds.append(sound)


def extract_tyz_ipa_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list in expanded_node.find_child(NodeKind.LIST):
        for list_item in list.find_child(NodeKind.LIST_ITEM):
            sound = Sound()
            for node in list_item.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
                    raw_tag = clean_node(wxr, None, node)
                    if raw_tag != "":
                        sound.raw_tags.append(raw_tag)
                elif (
                    isinstance(node, HTMLNode)
                    and node.tag == "span"
                    and "IPA" in node.attrs.get("class", "").split()
                ):
                    sound.ipa = clean_node(wxr, None, node)
                elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    clean_node(wxr, base_data, node)
            if sound.ipa != "":
                base_data.sounds.append(sound)


def extract_ipa_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    ipa_class: str,
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:IPA
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tags = []
    for span_tag in expanded_node.find_html("span"):
        class_names = span_tag.attrs.get("class", "").split()
        if "qualifier-content" in class_names:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                raw_tags.append(raw_tag)
        elif ipa_class in class_names:
            ipa = clean_node(wxr, None, span_tag)
            if ipa != "":
                sound = Sound(ipa=ipa, raw_tags=raw_tags)
                translate_raw_tags(sound)
                base_data.sounds.append(sound)

    for link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link)


def extract_rhymes_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:rhymes
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="IPA"
    ):
        rhyme = clean_node(wxr, None, span_tag)
        if rhyme != "":
            base_data.sounds.append(Sound(rhymes=rhyme))

    for link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link)


def extract_hyphenation_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://vi.wiktionary.org/wiki/Bản_mẫu:hyphenation
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        h_str = clean_node(wxr, None, span_tag)
        h_data = Hyphenation()
        for part in h_str.split("‧"):
            part = part.strip()
            if part != "":
                h_data.parts.append(part)
        if len(h_data.parts) > 0:
            base_data.hyphenations.append(h_data)


def extract_homophone_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list in level_node.find_child(NodeKind.LIST):
        for list_item in list.find_child(NodeKind.LIST_ITEM):
            for link_node in list_item.find_child(NodeKind.LINK):
                homophone = clean_node(wxr, None, link_node)
                if homophone != "":
                    base_data.sounds.append(Sound(homophone=homophone))
