import re
from dataclasses import dataclass

from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_sound_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "th-pron":
            extract_th_pron_template(wxr, base_data, t_node)


@dataclass
class TableHeader:
    text: str
    rowspan: int


def extract_th_pron_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
) -> None:
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
