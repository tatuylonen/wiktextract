import copy
import logging
from collections import defaultdict
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.datautils import append_base_data
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

from .gloss import extract_gloss
from .inflection import extract_inflection

# Templates that are used to form panels on pages and that
# should be ignored in various positions
PANEL_TEMPLATES = {}

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = {}

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = {}


def parse_section(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> None:
    # https://fr.wiktionary.org/wiki/Wiktionnaire:Structure_des_pages
    if isinstance(node, list):
        for x in node:
            parse_section(wxr, page_data, base_data, x)
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind in LEVEL_KINDS:
        level_node = node.largs[0][0]
        if level_node.kind == NodeKind.TEMPLATE:
            level_template_name, *level_template_args = level_node.largs
            if level_template_name == ["S"]:
                # https://fr.wiktionary.org/wiki/Modèle:S
                # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections
                section_type = level_template_args[0][0]
                subtitle = clean_node(wxr, page_data[-1], node.largs)
                wxr.wtp.start_subsection(subtitle)
                if (
                    section_type
                    in wxr.config.OTHER_SUBTITLES["ignored_sections"]
                ):
                    pass
                # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections_de_types_de_mots
                elif section_type in wxr.config.POS_SUBTITLES:
                    process_pos_block(
                        wxr, page_data, base_data, node, section_type
                    )
                elif (
                    wxr.config.capture_etymologies
                    and section_type in wxr.config.OTHER_SUBTITLES["etymology"]
                ):
                    extract_etymology(wxr, page_data, base_data, node.children)
                elif (
                    wxr.config.capture_pronunciation
                    and section_type
                    in wxr.config.OTHER_SUBTITLES["pronunciation"]
                ):
                    pass
                elif (
                    wxr.config.capture_linkages
                    and section_type in wxr.config.LINKAGE_SUBTITLES
                ):
                    pass
                elif (
                    wxr.config.capture_translations
                    and section_type
                    in wxr.config.OTHER_SUBTITLES["translations"]
                ):
                    pass
                elif (
                    wxr.config.capture_inflections
                    and section_type
                    in wxr.config.OTHER_SUBTITLES["inflection_sections"]
                ):
                    pass
                else:
                    pass
                # wxr.wtp.debug(
                #     f"Unhandled section type: {subtitle}",
                #     sortid="extractor/fr/page/parse_section/192",
                # )


def process_pos_block(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    node: WikiNode,
    pos_argument: str,
):
    pos_type = wxr.config.POS_SUBTITLES[pos_argument]["pos"]
    base_data["pos"] = pos_type
    append_base_data(page_data, "pos", pos_type, base_data)
    child_nodes = list(node.filter_empty_str_child())
    headword_start = 0
    gloss_start = len(child_nodes)
    for index, child in enumerate(child_nodes):
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TEMPLATE:
                template_name = child.template_name
                lang_code = base_data.get("lang_code")
                if template_name.startswith(f"{lang_code}-"):
                    extract_inflection(wxr, page_data, child, template_name)
            elif child.kind == NodeKind.BOLD:
                headword_start = index + 1
            elif child.kind == NodeKind.LIST:
                gloss_start = index
                extract_gloss(wxr, page_data, child)
            elif child.kind in LEVEL_KINDS:
                parse_section(wxr, page_data, base_data, child)
        else:
            parse_section(wxr, page_data, base_data, child)

    headword_nodes = child_nodes[headword_start:gloss_start]


def extract_etymology(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    nodes: List[Union[WikiNode, str]],
) -> None:
    level_node_index = -1
    for index, node in enumerate(nodes):
        if isinstance(node, WikiNode) and node.kind in LEVEL_KINDS:
            level_node_index = index
            break
    if level_node_index != -1:
        etymology = clean_node(wxr, page_data[-1], nodes[:index])
    else:
        etymology = clean_node(wxr, page_data[-1], nodes)
    base_data["etymology_text"] = etymology
    append_base_data(page_data, "etymology_text", etymology, base_data)
    if level_node_index != -1:
        parse_section(wxr, page_data, base_data, nodes[level_node_index:])


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
    for node in filter(lambda n: isinstance(n, WikiNode), tree.children):
        # ignore link created by `voir` template at the page top
        if node.kind == NodeKind.TEMPLATE:
            template_name = node.template_name
            if template_name in {"voir", "voir2"} or template_name.startswith(
                "voir/"
            ):
                continue
        if node.kind != NodeKind.LEVEL2:
            wxr.wtp.warning(
                f"Unexpected top-level node: {node}",
                sortid="extractor/fr/page/parse_page/94",
            )
            continue

        level_node = node.largs[0][0]
        if level_node.kind == NodeKind.TEMPLATE:
            level_template_name, *level_template_args = level_node.largs
            # https://fr.wiktionary.org/wiki/Modèle:langue
            # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_langues
            if level_template_name == ["langue"]:
                categories_and_links = defaultdict(list)
                lang_code = level_template_args[0][0]
                lang_name = clean_node(wxr, categories_and_links, level_node)
                wxr.wtp.start_section(lang_name)
                base_data = defaultdict(
                    list,
                    {
                        "lang": lang_name,
                        "lang_code": lang_code,
                        "word": wxr.wtp.title,
                    },
                )
                base_data.update(categories_and_links)
                page_data.append(copy.deepcopy(base_data))
                parse_section(wxr, page_data, base_data, node.children)

    return page_data
