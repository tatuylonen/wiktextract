import itertools
import re
from dataclasses import dataclass

from wikitextprocessor import (
    HTMLNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import set_sound_file_url_fields
from .models import Sound, WordEntry
from .tags import translate_raw_tags


def extract_pronunciation_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: WikiNode
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "zh-forms":
            from .page import process_zh_forms

            process_zh_forms(wxr, base_data, t_node)
        else:
            new_sounds, new_cats = process_pron_template(wxr, t_node)
            base_data.sounds.extend(new_sounds)
            base_data.categories.extend(new_cats)
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        new_sounds, new_cats = process_pron_item_list_item(wxr, list_item_node)
        base_data.sounds.extend(new_sounds)
        base_data.categories.extend(new_cats)


def process_pron_item_list_item(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> tuple[list[Sound], list[str]]:
    raw_tags = []
    sounds = []
    categories = []
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        new_sounds, new_cats = process_pron_template(
            wxr, template_node, raw_tags
        )
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    return sounds, categories


def process_pron_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str] = [],
) -> tuple[list[Sound], list[str]]:
    template_name = template_node.template_name.lower()
    sounds = []
    categories = []
    if template_name == "zh-pron":
        new_sounds, new_cats = process_zh_pron_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    elif template_name in ["rhymes", "rhyme"]:
        new_sounds, new_cats = extract_rhymes_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    elif template_name in ["homophones", "homophone", "hmp"]:
        new_sounds, new_cats = extract_homophones_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    elif template_name in ["a", "accent"]:
        # https://zh.wiktionary.org/wiki/Template:Accent
        raw_tags.append(clean_node(wxr, None, template_node).strip("()"))
    elif template_name in ["audio", "音"]:
        sounds.extend(process_audio_template(wxr, template_node, raw_tags))
    elif template_name == "ipa":
        sounds.extend(process_ipa_template(wxr, template_node, raw_tags))
    elif template_name == "enpr":
        sounds.extend(process_enpr_template(wxr, template_node, raw_tags))
    elif template_name == "ja-pron":
        new_sounds, new_cats = extract_ja_pron_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    elif template_name == "th-pron":
        new_sounds, new_cats = extract_th_pron_template(wxr, template_node)
        sounds.extend(new_sounds)
        categories.extend(new_cats)
    return sounds, categories


def process_zh_pron_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    # https://zh.wiktionary.org/wiki/Template:Zh-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    seen_lists = set()
    sounds = []
    categories = {}
    for list_node in expanded_node.find_child_recursively(NodeKind.LIST):
        if list_node not in seen_lists:
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                sounds.extend(
                    process_zh_pron_list_item(wxr, list_item, [], seen_lists)
                )
    clean_node(wxr, categories, expanded_node)
    for sound in sounds:
        translate_raw_tags(sound)
    return sounds, categories.get("categories", [])


def process_zh_pron_list_item(
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
                if link_str.startswith("File:"):
                    filename = link_str.removeprefix("File:")
                    sound_data = Sound(raw_tags=current_tags)
                    set_sound_file_url_fields(wxr, filename, sound_data)
                    sounds.append(sound_data)
                elif node_str != "":
                    current_tags.append(node_str.strip("()"))
            elif isinstance(node, HTMLNode):
                if node.tag == "small":
                    # remove "幫助"(help) <sup> tag
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
                        ).rstrip("：")
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
                    and current_tags[-1] == "同音詞"
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
                        process_zh_pron_list_item(
                            wxr,
                            next_list_item,
                            current_tags,
                            seen_lists,
                        )
                    )
    return sounds


def split_zh_pron_raw_tag(raw_tag_text: str) -> list[str]:
    raw_tags = []
    if "(" not in raw_tag_text and "（" not in raw_tag_text:
        for raw_tag in re.split(r",|，|：|、|;|；|和(?!$)", raw_tag_text):
            raw_tag = raw_tag.strip().removeprefix("包括").strip()
            if raw_tag != "":
                raw_tags.append(raw_tag)
    else:
        processed_offsets = []
        for match in re.finditer(r"\([^()]+\)|（[^（）]+）", raw_tag_text):
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
        elif isinstance(node, str) and node.strip() == "[實際讀音：":
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
                raw_tags=raw_tags + ["實際讀音"],
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
        elif c in ["(", "（"]:
            parentheses += 1
            pron += c
        elif c in [")", "）"]:
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


def extract_homophones_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    # https://zh.wiktionary.org/wiki/Template:homophones
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    homophones = []
    cats = {}
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for top_span in expanded_node.find_html(
        "span", attr_name="class", attr_value="homophones"
    ):
        for span_tag in top_span.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            span_class = span_tag.attrs.get("class", "").split()
            if "Latn" in span_class and len(homophones) > 0:
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
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, cats, link_node)
    return homophones, cats.get("categories", [])


def process_audio_template(
    wxr: WiktextractContext, template_node: TemplateNode, raw_tags: list[str]
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:Audio
    sound_file = clean_node(
        wxr, None, template_node.template_parameters.get(2, "")
    )
    sound_data = Sound()
    set_sound_file_url_fields(wxr, sound_file, sound_data)
    raw_tag = clean_node(
        wxr, None, template_node.template_parameters.get(3, "")
    )
    if len(raw_tag) > 0:
        sound_data.raw_tags.append(raw_tag)
    sound_data.raw_tags.extend(raw_tags)
    return [sound_data]


def process_ipa_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:IPA
    sounds = []
    for index in itertools.count(2):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            ipa=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        sounds.append(sound)
    return sounds


def process_enpr_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    raw_tags: list[str],
) -> list[Sound]:
    # https://zh.wiktionary.org/wiki/Template:enPR
    sounds = []
    for index in range(1, 4):
        if index not in template_node.template_parameters:
            break
        sound = Sound(
            enpr=clean_node(
                wxr, None, template_node.template_parameters.get(index)
            ),
            raw_tags=raw_tags,
        )
        sounds.append(sound)
    return sounds


def extract_ja_pron_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    cats = {}
    sounds = []
    for li_tag in expanded_node.find_html_recursively("li"):
        sound = Sound()
        for span_tag in li_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            if "usage-label-accent" in span_class:
                raw_tag = clean_node(wxr, None, span_tag).strip("() ")
                if raw_tag != "":
                    sound.raw_tags.append(raw_tag)
            elif "IPA" in span_class:
                sound.ipa = clean_node(wxr, None, span_tag)
            elif "Latn" in span_class:
                sound.roman = clean_node(wxr, None, span_tag)
            elif span_tag.attrs.get("lang", "") == "ja":
                sound.other = clean_node(wxr, None, span_tag)
        if sound.ipa != "" or sound.other != "":
            translate_raw_tags(sound)
            sounds.append(sound)

    clean_node(wxr, cats, expanded_node)
    return sounds, cats.get("categories", [])


def extract_th_pron_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    @dataclass
    class TableHeader:
        raw_tags: list[str]
        rowspan: int

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    cats = {}
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
                if header_str.startswith("(標準泰語) IPA"):
                    field = "ipa"
                elif header_str.startswith("同音詞"):
                    field = "homophone"
                elif header_str == "音頻":
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

    clean_node(wxr, cats, expanded_node)
    return sounds, cats.get("categories", [])


def extract_rhymes_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Sound], list[str]]:
    sounds = []
    cats = {}
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        rhyme = clean_node(wxr, cats, link_node)
        if rhyme != "":
            sounds.append(Sound(rhymes=rhyme))
    return sounds, cats.get("categories", [])
