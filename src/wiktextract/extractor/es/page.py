import copy
import logging
from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wiktextract.datautils import append_base_data
from wiktextract.extractor.es.pronunciation import extract_pronunciation
from wiktextract.extractor.es.models import WordEntry, PydanticLogger

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

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
) -> None:
    # Page Structure: https://es.wiktionary.org/wiki/Wikcionario:Estructura
    subtitle = clean_node(wxr, page_data[-1], level_node.largs)
    wxr.wtp.start_subsection(subtitle)

    pos_template_name = None
    for level_node_template in level_node.find_content(NodeKind.TEMPLATE):
        pos_template_name = level_node_template.template_name

    if subtitle in wxr.config.OTHER_SUBTITLES["ignored_sections"]:
        pass

    elif pos_template_name and pos_template_name in wxr.config.POS_SUBTITLES:
        process_pos_block(
            wxr, page_data, base_data, level_node, pos_template_name, subtitle
        )
    else:
        wxr.wtp.debug(
            f"Unprocessed section: {subtitle}",
            sortid="extractor/es/page/parse_section/48",
        )


def process_pos_block(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    pos_level_node: WikiNode,
    pos_template_name: str,
    pos_title: str,
):
    pos_type = wxr.config.POS_SUBTITLES[pos_template_name]["pos"]
    append_base_data(page_data, "pos", pos_type, base_data)
    page_data[-1]["pos_title"] = pos_title
    child_nodes = list(pos_level_node.filter_empty_str_child())

    for child in child_nodes:
        if (
            isinstance(child, WikiNode)
            and child.kind == NodeKind.TEMPLATE
            and (
                "inflect" in child.template_name
                or "v.conj" in child.template_name
            )
        ):
            # XXX: Extract forms
            pass
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            # XXX: Extract data
            pass
        else:
            # XXX: Extract data
            pass
    pass


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> List[Dict[str, str]]:
    if wxr.config.verbose:
        logging.info(f"Parsing page: {page_title}")
        # Pass current wiktextractcontext to pydantic for more better logging
        PydanticLogger.wxr = wxr

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

    page_data: List[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        for subtitle_template in level2_node.find_content(NodeKind.TEMPLATE):
            # https://es.wiktionary.org/wiki/Plantilla:lengua
            # https://es.wiktionary.org/wiki/Apéndice:Códigos_de_idioma
            if subtitle_template.template_name == "lengua":
                categories_and_links = defaultdict(list)
                lang_code = subtitle_template.template_parameters.get(1)
                if (
                    wxr.config.capture_language_codes is not None
                    and lang_code not in wxr.config.capture_language_codes
                ):
                    continue

                lang_name = clean_node(
                    wxr, categories_and_links, subtitle_template
                )
                wxr.wtp.start_section(lang_name)
                base_data = WordEntry(
                    lang_name=lang_name, lang_code=lang_code, word=wxr.wtp.title
                )
                base_data.update(categories_and_links)
                page_data.append(copy.deepcopy(base_data))
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    parse_section(wxr, page_data, base_data, level3_node)

                for not_level3_node in level2_node.invert_find_child(
                    NodeKind.LEVEL3
                ):
                    if (
                        isinstance(not_level3_node, WikiNode)
                        and not_level3_node.kind == NodeKind.TEMPLATE
                        and not_level3_node.template_name == "pron-graf"
                    ):
                        if wxr.config.capture_pronunciation:
                            extract_pronunciation(
                                wxr, page_data[-1], not_level3_node
                            )
                    else:
                        wxr.wtp.debug(
                            f"Found unexpected child in level 2 'lengua' node: {not_level3_node}",
                            sortid="extractor/es/page/parse_page/80",
                        )

    return [d.model_dump(exclude_defaults=True) for d in page_data]
