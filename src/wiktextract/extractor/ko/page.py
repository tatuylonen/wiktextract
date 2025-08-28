import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .linkage import extract_linkage_section
from .models import Form, Sense, WordEntry
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
