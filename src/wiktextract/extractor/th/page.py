import re
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
from .alt_form import extract_alt_form_section, extract_romanization_section
from .descendant import extract_descendant_section
from .etymology import extract_etymology_section
from .linkage import extract_linkage_section
from .models import Form, Linkage, Sense, WordEntry
from .pos import (
    extract_note_section,
    extract_pos_section,
    extract_usage_note_section,
)
from .section_titles import LINKAGE_SECTIONS, POS_DATA, TRANSLATION_SECTIONS
from .sound import extract_sound_section
from .tags import translate_raw_tags
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    title_text = title_text.rstrip(string.digits + string.whitespace)
    wxr.wtp.start_subsection(title_text)
    if title_text in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
        if len(page_data[-1].senses) == 0 and title_text in LINKAGE_SECTIONS:
            page_data.pop()
            extract_linkage_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
                LINKAGE_SECTIONS[title_text],
            )
        elif (
            len(page_data[-1].senses) == 0 and title_text == "การถอดเป็นอักษรโรมัน"
        ):
            page_data.pop()
            extract_romanization_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
    elif title_text == "รากศัพท์":
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_etymology_section(wxr, base_data, level_node)
    elif title_text in TRANSLATION_SECTIONS:
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_SECTIONS[title_text],
        )
    elif title_text == "คำสืบทอด":
        extract_descendant_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text.startswith(("การออกเสียง", "การอ่านออกเสียง", "ออกเสียง")):
        extract_sound_section(wxr, base_data, level_node)
    elif title_text == "รูปแบบอื่น":
        extract_alt_form_section(
            wxr,
            page_data[-1]
            if len(page_data) > 0
            and page_data[-1].lang_code == base_data.lang_code
            and page_data[-1].pos == base_data.pos
            else base_data,
            level_node,
        )
    elif title_text == "การใช้":
        extract_note_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text == "หมายเหตุการใช้":
        extract_usage_note_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text not in [
        "ดูเพิ่ม",  # see more
        "อ้างอิง",  # references
        "อ่านเพิ่ม",  # read more
        "อ่านเพิ่มเติม",  # read more
        "รากอักขระ",  # glyph origin
        "การผันรูป",  # conjugation
        "การผัน",  # conjugation
        "คำกริยาในรูปต่าง ๆ",  # verb forms
        "การอ่าน",  # Japanese readings
        "การผันคำกริยา",  # conjugation
        "การผันคำ",  # inflection
        "การกลายรูป",  # conjugation
        "การผันคำนาม",  # inflection
    ]:
        wxr.wtp.debug(f"Unknown title: {title_text}", sortid="th/page/106")

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    extract_category_templates(
        wxr, page_data if len(page_data) else [base_data], level_node
    )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://th.wiktionary.org/wiki/วิธีใช้:คู่มือในการเขียน

    # skip translation pages
    if page_title.endswith("/คำแปลภาษาอื่น"):
        return []
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        lang_name = lang_name.removeprefix("ภาษา")
        lang_code = name_to_code(lang_name, "th")
        if lang_code == "":
            lang_code = "unknown"
        if lang_name == "":
            lang_name = "unknown"
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        for t_node in level2_node.find_child(NodeKind.TEMPLATE):
            if t_node.template_name == "zh-forms":
                extract_zh_forms(wxr, base_data, t_node)
        for next_level_node in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]


CATEGORY_TEMPLATES = frozenset(
    [
        "zh-cat",
        "cln",
        "catlangname",
        "c",
        "topics",
        "top",
        "catlangcode",
        "topic",
    ]
)


def extract_category_templates(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
):
    categories = {}
    for node in level_node.find_child(NodeKind.TEMPLATE):
        if node.template_name.lower() in CATEGORY_TEMPLATES:
            clean_node(wxr, categories, node)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.categories.extend(categories.get("categories", []))


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
    for raw_tag in re.split(r"/|และ", row_header):
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

    if row_header == "anagram":
        for form in forms:
            base_data.anagrams.append(
                Linkage(word=form.form, raw_tags=form.raw_tags, tags=form.tags)
            )
    else:
        base_data.forms.extend(forms)
