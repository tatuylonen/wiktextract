import re
from typing import Any, Union

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .descendant import extract_descendants
from .etymology import extract_etymology
from .gloss import extract_gloss
from .headword_line import extract_headword_line
from .inflection import extract_inflections
from .linkage import extract_linkages
from .models import Form, Sense, WordEntry
from .note import extract_note
from .pronunciation import extract_pronunciation
from .section_titles import (
    DESCENDANTS_TITLES,
    ETYMOLOGY_TITLES,
    IGNORED_TITLES,
    INFLECTION_TITLES,
    LINKAGE_TITLES,
    NOTES_TITLES,
    POS_TITLES,
    PRONUNCIATION_TITLES,
    TRANSLATIONS_TITLES,
)
from .translation import extract_translation

# Templates that are used to form panels on pages and that
# should be ignored in various positions
PANEL_TEMPLATES = {}

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = {}

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = frozenset(
    {
        "col1",
        "col2",
        "col3",
        "col4",
        "col5",
        "col1-u",
        "col2-u",
        "col3-u",
        "col4-u",
        "col5-u",
        "check deprecated lang param usage",
        "deprecated code",
        "ru-verb-alt-ё",
        "ru-noun-alt-ё",
        "ru-adj-alt-ё",
        "ru-proper noun-alt-ё",
        "ru-pos-alt-ё",
        "ru-alt-ё",
        # langhd is needed for pre-expanding language heading templates:
        # https://zh.wiktionary.org/wiki/Template:-en-
        "langhd",
        "zh-der",  # col3 for Chinese
        "der3",  # redirects to col3
    }
)


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    node: Union[WikiNode, list[Union[WikiNode, str]]],
) -> None:
    if isinstance(node, list):
        for x in node:
            parse_section(wxr, page_data, base_data, x)
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind in LEVEL_KIND_FLAGS:
        subtitle = clean_node(wxr, None, node.largs)
        # remove number suffix from subtitle
        subtitle = re.sub(r"\s*(?:（.+）|\d+)$", "", subtitle)
        wxr.wtp.start_subsection(subtitle)
        if subtitle in IGNORED_TITLES:
            pass
        elif subtitle in POS_TITLES:
            process_pos_block(wxr, page_data, base_data, node, subtitle)
        elif wxr.config.capture_etymologies and subtitle.startswith(
            tuple(ETYMOLOGY_TITLES)
        ):
            extract_etymology(wxr, page_data, base_data, node)
        elif (
            wxr.config.capture_pronunciation
            and subtitle in PRONUNCIATION_TITLES
        ):
            extract_pronunciation(wxr, page_data, base_data, node)
        elif wxr.config.capture_linkages and subtitle in LINKAGE_TITLES:
            extract_linkages(
                wxr,
                page_data,
                node.children,
                LINKAGE_TITLES[subtitle],
                "",
            )
        elif (
            wxr.config.capture_translations and subtitle in TRANSLATIONS_TITLES
        ):
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_translation(wxr, page_data, node)
        elif wxr.config.capture_inflections and subtitle in INFLECTION_TITLES:
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_inflections(wxr, page_data, node)
        elif wxr.config.capture_descendants and subtitle in DESCENDANTS_TITLES:
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_descendants(wxr, node, page_data[-1])
        elif subtitle in NOTES_TITLES:
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_note(wxr, page_data, node)
        else:
            wxr.wtp.debug(
                f"Unhandled subtitle: {subtitle}",
                sortid="extractor/zh/page/parse_section/192",
            )

        for template in node.find_child(NodeKind.TEMPLATE):
            add_page_end_categories(wxr, page_data, template)


def process_pos_block(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    node: WikiNode,
    pos_text: str,
):
    pos_data = POS_TITLES[pos_text]
    pos_type = pos_data["pos"]
    base_data.pos = pos_type
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].tags.extend(pos_data.get("tags", []))
    for index, child in enumerate(node.filter_empty_str_child()):
        if isinstance(child, WikiNode):
            if index == 0 and isinstance(child, TemplateNode):
                extract_headword_line(
                    wxr, page_data, child, base_data.lang_code
                )
                process_soft_redirect_template(wxr, child, page_data)
            elif child.kind == NodeKind.LIST:
                extract_gloss(wxr, page_data, child, Sense())
            elif child.kind in LEVEL_KIND_FLAGS:
                parse_section(wxr, page_data, base_data, child)
        else:
            parse_section(wxr, page_data, base_data, child)
    if len(page_data[-1].senses) == 0 and not node.contain_node(NodeKind.LIST):
        # low quality pages don't put gloss in list
        gloss_text = clean_node(
            wxr, page_data[-1], list(node.invert_find_child(LEVEL_KIND_FLAGS))
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

    # skip translation pages
    if page_title.endswith(
        tuple("/" + tr_title for tr_title in TRANSLATIONS_TITLES)
    ):
        return []

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")
    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

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
        for template_node in level2_node.find_child(NodeKind.TEMPLATE):
            if template_node.template_name == "zh-forms":
                process_zh_forms(wxr, base_data, template_node)

        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)
        if not level2_node.contain_node(NodeKind.LEVEL3):
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            process_low_quality_page(wxr, level2_node, page_data)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]


def process_low_quality_page(
    wxr: WiktextractContext,
    level_node: WikiNode,
    page_data: list[WordEntry],
) -> None:
    if level_node.contain_node(NodeKind.TEMPLATE):
        for template_node in level_node.find_child(NodeKind.TEMPLATE):
            process_soft_redirect_template(wxr, template_node, page_data)
    else:
        # only have a gloss text
        gloss_text = clean_node(wxr, page_data[-1], level_node.children)
        if len(gloss_text) > 0:
            page_data[-1].senses.append(Sense(glosses=[gloss_text]))


def process_soft_redirect_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    page_data: list[WordEntry],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Ja-see
    # https://zh.wiktionary.org/wiki/Template:Zh-see
    update_pos = False
    if template_node.template_name.lower() == "zh-see":
        page_data[-1].redirects.append(
            clean_node(wxr, None, template_node.template_parameters.get(1, ""))
        )
        update_pos = True
    elif template_node.template_name.lower() == "ja-see":
        for key, value in template_node.template_parameters.items():
            if isinstance(key, int):
                page_data[-1].redirects.append(clean_node(wxr, None, value))
        update_pos = True

    if update_pos and page_data[-1].pos == "unknown":
        page_data[-1].pos = "soft-redirect"


def process_zh_forms(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://zh.wiktionary.org/wiki/Template:zh-forms
    for p_name, p_value in template_node.template_parameters.items():
        if not isinstance(p_name, str):
            continue
        if re.fullmatch(r"s\d*", p_name):
            form_data = Form(
                form=clean_node(wxr, None, p_value), tags=["Simplified Chinese"]
            )
            if len(form_data.form) > 0:
                base_data.forms.append(form_data)
        elif re.fullmatch(r"t\d+", p_name):
            form_data = Form(
                form=clean_node(wxr, None, p_value),
                tags=["Traditional Chinese"],
            )
            if len(form_data.form) > 0:
                base_data.forms.append(form_data)
        elif p_name == "alt":
            for form_text in clean_node(wxr, None, p_value).split(","):
                texts = form_text.split("-")
                form_data = Form(form=texts[0], raw_tags=texts[1:])
                if len(form_data.form) > 0:
                    base_data.forms.append(form_data)
        elif p_name == "lit":
            lit = clean_node(wxr, None, p_value)
            base_data.literal_meaning = lit


# https://zh.wiktionary.org/wiki/Template:Zh-cat
# https://zh.wiktionary.org/wiki/Template:Catlangname
CATEGORY_TEMPLATES = frozenset(["zh-cat", "cln", "catlangname"])


def add_page_end_categories(
    wxr: WiktextractContext, page_data: list[WordEntry], template: TemplateNode
) -> None:
    if template.template_name.lower() in CATEGORY_TEMPLATES:
        categories = {}
        clean_node(wxr, categories, template)
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(categories.get("categories", []))
