from typing import Any, Optional

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .etymology import EtymologyData, extract_etymology, insert_etymology_data
from .form_line import extract_form_line
from .gloss import extract_gloss, process_exemple_template
from .inflection import extract_inflection
from .linkage import extract_linkage
from .models import Sense, WordEntry
from .note import extract_note
from .pronunciation import extract_pronunciation
from .section_types import (
    ETYMOLOGY_SECTIONS,
    IGNORED_SECTIONS,
    INFLECTION_SECTIONS,
    LINKAGE_SECTIONS,
    NOTES_SECTIONS,
    POS_SECTIONS,
    PRONUNCIATION_SECTIONS,
    TRANSLATION_SECTIONS,
)
from .translation import extract_translation

# Templates that are used to form panels on pages and that
# should be ignored in various positions
PANEL_TEMPLATES = set()

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = set()

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = set()


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> Optional[EtymologyData]:
    # Page structure: https://fr.wiktionary.org/wiki/Wiktionnaire:Structure_des_pages
    for level_node_template in level_node.find_content(NodeKind.TEMPLATE):
        if level_node_template.template_name == "S":
            # French Wiktionary uses a `S` template for all subtitles, we could
            # find the subtitle type by only checking the template parameter.
            # https://fr.wiktionary.org/wiki/Modèle:S
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections
            first_param = level_node_template.template_parameters.get(1, "")
            if not isinstance(first_param, str):
                continue
            section_type = first_param.strip().lower()
            title_categories = {}
            subtitle = clean_node(wxr, title_categories, level_node.largs)
            wxr.wtp.start_subsection(subtitle)
            if section_type in IGNORED_SECTIONS:
                for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
                    parse_section(wxr, page_data, base_data, next_level_node)
            # POS parameters:
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections_de_types_de_mots
            elif section_type in POS_SECTIONS:
                process_pos_block(
                    wxr,
                    page_data,
                    base_data,
                    level_node,
                    section_type,
                    subtitle,
                )
                if len(page_data) > 0:
                    page_data[-1].categories.extend(
                        title_categories.get("categories", [])
                    )
            elif (
                wxr.config.capture_etymologies
                and section_type in ETYMOLOGY_SECTIONS
            ):
                etymology_data = extract_etymology(wxr, level_node, base_data)
                for node in level_node.find_child(LEVEL_KIND_FLAGS):
                    parse_section(wxr, page_data, base_data, node)
                return etymology_data
            elif (
                wxr.config.capture_pronunciation
                and section_type in PRONUNCIATION_SECTIONS
            ):
                extract_pronunciation(wxr, page_data, level_node, base_data)
            elif (
                wxr.config.capture_linkages and section_type in LINKAGE_SECTIONS
            ):
                extract_linkage(
                    wxr,
                    page_data if len(page_data) > 0 else [base_data],
                    level_node,
                    section_type,
                )
            elif (
                wxr.config.capture_translations
                and section_type in TRANSLATION_SECTIONS
            ):
                extract_translation(
                    wxr,
                    page_data if len(page_data) > 0 else [base_data],
                    base_data,
                    level_node,
                )
            elif (
                wxr.config.capture_inflections
                and section_type in INFLECTION_SECTIONS
            ):
                pass
            elif section_type in NOTES_SECTIONS:
                extract_note(
                    wxr,
                    page_data if len(page_data) > 0 else [base_data],
                    level_node,
                )

    find_bottom_category_links(wxr, page_data, level_node)


def process_pos_block(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    pos_title_node: WikiNode,
    pos_argument: str,
    pos_title: str,
):
    pos_data = POS_SECTIONS[pos_argument]
    pos_type = pos_data["pos"]
    if len(page_data) == 0 or "pos" in page_data[-1].model_fields_set:
        page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos = pos_type
    page_data[-1].pos_title = pos_title
    page_data[-1].tags.extend(pos_data.get("tags", []))
    for level_node_template in pos_title_node.find_content(NodeKind.TEMPLATE):
        if level_node_template.template_name == "S":
            if level_node_template.template_parameters.get(3) == "flexion":
                page_data[-1].tags.append("form-of")
            expanded_s = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(level_node_template), expand_all=True
            )
            for span_tag in expanded_s.find_html("span"):
                page_data[-1].pos_id = span_tag.attrs.get("id", "")
                break
    child_nodes = list(pos_title_node.filter_empty_str_child())
    form_line_start = 0  # Ligne de forme
    level_node_index = len(child_nodes)
    gloss_start = len(child_nodes)
    lang_code = page_data[-1].lang_code
    has_gloss_list = False
    for index, child in enumerate(child_nodes):
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TEMPLATE:
                template_name = child.template_name
                if (
                    template_name.endswith("-exemple")
                    and len(page_data[-1].senses) > 0
                ):
                    # zh-exemple and ja-exemple expand to list thus are not the
                    # child of gloss list item.
                    process_exemple_template(
                        wxr, child, page_data[-1].senses[-1]
                    )
                elif template_name.startswith(("zh-mot", "ja-mot")):
                    # skip form line templates
                    form_line_start = index
                elif template_name.startswith(f"{lang_code}-"):
                    extract_inflection(wxr, page_data, child)
            elif child.kind == NodeKind.BOLD and form_line_start == 0:
                form_line_start = index + 1
            elif child.kind == NodeKind.LIST:
                if index < gloss_start:
                    gloss_start = index
                extract_gloss(wxr, page_data, child)
                has_gloss_list = True
            elif child.kind in LEVEL_KIND_FLAGS:
                parse_section(wxr, page_data, base_data, child)
                if index < level_node_index:
                    level_node_index = index

    form_line_nodes = child_nodes[form_line_start:gloss_start]
    extract_form_line(wxr, page_data, form_line_nodes)
    if not has_gloss_list:
        gloss_text = clean_node(
            wxr, None, child_nodes[form_line_start:level_node_index]
        )
        if gloss_text != "":
            page_data[-1].senses.append(Sense(glosses=[gloss_text]))


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
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

    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        for subtitle_template in level2_node.find_content(NodeKind.TEMPLATE):
            # https://fr.wiktionary.org/wiki/Modèle:langue
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_langues
            if subtitle_template.template_name == "langue":
                categories = {}
                lang_code = subtitle_template.template_parameters.get(1)
                if (
                    wxr.config.capture_language_codes is not None
                    and lang_code not in wxr.config.capture_language_codes
                ):
                    continue
                lang_name = clean_node(wxr, categories, subtitle_template)
                wxr.wtp.start_section(lang_name)
                base_data = WordEntry(
                    word=wxr.wtp.title,
                    lang_code=lang_code,
                    lang=lang_name,
                    pos="unknown",
                    categories=categories.get("categories", []),
                )
                etymology_data: Optional[EtymologyData] = None
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    new_etymology_data = parse_section(
                        wxr, page_data, base_data, level3_node
                    )
                    if new_etymology_data is not None:
                        etymology_data = new_etymology_data

                if etymology_data is not None:
                    insert_etymology_data(lang_code, page_data, etymology_data)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]


def find_bottom_category_links(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: WikiNode
) -> None:
    if len(page_data) == 0:
        return
    categories = {}
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
        if isinstance(node, TemplateNode) and node.template_name.endswith(
            " entrée"
        ):
            clean_node(wxr, categories, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            clean_node(wxr, categories, node)

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.categories.extend(categories.get("categories", []))
