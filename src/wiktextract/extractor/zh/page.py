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
from ...wxr_logging import logger
from .descendant import extract_descendant_section
from .etymology import extract_etymology_section, extract_ja_kanjitab_template
from .gloss import extract_gloss
from .headword_line import extract_pos_head_line_nodes
from .inflection import extract_inflections
from .linkage import extract_linkage_section
from .models import Form, Linkage, Sense, WordEntry
from .note import extract_note_section
from .pronunciation import extract_pronunciation_section
from .section_titles import (
    DESCENDANTS_TITLES,
    ETYMOLOGY_TITLES,
    IGNORED_TITLES,
    INFLECTION_TITLES,
    LINKAGE_TITLES,
    POS_TITLES,
    PRONUNCIATION_TITLES,
    TRANSLATIONS_TITLES,
    USAGE_NOTE_TITLES,
)
from .tags import translate_raw_tags
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    subtitle = clean_node(wxr, None, level_node.largs)
    # remove number suffix from subtitle
    subtitle = re.sub(r"\s*(?:（.+）|\d+)$", "", subtitle)
    wxr.wtp.start_subsection(subtitle)
    if subtitle in IGNORED_TITLES:
        pass
    elif subtitle in POS_TITLES:
        process_pos_block(wxr, page_data, base_data, level_node, subtitle)
        if len(page_data[-1].senses) == 0 and subtitle in LINKAGE_TITLES:
            page_data.pop()
            extract_linkage_section(
                wxr,
                page_data if len(page_data) > 0 else [base_data],
                level_node,
                LINKAGE_TITLES[subtitle],
            )
    elif wxr.config.capture_etymologies and subtitle.startswith(
        tuple(ETYMOLOGY_TITLES)
    ):
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_etymology_section(wxr, page_data, base_data, level_node)
    elif wxr.config.capture_pronunciation and subtitle in PRONUNCIATION_TITLES:
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_pronunciation_section(wxr, base_data, level_node)
    elif wxr.config.capture_linkages and subtitle in LINKAGE_TITLES:
        is_descendant_section = False
        if subtitle in DESCENDANTS_TITLES:
            for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
                if t_node.template_name.lower() in [
                    "desc",
                    "descendant",
                    "desctree",
                    "descendants tree",
                    "cjkv",
                ]:
                    is_descendant_section = True
                    break
        if is_descendant_section and wxr.config.capture_descendants:
            extract_descendant_section(
                wxr,
                level_node,
                page_data if len(page_data) > 0 else [base_data],
            )
        elif not is_descendant_section:
            extract_linkage_section(
                wxr,
                page_data if len(page_data) > 0 else [base_data],
                level_node,
                LINKAGE_TITLES[subtitle],
            )
    elif wxr.config.capture_translations and subtitle in TRANSLATIONS_TITLES:
        if len(page_data) == 0:
            page_data.append(base_data.model_copy(deep=True))
        extract_translation_section(wxr, page_data[-1], level_node)
    elif wxr.config.capture_inflections and subtitle in INFLECTION_TITLES:
        extract_inflections(
            wxr, page_data if len(page_data) > 0 else [base_data], level_node
        )
    elif wxr.config.capture_descendants and subtitle in DESCENDANTS_TITLES:
        extract_descendant_section(
            wxr, level_node, page_data if len(page_data) > 0 else [base_data]
        )
    elif subtitle in USAGE_NOTE_TITLES:
        extract_note_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    else:
        wxr.wtp.debug(
            f"Unhandled subtitle: {subtitle}",
            sortid="extractor/zh/page/parse_section/192",
        )

    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)

    for template in level_node.find_child(NodeKind.TEMPLATE):
        add_page_end_categories(
            wxr, page_data if len(page_data) else [base_data], template
        )


def process_pos_block(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
):
    pos_data = POS_TITLES[pos_title]
    pos_type = pos_data["pos"]
    base_data.pos = pos_type
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    page_data[-1].pos_level = level_node.kind
    page_data[-1].tags.extend(pos_data.get("tags", []))
    first_gloss_list_index = len(level_node.children)
    for index, child in enumerate(level_node.children):
        if (
            isinstance(child, WikiNode)
            and child.kind == NodeKind.LIST
            and child.sarg.startswith("#")
        ):
            if index < first_gloss_list_index:
                first_gloss_list_index = index
            extract_gloss(wxr, page_data, child, Sense())

    extract_pos_head_line_nodes(
        wxr, page_data[-1], level_node.children[:first_gloss_list_index]
    )

    if len(page_data[-1].senses) == 0 and not level_node.contain_node(
        NodeKind.LIST
    ):
        # low quality pages don't put gloss in list
        expanded_node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                list(
                    level_node.invert_find_child(
                        LEVEL_KIND_FLAGS, include_empty_str=True
                    )
                )
            ),
            expand_all=True,
        )
        if not expanded_node.contain_node(NodeKind.LIST):
            gloss_text = clean_node(
                wxr,
                page_data[-1],
                expanded_node,
            )
            if len(gloss_text) > 0:
                page_data[-1].senses.append(Sense(glosses=[gloss_text]))
            else:
                page_data[-1].senses.append(Sense(tags=["no-gloss"]))


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout documents
    # https://zh.wiktionary.org/wiki/Wiktionary:佈局解釋
    # https://zh.wiktionary.org/wiki/Wiktionary:体例说明
    # https://zh.wiktionary.org/wiki/Wiktionary:格式手冊

    # skip translation pages
    if page_title.endswith(
        tuple("/" + tr_title for tr_title in TRANSLATIONS_TITLES) + ("/衍生詞",)
    ):
        return []

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")
    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(page_text, pre_expand=True)

    page_data = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        categories = {}
        lang_name = clean_node(wxr, categories, level2_node.largs)
        lang_code = name_to_code(lang_name, "zh")
        if lang_code == "":
            wxr.wtp.warning(
                f"Unrecognized language name: {lang_name}",
                sortid="extractor/zh/page/parse_page/509",
            )
            lang_code = "unknown"
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
        for t_node in level2_node.find_child(NodeKind.TEMPLATE):
            if t_node.template_name == "zh-forms":
                process_zh_forms(wxr, base_data, t_node)
            elif (
                t_node.template_name.endswith("-kanjitab")
                or t_node.template_name == "ja-kt"
            ):
                extract_ja_kanjitab_template(wxr, t_node, base_data)

        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)
        if not level2_node.contain_node(NodeKind.LEVEL3):
            page_data.append(base_data.model_copy(deep=True))
            process_low_quality_page(wxr, level2_node, page_data[-1])
            if page_data[-1] == base_data:
                page_data.pop()

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]


def process_low_quality_page(
    wxr: WiktextractContext, level_node: WikiNode, word_entry: WordEntry
) -> None:
    is_soft_redirect = False
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in ("ja-see", "ja-see-kango", "zh-see"):
            process_soft_redirect_template(wxr, template_node, word_entry)
            is_soft_redirect = True

    if not is_soft_redirect:  # only have a gloss text
        has_gloss_list = False
        for list_node in level_node.find_child(NodeKind.LIST):
            if list_node.sarg == "#":
                extract_gloss(wxr, [word_entry], list_node, Sense())
                has_gloss_list = True
        if not has_gloss_list:
            gloss_text = clean_node(wxr, word_entry, level_node.children)
            if len(gloss_text) > 0:
                for cat in word_entry.categories:
                    cat = cat.removeprefix(word_entry.lang).strip()
                    if cat in POS_TITLES:
                        pos_data = POS_TITLES[cat]
                        word_entry.pos = pos_data["pos"]
                        word_entry.tags.extend(pos_data.get("tags", []))
                        break
                word_entry.senses.append(Sense(glosses=[gloss_text]))


def process_soft_redirect_template(
    wxr: WiktextractContext, t_node: TemplateNode, word_entry: WordEntry
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Ja-see
    # https://zh.wiktionary.org/wiki/Template:Ja-see-kango
    # https://zh.wiktionary.org/wiki/Template:Zh-see
    template_name = t_node.template_name.lower()
    if template_name == "zh-see":
        word_entry.redirects.append(
            clean_node(wxr, None, t_node.template_parameters.get(1, ""))
        )
    elif template_name in ("ja-see", "ja-see-kango"):
        for key, value in t_node.template_parameters.items():
            if isinstance(key, int):
                word_entry.redirects.append(clean_node(wxr, None, value))

    if word_entry.pos == "unknown":
        word_entry.pos = "soft-redirect"


def process_zh_forms(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
):
    # https://zh.wiktionary.org/wiki/Template:zh-forms
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
    for raw_tag in re.split(r"/|與", row_header):
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
                if row_header != "異序詞":
                    form.raw_tags = row_header_tags
                if span_lang == "zh-Hant":
                    form.tags.append("Traditional-Chinese")
                elif span_lang == "zh-Hans":
                    form.tags.append("Simplified-Chinese")
                translate_raw_tags(form)
                forms.append(form)

    if row_header == "異序詞":
        for form in forms:
            base_data.anagrams.append(
                Linkage(word=form.form, raw_tags=form.raw_tags, tags=form.tags)
            )
    else:
        base_data.forms.extend(forms)


# https://zh.wiktionary.org/wiki/Template:Zh-cat
# https://zh.wiktionary.org/wiki/Template:Catlangname
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


def add_page_end_categories(
    wxr: WiktextractContext, page_data: list[WordEntry], template: TemplateNode
) -> None:
    if template.template_name.lower() in CATEGORY_TEMPLATES:
        categories = {}
        clean_node(wxr, categories, template)
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(categories.get("categories", []))
