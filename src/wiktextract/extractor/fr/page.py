import copy
import logging
from collections import defaultdict
from typing import Dict, List, Optional

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

from .etymology import EtymologyData, extract_etymology, insert_etymology_data
from .form_line import extract_form_line
from .gloss import extract_gloss, process_exemple_template
from .inflection import extract_inflection
from .linkage import extract_linkage
from .note import extract_note
from .pronunciation import extract_pronunciation
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
    page_data: List[Dict],
    base_data: Dict,
    level_node: WikiNode,
) -> Optional[List[EtymologyData]]:
    # Page structure: https://fr.wiktionary.org/wiki/Wiktionnaire:Structure_des_pages
    for level_node_template in level_node.find_content(NodeKind.TEMPLATE):
        if level_node_template.template_name == "S":
            # French Wiktionary uses a `S` template for all subtitles, we could
            # find the subtitle type by only checking the template parameter.
            # https://fr.wiktionary.org/wiki/Modèle:S
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections
            section_type = level_node_template.template_parameters.get(1)
            subtitle = clean_node(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node.largs,
            )
            wxr.wtp.start_subsection(subtitle)
            if section_type in wxr.config.OTHER_SUBTITLES["ignored_sections"]:
                pass
            # POS parameters:
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections_de_types_de_mots
            elif section_type in wxr.config.POS_SUBTITLES:
                process_pos_block(
                    wxr,
                    page_data,
                    base_data,
                    level_node,
                    section_type,
                    subtitle,
                )
            elif (
                wxr.config.capture_etymologies
                and section_type in wxr.config.OTHER_SUBTITLES["etymology"]
            ):
                return extract_etymology(wxr, level_node.children)
            elif (
                wxr.config.capture_pronunciation
                and section_type in wxr.config.OTHER_SUBTITLES["pronunciation"]
            ):
                extract_pronunciation(wxr, page_data, level_node, base_data)
            elif (
                wxr.config.capture_linkages
                and section_type in wxr.config.LINKAGE_SUBTITLES
            ):
                extract_linkage(
                    wxr,
                    page_data,
                    level_node,
                    section_type,
                )
            elif (
                wxr.config.capture_translations
                and section_type in wxr.config.OTHER_SUBTITLES["translations"]
            ):
                extract_translation(wxr, page_data, level_node)
            elif (
                wxr.config.capture_inflections
                and section_type
                in wxr.config.OTHER_SUBTITLES["inflection_sections"]
            ):
                pass
            elif section_type in wxr.config.OTHER_SUBTITLES["notes"]:
                extract_note(wxr, page_data, level_node)


def process_pos_block(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    pos_title_node: TemplateNode,
    pos_argument: str,
    pos_title: str,
):
    pos_type = wxr.config.POS_SUBTITLES[pos_argument]["pos"]
    page_data.append(copy.deepcopy(base_data))
    page_data[-1]["pos"] = pos_type
    page_data[-1]["pos_title"] = pos_title
    child_nodes = list(pos_title_node.filter_empty_str_child())
    form_line_start = 0  # Ligne de forme
    gloss_start = len(child_nodes)
    lang_code = page_data[-1].get("lang_code")
    for index, child in enumerate(child_nodes):
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TEMPLATE:
                template_name = child.template_name
                if (
                    template_name.endswith("-exemple")
                    and len(page_data[-1].get("senses", [])) > 0
                ):
                    # zh-exemple and ja-exemple expand to list thus are not the
                    # child of gloss list item.
                    process_exemple_template(
                        wxr, child, page_data[-1]["senses"][-1]
                    )
                elif template_name.startswith(("zh-mot", "ja-mot")):
                    # skip form line templates
                    continue
                elif template_name.startswith(f"{lang_code}-"):
                    extract_inflection(wxr, page_data, child)
            elif child.kind == NodeKind.BOLD:
                form_line_start = index + 1
            elif child.kind == NodeKind.LIST:
                gloss_start = index
                extract_gloss(wxr, page_data, child)
            elif child.kind in LEVEL_KINDS:
                parse_section(wxr, page_data, base_data, child)

    form_line_nodes = child_nodes[form_line_start:gloss_start]
    extract_form_line(wxr, page_data, form_line_nodes)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> List[Dict[str, str]]:
    if wxr.config.verbose:
        logging.info(f"Parsing page: {page_title}")

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
        for subtitle_template in level2_node.find_content(NodeKind.TEMPLATE):
            # https://fr.wiktionary.org/wiki/Modèle:langue
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_langues
            if subtitle_template.template_name == "langue":
                base_data = defaultdict(list, {"word": wxr.wtp.title})
                lang_code = subtitle_template.template_parameters.get(1)
                if (
                    wxr.config.capture_language_codes is not None
                    and lang_code not in wxr.config.capture_language_codes
                ):
                    continue
                lang_name = clean_node(wxr, base_data, subtitle_template)
                wxr.wtp.start_section(lang_name)
                base_data["lang_name"] = lang_name
                base_data["lang_code"] = lang_code
                etymology_data: Optional[EtymologyData] = None
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    new_etymology_data = parse_section(
                        wxr, page_data, base_data, level3_node
                    )
                    if new_etymology_data is not None:
                        etymology_data = new_etymology_data

                if etymology_data is not None:
                    insert_etymology_data(lang_code, page_data, etymology_data)

    return page_data
