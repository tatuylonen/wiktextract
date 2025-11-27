from itertools import count

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
    source: str = "",
    sense: str = "",
) -> None:
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "col"
        ):
            extract_col_template(
                wxr, word_entry, node, linkage_type, source, sense
            )
        elif isinstance(node, TemplateNode) and node.template_name == "ws":
            extract_ws_template(
                wxr, word_entry, node, linkage_type, source, sense
            )
        elif isinstance(node, TemplateNode) and node.template_name == "zh-dial":
            extract_zh_dial_template(wxr, word_entry, node, linkage_type, sense)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_linkage_list_item(
                    wxr, word_entry, list_item, linkage_type, source, sense
                )


def extract_col_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    source: str,
    sense: str,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for li_tag in expanded_node.find_html_recursively("li"):
        l_data = []
        for span_tag in li_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            if "Latn" in span_class:
                for data in l_data:
                    data.roman = clean_node(wxr, None, span_tag)
            elif "lang" in span_tag.attrs:
                word = clean_node(wxr, None, span_tag)
                if word != "":
                    l_data.append(
                        Linkage(word=word, source=source, sense=sense)
                    )
                    if span_class == "Hant":
                        l_data[-1].tags.append("Traditional-Chinese")
                    elif span_class == "Hans":
                        l_data[-1].tags.append("Simplified-Chinese")
        getattr(word_entry, linkage_type).extend(l_data)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    source: str,
    sense: str,
) -> None:
    linkages = []
    raw_tags = []

    for index, node in enumerate(list_item.children):
        if isinstance(node, TemplateNode) and node.template_name == "l":
            l_data = Linkage(
                word=clean_node(wxr, None, node.template_parameters.get(2, "")),
                source=source,
                sense=sense,
                raw_tags=raw_tags,
            )
            if l_data.word != "":
                translate_raw_tags(l_data)
                linkages.append(l_data)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            for link_node in node.find_child(NodeKind.LINK):
                link_str = clean_node(wxr, None, link_node)
                if link_str.startswith("อรรถาภิธาน:") and not source.startswith(
                    "อรรถาภิธาน:"
                ):
                    extract_thesaurus_page(
                        wxr, word_entry, linkage_type, link_str, sense
                    )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            link_str = clean_node(wxr, None, node)
            if link_str != "":
                l_data = Linkage(word=link_str, sense=sense, raw_tags=raw_tags)
                translate_raw_tags(l_data)
                linkages.append(l_data)
        elif isinstance(node, str) and ("-" in node or "–" in node):
            if "-" in node:
                sense = node[node.index("-") + 1 :]
            elif "–" in node:
                sense = node[node.index("–") + 1 :]
            sense = clean_node(
                wxr,
                None,
                [sense] + list_item.children[index + 1 :],
            ).strip()
            for l_data in linkages:
                l_data.sense = sense
            break
        elif isinstance(node, TemplateNode) and node.template_name in [
            "qualifier",
            "q",
            "qual",
            "qf",
        ]:
            text = clean_node(wxr, None, node).strip("() ")
            for raw_tag in text.split(","):
                raw_tag = raw_tag.strip()
                if raw_tag != "":
                    raw_tags.append(raw_tag)
        elif isinstance(node, TemplateNode) and node.template_name == "zh-l":
            linkages.extend(extract_zh_l_template(wxr, node, sense, raw_tags))

    getattr(word_entry, linkage_type).extend(linkages)


def extract_thesaurus_page(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    page_title: str,
    sense: str,
) -> None:
    page = wxr.wtp.get_page(page_title, 110)
    if page is None or page.body is None:
        return
    root = wxr.wtp.parse(page.body)
    for level2_node in root.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs).removeprefix(
            "ภาษา"
        )
        if lang_name != word_entry.lang:
            continue
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            pos_title = clean_node(wxr, None, level3_node.largs)
            if pos_title != word_entry.pos_title:
                continue
            for linkage_level_node in level3_node.find_child_recursively(
                LEVEL_KIND_FLAGS
            ):
                linkage_title = clean_node(wxr, None, linkage_level_node.largs)
                if LINKAGE_SECTIONS.get(linkage_title) != linkage_type:
                    continue
                extract_linkage_section(
                    wxr,
                    word_entry,
                    linkage_level_node,
                    linkage_type,
                    source=page_title,
                    sense=sense,
                )


def extract_ws_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    source: str,
    sense: str,
) -> None:
    word = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if word != "":
        l_data = Linkage(word=word, source=source, sense=sense)
        getattr(word_entry, linkage_type).append(l_data)


LINKAGE_TEMPLATES = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "synsee": "synonyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
    "cot": "coordinate_terms",
    "coordinate terms": "coordinate_terms",
    "hyper": "hypernyms",
    "hypernyms": "hypernyms",
    "hypo": "hyponyms",
    "hyponyms": "hyponyms",
}


def extract_syn_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    sense = " ".join(word_entry.senses[-1].glosses)
    for arg_name in count(2):
        if arg_name not in t_node.template_parameters:
            break
        arg_value = clean_node(wxr, None, t_node.template_parameters[arg_name])
        if arg_value.startswith(("อรรถาภิธาน:", "Thesaurus:")):
            extract_thesaurus_page(
                wxr, word_entry, linkage_type, arg_value, sense
            )
        elif arg_value != "":
            getattr(word_entry, linkage_type).append(
                Linkage(word=arg_value, sense=sense)
            )


def extract_zh_dial_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    sense: str,
):
    from .sound import split_zh_pron_raw_tag

    linkage_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table_node in expanded_node.find_child_recursively(NodeKind.TABLE):
        is_note_row = False
        note_tags = {}
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            for cell_node in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    is_note_row = clean_node(wxr, None, cell_node) == "หมายเหตุ"
                elif is_note_row:
                    for note_str in clean_node(wxr, None, cell_node).split(";"):
                        if "-" in note_str:
                            note_symbol, note = note_str.split("-", maxsplit=1)
                            note_symbol = note_symbol.strip()
                            note = note.strip()
                            if note_symbol != "" and note != "":
                                note_tags[note_symbol] = note
        lang_tags = []
        region_tags = []
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            if not row_node.contain_node(NodeKind.TABLE_CELL):
                continue  # skip header row
            for header_node in row_node.find_child(NodeKind.TABLE_HEADER_CELL):
                lang_tags = split_zh_pron_raw_tag(
                    clean_node(wxr, None, header_node)
                )
            if lang_tags == ["หมายเหตุ"]:  # skip last note row
                continue
            for cell_node in row_node.find_child(NodeKind.TABLE_CELL):
                for link_node in cell_node.find_child(NodeKind.LINK):
                    region_tags = split_zh_pron_raw_tag(
                        clean_node(wxr, None, link_node)
                    )
                for span_tag in cell_node.find_html("span"):
                    span_text = clean_node(wxr, None, span_tag)
                    if span_text == "":
                        continue
                    if (
                        span_tag.attrs.get("lang", "") == "zh"
                        and span_text != wxr.wtp.title
                    ):
                        l_data = Linkage(word=span_text, sense=sense)
                        if len(lang_tags) > 0:
                            l_data.raw_tags.extend(lang_tags)
                        if len(region_tags) > 0:
                            l_data.raw_tags.extend(region_tags)
                        translate_raw_tags(l_data)
                        linkage_list.append(l_data)
                    elif (
                        span_tag.attrs.get("style", "") == "font-size:60%"
                        and len(linkage_list) > 0
                    ):
                        for note_symbol in span_text.split(","):
                            note_symbol = note_symbol.strip()
                            raw_tag = note_symbol
                            if note_symbol in note_tags:
                                raw_tag = note_tags[note_symbol]
                            if raw_tag != "":
                                linkage_list[-1].raw_tags.append(raw_tag)
                                translate_raw_tags(linkage_list[-1])

    getattr(word_entry, linkage_type).extend(linkage_list)


def extract_zh_l_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: str,
    raw_tags: list[str],
) -> list[Linkage]:
    l_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    roman = ""
    new_sense = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if new_sense != "":
        sense = new_sense
    for i_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="Latn"
    ):
        roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value="zh"
    ):
        linkage_data = Linkage(
            sense=sense,
            raw_tags=raw_tags,
            roman=roman,
            word=clean_node(wxr, None, span_tag),
        )
        lang_attr = span_tag.attrs.get("lang", "")
        if lang_attr == "zh-Hant":
            linkage_data.tags.append("Traditional-Chinese")
        elif lang_attr == "zh-Hans":
            linkage_data.tags.append("Simplified-Chinese")
        if linkage_data.word not in ["／", ""]:
            translate_raw_tags(linkage_data)
            l_list.append(linkage_data)

    return l_list
