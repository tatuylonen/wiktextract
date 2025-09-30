import string
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .linkage import extract_alt_form_section, extract_linkage_section
from .models import Form, Sense, WordEntry
from .pos import extract_note_section, extract_pos_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA, TRANSLATION_SECTIONS
from .sound import extract_homophone_section, extract_sound_section
from .tags import translate_raw_tags
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    subtitle = clean_node(wxr, None, level_node.largs)
    subtitle = subtitle.rstrip(string.digits + string.whitespace)
    if subtitle in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, subtitle)
        if len(page_data[-1].senses) == 0 and subtitle in LINKAGE_SECTIONS:
            page_data.pop()
            extract_linkage_section(
                wxr,
                page_data if len(page_data) > 0 else [base_data],
                level_node,
                LINKAGE_SECTIONS[subtitle],
            )
    elif subtitle in TRANSLATION_SECTIONS:
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif subtitle == "Cách phát âm":
        extract_sound_section(wxr, base_data, level_node)
    elif subtitle == "Từ đồng âm":
        extract_homophone_section(wxr, base_data, level_node)
    elif subtitle == "Từ nguyên":
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_etymology_section(wxr, base_data, level_node)
    elif subtitle == "Cách viết khác":
        extract_alt_form_section(wxr, base_data, page_data, level_node)
    elif subtitle in ["Ghi chú sử dụng", "Chú ý"]:
        extract_note_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif subtitle in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data if len(page_data) > 0 else [base_data],
            level_node,
            LINKAGE_SECTIONS[subtitle],
        )
    elif subtitle not in ["Tham khảo", "Cách ra dấu", "Đọc thêm", "Xem thêm"]:
        wxr.wtp.debug(f"Unknown title: {subtitle}", sortid="vi/page/22")

    extract_section_cats(wxr, base_data, page_data, level_node)
    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://vi.wiktionary.org/wiki/Wiktionary:Sơ_đồ_mục_từ

    # ignore thesaurus, rhyme, quote, reconstruct pages
    if page_title.startswith(
        ("Kho từ vựng:", "Vần:", "Kho ngữ liệu:", "Từ tái tạo:")
    ):
        return []

    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        categories = {}
        lang_name = clean_node(wxr, categories, level2_node.largs) or "unknown"
        lang_code = name_to_code(lang_name, "vi") or "unknown"
        for t_node in level2_node.find_content(NodeKind.TEMPLATE):
            if t_node.template_name == "langname":
                lang_code = clean_node(
                    wxr, None, t_node.template_parameters.get(1, "")
                )
        if (
            wxr.config.capture_language_codes is not None
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        base_data.categories = categories.get("categories", [])
        extract_section_cats(wxr, base_data, page_data, level2_node)
        for t_node in level2_node.find_child(NodeKind.TEMPLATE):
            if t_node.template_name in ["zho-forms", "zh-forms"]:
                extract_zh_forms_template(wxr, base_data, t_node)
        for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]


def extract_section_cats(
    wxr: WiktextractContext,
    base_data: WordEntry,
    page_data: list[WordEntry],
    level_node: LevelNode,
):
    cats = {}
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
        if node.kind == NodeKind.LINK:
            clean_node(wxr, cats, node)
        elif node.template_name in [
            "topics",
            "C",
            "topic",
            "catlangname",
            "cln",
        ]:
            clean_node(wxr, cats, node)

    if len(page_data) == 0 or page_data[-1].lang_code != base_data.lang_code:
        base_data.categories.extend(cats.get("categories", []))
    else:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(cats.get("categories", []))


def extract_zh_forms_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    base_data.literal_meaning = clean_node(
        wxr, None, t_node.template_parameters.get("lit", "")
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            row_header_tags = []
            header_has_span = False
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    row_header, row_header_tags, header_has_span = (
                        extract_zh_forms_header_cell(wxr, base_data, cell)
                    )
                elif not header_has_span:
                    extract_zh_forms_data_cell(
                        wxr, base_data, cell, row_header, row_header_tags
                    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link_node)


def extract_zh_forms_header_cell(
    wxr: WiktextractContext, base_data: WordEntry, header_cell: WikiNode
) -> tuple[str, list[str], bool]:
    row_header = ""
    row_header_tags = []
    header_has_span = False
    first_span_index = len(header_cell.children)
    for index, span_tag in header_cell.find_html("span", with_index=True):
        if index < first_span_index:
            first_span_index = index
        header_has_span = True
    row_header = clean_node(wxr, None, header_cell.children[:first_span_index])
    for raw_tag in row_header.split(" và "):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            row_header_tags.append(raw_tag)
    for span_tag in header_cell.find_html_recursively("span"):
        span_lang = span_tag.attrs.get("lang", "")
        form_nodes = []
        sup_title = ""
        for node in span_tag.children:
            if isinstance(node, HTMLNode) and node.tag == "sup":
                for sup_span in node.find_html("span"):
                    sup_title = sup_span.attrs.get("title", "")
            else:
                form_nodes.append(node)
        if span_lang in ["zh-Hant", "zh-Hans"]:
            for word in clean_node(wxr, None, form_nodes).split("/"):
                if word not in [base_data.word, ""]:
                    form = Form(form=word, raw_tags=row_header_tags)
                    if sup_title != "":
                        form.raw_tags.append(sup_title)
                    translate_raw_tags(form)
                    base_data.forms.append(form)
    return row_header, row_header_tags, header_has_span


def extract_zh_forms_data_cell(
    wxr: WiktextractContext,
    base_data: WordEntry,
    cell: WikiNode,
    row_header: str,
    row_header_tags: list[str],
):
    for top_span_tag in cell.find_html("span"):
        forms = []
        for span_tag in top_span_tag.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            if span_lang in ["zh-Hant", "zh-Hans", "zh"]:
                word = clean_node(wxr, None, span_tag)
                if word not in ["", "／", base_data.word]:
                    form = Form(form=word, raw_tags=row_header_tags)
                    if span_lang == "zh-Hant":
                        form.tags.append("Traditional-Chinese")
                    elif span_lang == "zh-Hans":
                        form.tags.append("Simplified-Chinese")
                    translate_raw_tags(form)
                    forms.append(form)
            elif "font-size:80%" in span_tag.attrs.get("style", ""):
                raw_tag = clean_node(wxr, None, span_tag)
                if raw_tag != "":
                    for form in forms:
                        form.raw_tags.append(raw_tag)
                        translate_raw_tags(form)
        base_data.forms.extend(forms)
