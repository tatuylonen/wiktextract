import re
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
from .linkage import extract_linkage_section
from .models import Form, Linkage, Sense, WordEntry
from .pos import extract_grammar_note_section, extract_pos_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .sound import (
    SOUND_TEMPLATES,
    extract_sound_section,
    extract_sound_template,
)
from .tags import translate_raw_tags
from .translation import extract_translation_section


def extract_section_categories(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, link_node
        )
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in ["C", "topics"]:
            clean_node(
                wxr, page_data[-1] if len(page_data) > 0 else base_data, t_node
            )


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    title_text = re.sub(r"\s*\d+$", "", title_text).strip("() ")
    if "(" in title_text:
        title_text = title_text[: title_text.index("(")]
    if title_text.removeprefix("보조 ").strip() in POS_DATA:
        orig_page_data_len = len(page_data)
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
        if (
            len(page_data) == orig_page_data_len
            and title_text in LINKAGE_SECTIONS
            and len(page_data) > 0
        ):  # try extract as linkage section
            extract_linkage_section(
                wxr, page_data[-1], level_node, LINKAGE_SECTIONS[title_text]
            )
    elif title_text in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_SECTIONS[title_text],
        )
    elif title_text == "번역":
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text == "발음":
        extract_sound_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text == "어원":
        extract_etymology_section(
            wxr,
            page_data[-1]
            if len(page_data) > 0 and len(page_data[-1].etymology_texts) == 0
            else base_data,
            level_node,
        )
    elif title_text == "어법 주의 사항":
        extract_grammar_note_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
        )
    elif title_text in ["다른 표기", "표기"]:
        extract_alt_form_section(wxr, base_data, level_node)
    elif title_text in [
        "참고 문헌",
        "독음",
        "자원",
        "교차언어",
        "관사를 입력하세요",
        "각주",
        "갤러리",
        "참조",
        "이체자",
        "외부 링크",
    ]:
        pass  # ignore
    else:
        wxr.wtp.debug(f"unknown title: {title_text}", sortid="ko/page/63")

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    extract_section_categories(wxr, page_data, base_data, level_node)


def parse_language_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level2_node: LevelNode
) -> None:
    pre_data_len = len(page_data)
    lang_name = clean_node(wxr, None, level2_node.largs)
    if lang_name == "":
        lang_name = "unknown"
    lang_code = name_to_code(lang_name, "ko")
    if lang_code == "":
        lang_code = "unknown"
    if (
        wxr.config.capture_language_codes is not None
        and lang_code not in wxr.config.capture_language_codes
    ):
        return
    wxr.wtp.start_section(lang_name)
    base_data = WordEntry(
        word=wxr.wtp.title,
        lang_code=lang_code,
        lang=lang_name,
        pos="unknown",
    )
    extract_section_categories(wxr, page_data, base_data, level2_node)
    for t_node in level2_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in SOUND_TEMPLATES:
            extract_sound_template(wxr, base_data, t_node)
        elif t_node.template_name == "zh-see":
            base_data.redirects.append(
                clean_node(wxr, None, t_node.template_parameters.get(1, ""))
            )
            clean_node(wxr, base_data, t_node)
        elif t_node.template_name in ["ja-see", "ja-see-kango"]:
            extract_ja_see_template(wxr, base_data, t_node)
        elif t_node.template_name == "zh-forms":
            extract_zh_forms(wxr, base_data, t_node)
    if len(base_data.redirects) > 0:
        page_data.append(base_data)
    for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    # no POS section
    if len(page_data) == pre_data_len:
        extract_pos_section(wxr, page_data, base_data, level2_node, "")


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://ko.wiktionary.org/wiki/위키낱말사전:문서_양식
    # https://ko.wiktionary.org/wiki/위키낱말사전:한국어_편집부
    if page_title.startswith(("Appendix:", "T195546/NS111")):
        return []
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        parse_language_section(wxr, page_data, level2_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]


def extract_alt_form_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name in ["alt", "alter"]:
            extract_alt_template(wxr, base_data, t_node)


def extract_alt_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    forms = []
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "").split()
        if span_lang == lang_code:
            word = clean_node(wxr, None, span_tag)
            if word != "":
                forms.append(Form(form=word))
        elif span_lang.endswith("-Latn") and len(forms) > 0:
            forms[-1].roman = clean_node(wxr, None, span_tag)
        elif "label-content" in span_class and len(forms) > 0:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                for form in forms:
                    form.raw_tags.append(raw_tag)
                    translate_raw_tags(form)
    base_data.forms.extend(forms)


def extract_ja_see_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    for key, value in t_node.template_parameters.items():
        if isinstance(key, int):
            base_data.redirects.append(clean_node(wxr, None, value))
    clean_node(wxr, base_data, t_node)


def extract_zh_forms(
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
    for raw_tag in re.split(r"/| 및 ", row_header):
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
    forms = []
    for top_span_tag in cell.find_html("span"):
        span_style = top_span_tag.attrs.get("style", "")
        span_lang = top_span_tag.attrs.get("lang", "")
        if span_style == "white-space:nowrap;":
            extract_zh_forms_data_cell(
                wxr, base_data, top_span_tag, row_header, row_header_tags
            )
        elif "font-size:80%" in span_style:
            raw_tag = clean_node(wxr, None, top_span_tag)
            if raw_tag != "":
                for form in forms:
                    form.raw_tags.append(raw_tag)
                    translate_raw_tags(form)
        elif span_lang in ["zh-Hant", "zh-Hans", "zh"]:
            word = clean_node(wxr, None, top_span_tag)
            if word not in ["", "／", base_data.word]:
                form = Form(form=word)
                if row_header != "anagram":
                    form.raw_tags = row_header_tags
                if span_lang == "zh-Hant":
                    form.tags.append("Traditional-Chinese")
                elif span_lang == "zh-Hans":
                    form.tags.append("Simplified-Chinese")
                translate_raw_tags(form)
                forms.append(form)

    if row_header == "어구전철":
        for form in forms:
            base_data.anagrams.append(
                Linkage(word=form.form, raw_tags=form.raw_tags, tags=form.tags)
            )
    else:
        base_data.forms.extend(forms)
