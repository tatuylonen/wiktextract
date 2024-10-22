from typing import TypeAlias

from wikitextprocessor import WikiNode
from wikitextprocessor.core import TemplateArgs
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.clean import clean_value
from wiktextract.page import clean_node

from .models import TemplateData, WordEntry
from .parse_utils import (
    ETYMOLOGY_TEMPLATES,
    PANEL_TEMPLATES,
    POSReturns,
    find_sections,
)
from .pronunciation import process_pron
from .section_titles import POS_HEADINGS, Heading, Tags
from .text_utils import ENDING_NUMBER_RE


def process_etym(
    wxr: WiktextractContext,
    base_data: WordEntry,
    node: WikiNode,
    title: str,
    num: int,
) -> tuple[int, POSReturns]:
    """Extract etymological data from section and process POS children."""
    # Get everything except subsections, which we assume are POS nodes.
    etym_contents = list(node.invert_find_child(LEVEL_KIND_FLAGS))
    etym_sublevels = list(node.find_child(LEVEL_KIND_FLAGS))
    ret_etym_sublevels: list[tuple[str, Tags, int, WikiNode, WordEntry]] = []

    section_num = num

    # Greek wiktionary doesn't seem to have etymology templates, or at
    # least they're not used as much.
    etym_text = clean_node(wxr, base_data, etym_contents)

    if etym_text:
        base_data.etymology_text = etym_text

    for heading_type, heading_name, tags, num, subnode in find_sections(
        wxr, etym_sublevels
    ):
        if heading_type == Heading.POS:
            section_num = num if num > section_num else section_num
            ret_etym_sublevels.append(
                (heading_name, tags, num, subnode, base_data.copy(deep=True))
            )
        elif heading_type == Heading.Pron:
            section_num = num if num > section_num else section_num

            num, pron_sublevels = process_pron(
                wxr, subnode, base_data, section_num
            )

            ret_etym_sublevels.extend(pron_sublevels)

    return section_num, ret_etym_sublevels
