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
from .models import Sound, WordEntry
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
        if isinstance(node, TemplateNode) and node.template_name.lower() in [
            "âm thanh",
            "audio",
            "âm thanh",
        ]:
            extract_audio_template(wxr, base_data, node)


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
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    file = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if file == "":
        return
    sound = Sound()
    set_sound_file_url_fields(wxr, file, sound)
    raw_tag = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
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
