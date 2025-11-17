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
            elif node.template_name in ["zh-pron", "zho-pron"]:
                extract_zh_pron_template(wxr, base_data, node)
            elif node.template_name in ["th-pron", "tha-pron"]:
                extract_th_pron_template(wxr, base_data, node)
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
            ] or node.template_name.endswith("-IPA"):
                extract_ipa_template(wxr, base_data, node, "IPA")
            elif node.template_name in ["enPR", "AHD"]:
                extract_ipa_template(wxr, base_data, node, "enPR")
            elif node.template_name in ["rhymes", "rhyme"]:
                extract_rhymes_template(wxr, base_data, node)
            elif node.template_name in ["hyphenation", "hyph"]:
                extract_hyphenation_template(wxr, base_data, node)
            elif node.template_name in ["homophones", "homophone", "hmp"]:
                extract_homophones_template(wxr, base_data, node)
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


def extract_zh_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    seen_lists = set()
    sounds = []
    for list_node in expanded_node.find_child_recursively(NodeKind.LIST):
        if list_node not in seen_lists:
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                sounds.extend(
                    extract_zh_pron_list_item(wxr, list_item, [], seen_lists)
                )
    for sound in sounds:
        translate_raw_tags(sound)
    base_data.sounds.extend(sounds)
    clean_node(wxr, base_data, expanded_node)


def extract_zh_pron_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    raw_tags: list[str],
    seen_lists: set[WikiNode],
) -> list[Sound]:
    current_tags = raw_tags[:]
    sounds = []
    is_first_small_tag = True
    for node in list_item_node.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                link_str = clean_node(wxr, None, node.largs)
                node_str = clean_node(wxr, None, node)
                if link_str.startswith(("File:", "Tập tin:")):
                    filename = link_str.removeprefix("File:").removeprefix(
                        "Tập tin:"
                    )
                    sound_data = Sound(raw_tags=current_tags)
                    set_sound_file_url_fields(wxr, filename, sound_data)
                    sounds.append(sound_data)
                elif node_str != "":
                    current_tags.append(node_str.strip("()"))
            elif isinstance(node, HTMLNode):
                if node.tag == "small":
                    # remove "ghi chú"(help) <sup> tag
                    if is_first_small_tag:
                        raw_tag_text = clean_node(
                            wxr,
                            None,
                            [
                                n
                                for n in node.children
                                if not (
                                    isinstance(n, HTMLNode) and n.tag == "sup"
                                )
                            ],
                        ).rstrip(":")
                        current_tags.extend(split_zh_pron_raw_tag(raw_tag_text))
                    elif len(sounds) > 0:
                        sounds[-1].raw_tags.extend(
                            split_zh_pron_raw_tag(clean_node(wxr, None, node))
                        )
                    is_first_small_tag = False
                elif node.tag == "span":
                    sounds.extend(extract_zh_pron_span(wxr, node, current_tags))
                elif (
                    node.tag == "table"
                    and len(current_tags) > 0
                    and current_tags[-1] == "Đồng âm"
                ):
                    sounds.extend(
                        extract_zh_pron_homophones_table(
                            wxr, node, current_tags
                        )
                    )
            elif node.kind == NodeKind.LIST:
                seen_lists.add(node)
                for next_list_item in node.find_child(NodeKind.LIST_ITEM):
                    sounds.extend(
                        extract_zh_pron_list_item(
                            wxr,
                            next_list_item,
                            current_tags,
                            seen_lists,
                        )
                    )
    return sounds


def split_zh_pron_raw_tag(raw_tag_text: str) -> list[str]:
    raw_tags = []
    if "(" not in raw_tag_text:
        for raw_tag in re.split(r",|:|;| và ", raw_tag_text):
            raw_tag = raw_tag.strip().removeprefix("bao gồm").strip()
            if raw_tag != "":
                raw_tags.append(raw_tag)
    else:
        processed_offsets = []
        for match in re.finditer(r"\([^()]+\)", raw_tag_text):
            processed_offsets.append((match.start(), match.end()))
            raw_tags.extend(
                split_zh_pron_raw_tag(
                    raw_tag_text[match.start() + 1 : match.end() - 1]
                )
            )
        not_processed = ""
        last_end = 0
        for start, end in processed_offsets:
            not_processed += raw_tag_text[last_end:start]
            last_end = end
        not_processed += raw_tag_text[last_end:]
        if not_processed != raw_tag_text:
            raw_tags = split_zh_pron_raw_tag(not_processed) + raw_tags
        else:
            raw_tags.append(not_processed)
    return raw_tags


def extract_zh_pron_span(
    wxr: WiktextractContext, span_tag: HTMLNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    small_tags = []
    pron_nodes = []
    roman = ""
    phonetic_pron = ""
    for index, node in enumerate(span_tag.children):
        if isinstance(node, HTMLNode) and node.tag == "small":
            small_tags = split_zh_pron_raw_tag(clean_node(wxr, None, node))
        elif (
            isinstance(node, HTMLNode)
            and node.tag == "span"
            and "-Latn" in node.attrs.get("lang", "")
        ):
            roman = clean_node(wxr, None, node).strip("() ")
        elif isinstance(node, str) and node.strip() == "[Phonetic:":
            phonetic_pron = clean_node(
                wxr, None, span_tag.children[index + 1 :]
            ).strip("] ")
            break
        else:
            pron_nodes.append(node)
    for zh_pron in split_zh_pron(clean_node(wxr, None, pron_nodes)):
        zh_pron = zh_pron.strip("[]： ")
        if len(zh_pron) > 0:
            if "IPA" in span_tag.attrs.get("class", ""):
                sounds.append(
                    Sound(ipa=zh_pron, roman=roman, raw_tags=raw_tags)
                )
            else:
                sounds.append(
                    Sound(zh_pron=zh_pron, roman=roman, raw_tags=raw_tags)
                )
    if len(sounds) > 0:
        sounds[-1].raw_tags.extend(small_tags)
    if phonetic_pron != "":
        sounds.append(
            Sound(
                zh_pron=phonetic_pron,
                roman=roman,
                raw_tags=raw_tags + ["Phonetic"],
            )
        )
    return sounds


def split_zh_pron(zh_pron: str) -> list[str]:
    # split by comma and other symbols that outside parentheses
    parentheses = 0
    pron_list = []
    pron = ""
    for c in zh_pron:
        if (
            (c in [",", ";", "→"] or (c == "/" and not zh_pron.startswith("/")))
            and parentheses == 0
            and len(pron.strip()) > 0
        ):
            pron_list.append(pron.strip())
            pron = ""
        elif c == "(":
            parentheses += 1
            pron += c
        elif c == ")":
            parentheses -= 1
            pron += c
        else:
            pron += c

    if pron.strip() != "":
        pron_list.append(pron)
    return pron_list


def extract_zh_pron_homophones_table(
    wxr: WiktextractContext, table: HTMLNode, raw_tags: list[str]
) -> list[Sound]:
    sounds = []
    for td_tag in table.find_html_recursively("td"):
        for span_tag in td_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            span_lang = span_tag.attrs.get("lang", "")
            span_str = clean_node(wxr, None, span_tag)
            if (
                span_str not in ["", "／"]
                and span_lang != ""
                and span_class in ["Hant", "Hans", "Hani"]
            ):
                sound = Sound(homophone=span_str, raw_tags=raw_tags)
                if span_class == "Hant":
                    sound.tags.append("Traditional-Chinese")
                elif span_class == "Hans":
                    sound.tags.append("Simplified-Chinese")
                sounds.append(sound)
    return sounds


def extract_th_pron_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://vi.wiktionary.org/wiki/Bản mẫu:th-pron
    @dataclass
    class TableHeader:
        raw_tags: list[str]
        rowspan: int

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    sounds = []
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
                if header_str.startswith("(Tiêu chuẩn) IPA"):
                    field = "ipa"
                elif header_str.startswith("Từ đồng âm"):
                    field = "homophone"
                elif header_str == "Âm thanh":
                    field = "audio"
                elif header_str != "":
                    rowspan = 1
                    rowspan_str = th_tag.attrs.get("rowspan", "1")
                    if re.fullmatch(r"\d+", rowspan_str):
                        rowspan = int(rowspan_str)
                    header = TableHeader([], rowspan)
                    for line in header_str.splitlines():
                        for raw_tag in line.strip("{}\n ").split(";"):
                            raw_tag = raw_tag.strip()
                            if raw_tag != "":
                                header.raw_tags.append(raw_tag)
                    row_headers.append(header)

            for td_tag in tr_tag.find_html("td"):
                if field == "audio":
                    for link_node in td_tag.find_child(NodeKind.LINK):
                        filename = clean_node(wxr, None, link_node.largs[0])
                        if filename != "":
                            sound = Sound()
                            set_sound_file_url_fields(wxr, filename, sound)
                            sounds.append(sound)
                elif field == "homophone":
                    for span_tag in td_tag.find_html_recursively(
                        "span", attr_name="lang", attr_value="th"
                    ):
                        word = clean_node(wxr, None, span_tag)
                        if word != "":
                            sounds.append(Sound(homophone=word))
                else:
                    raw_tags = []
                    for html_node in td_tag.find_child_recursively(
                        NodeKind.HTML
                    ):
                        if html_node.tag == "small":
                            node_str = clean_node(wxr, None, html_node)
                            if node_str.startswith("[") and node_str.endswith(
                                "]"
                            ):
                                for raw_tag in node_str.strip("[]").split(","):
                                    raw_tag = raw_tag.strip()
                                    if raw_tag != "":
                                        raw_tags.append(raw_tag)
                            elif len(sounds) > 0:
                                sounds[-1].roman = node_str
                        elif html_node.tag == "span":
                            node_str = clean_node(wxr, None, html_node)
                            span_lang = html_node.attrs.get("lang", "")
                            span_class = html_node.attrs.get("class", "")
                            if node_str != "" and (
                                span_lang == "th" or span_class in ["IPA", "tr"]
                            ):
                                sound = Sound(raw_tags=raw_tags)
                                for header in row_headers:
                                    sound.raw_tags.extend(header.raw_tags)
                                translate_raw_tags(sound)
                                if "romanization" in sound.tags:
                                    field = "roman"
                                setattr(sound, field, node_str)
                                sounds.append(sound)

    base_data.sounds.extend(sounds)
    clean_node(wxr, base_data, expanded_node)


def extract_homophones_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    homophones = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for top_span in expanded_node.find_html(
        "span", attr_name="class", attr_value="homophones"
    ):
        for span_tag in top_span.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            span_class = span_tag.attrs.get("class", "").split()
            if "tr" in span_class and len(homophones) > 0:
                homophones[-1].roman = clean_node(wxr, None, span_tag)
            elif span_lang == lang_code:
                homophone = clean_node(wxr, None, span_tag)
                if homophone != "":
                    homophones.append(Sound(homophone=homophone))
            elif "qualifier-content" in span_class and len(homophones) > 0:
                raw_tag = clean_node(wxr, None, span_tag)
                if raw_tag != "":
                    homophones[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(homophones[-1])

    base_data.sounds.extend(homophones)
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link_node)
