from typing import Any

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
from .descendant import extract_desc_section
from .etymology import (
    EtymologyData,
    extract_etymology,
    extract_etymology_examples,
    insert_etymology_data,
)
from .form_line import extract_form_line
from .gloss import extract_gloss, process_exemple_template
from .inflection import extract_inflection
from .linkage import extract_linkage
from .models import Sense, WordEntry
from .note import extract_note, extract_recognition_rate_section
from .pronunciation import extract_homophone_section, extract_pronunciation
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
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> EtymologyData | None:
    etymology_data = None
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
                pass
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
                extract_translation_section(
                    wxr,
                    page_data if len(page_data) > 0 else [base_data],
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
            elif section_type == "taux de reconnaissance":
                extract_recognition_rate_section(
                    wxr,
                    page_data[-1] if len(page_data) > 0 else base_data,
                    level_node,
                )
            elif section_type == "attestations":
                extract_etymology_examples(wxr, level_node, base_data)
            elif section_type in ["homophones", "homo"]:
                extract_homophone_section(
                    wxr,
                    page_data,
                    base_data,
                    level_node,
                    title_categories.get("categories", []),
                )
            elif section_type == "dérivés autres langues":
                extract_desc_section(
                    wxr,
                    page_data[-1] if len(page_data) > 0 else base_data,
                    level_node,
                )
            else:
                wxr.wtp.debug(
                    f"Unknown section: {section_type}",
                    sortid="extractor/fr/page/parse_section/127",
                )

    find_bottom_category_links(wxr, page_data, level_node)
    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)
    return etymology_data


def process_pos_block(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    pos_title_node: LevelNode,
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
    is_first_bold = True
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
                elif template_name.startswith(
                    (f"{lang_code}-", "flex-ku-", "zh-formes")
                ):
                    extract_inflection(wxr, page_data, child)
            elif child.kind == NodeKind.BOLD and is_first_bold:
                if index < form_line_start:
                    form_line_start = index
            elif child.kind == NodeKind.LIST and child.sarg.startswith("#"):
                if index < gloss_start:
                    gloss_start = index
                extract_gloss(wxr, page_data, child)
                has_gloss_list = True
            elif child.kind in LEVEL_KIND_FLAGS:
                level_node_index = index
                break

    form_line_nodes = child_nodes[form_line_start:gloss_start]
    extract_form_line(wxr, page_data, form_line_nodes)
    if not has_gloss_list:
        gloss_text = clean_node(
            wxr, None, child_nodes[form_line_start + 1 : level_node_index]
        )
        if gloss_text != "":
            page_data[-1].senses.append(Sense(glosses=[gloss_text]))


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # Page structure
    # https://fr.wiktionary.org/wiki/Convention:Structure_des_pages
    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")
    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
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
                    word=page_title,
                    lang_code=lang_code,
                    lang=lang_name,
                    pos="unknown",
                    categories=categories.get("categories", []),
                )
                etymology_data: EtymologyData | None = None
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
