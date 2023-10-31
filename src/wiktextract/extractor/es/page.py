import copy
import logging
from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
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

    return [d.model_dump(exclude_defaults=True) for d in page_data]
