import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .descendant import extract_descendant_section
from .etymology import extract_etymology_section
from .gloss import extract_gloss
from .headword_line import extract_pos_head_line_nodes
from .inflection import extract_inflections
from .linkage import extract_linkage_section
from .models import Form, Sense, WordEntry
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
)
from .translation import extract_translation


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
        extract_etymology_section(wxr, base_data, level_node)
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
        extract_translation(wxr, page_data, level_node)
    elif wxr.config.capture_inflections and subtitle in INFLECTION_TITLES:
        extract_inflections(
            wxr, page_data if len(page_data) > 0 else [base_data], level_node
        )
    elif wxr.config.capture_descendants and subtitle in DESCENDANTS_TITLES:
        extract_descendant_section(
            wxr, level_node, page_data if len(page_data) > 0 else [base_data]
        )
    elif subtitle in ["使用說明", "用法說明"]:
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
        add_page_end_categories(wxr, page_data, template)


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
                list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
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
        tuple("/" + tr_title for tr_title in TRANSLATIONS_TITLES)
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
        for template_node in level2_node.find_child(NodeKind.TEMPLATE):
            if template_node.template_name == "zh-forms":
                process_zh_forms(wxr, base_data, template_node)

        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)
        if not level2_node.contain_node(NodeKind.LEVEL3):
            page_data.append(base_data.model_copy(deep=True))
            process_low_quality_page(wxr, level2_node, page_data)
            if page_data[-1] == base_data:
                page_data.pop()

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]


def process_low_quality_page(
    wxr: WiktextractContext,
    level_node: WikiNode,
    page_data: list[WordEntry],
) -> None:
    is_soft_redirect = False
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in ("ja-see", "ja-see-kango", "zh-see"):
            process_soft_redirect_template(wxr, template_node, page_data)
            is_soft_redirect = True

    if not is_soft_redirect:  # only have a gloss text
        gloss_text = clean_node(wxr, page_data[-1], level_node.children)
        if len(gloss_text) > 0:
            for cat in page_data[-1].categories:
                cat = cat.removeprefix(page_data[-1].lang).strip()
                if cat in POS_TITLES:
                    pos_data = POS_TITLES[cat]
                    page_data[-1].pos = pos_data["pos"]
                    page_data[-1].tags.extend(pos_data.get("tags", []))
                    break
            page_data[-1].senses.append(Sense(glosses=[gloss_text]))


def process_soft_redirect_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    page_data: list[WordEntry],
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Ja-see
    # https://zh.wiktionary.org/wiki/Template:Ja-see-kango
    # https://zh.wiktionary.org/wiki/Template:Zh-see
    template_name = template_node.template_name.lower()
    if template_name == "zh-see":
        page_data[-1].redirects.append(
            clean_node(wxr, None, template_node.template_parameters.get(1, ""))
        )
    elif template_name in ("ja-see", "ja-see-kango"):
        for key, value in template_node.template_parameters.items():
            if isinstance(key, int):
                page_data[-1].redirects.append(clean_node(wxr, None, value))

    if page_data[-1].pos == "unknown":
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
CATEGORY_TEMPLATES = frozenset(["zh-cat", "cln", "catlangname", "c", "topics"])


def add_page_end_categories(
    wxr: WiktextractContext, page_data: list[WordEntry], template: TemplateNode
) -> None:
    if template.template_name.lower() in CATEGORY_TEMPLATES:
        categories = {}
        clean_node(wxr, categories, template)
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(categories.get("categories", []))
