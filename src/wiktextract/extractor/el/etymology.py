from typing import cast

from wikitextprocessor import NodeKind, TemplateNode, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.page import clean_node

from .models import WordEntry
from .parse_utils import (
    POSReturns,
    find_sections,
)
from .pos import extract_form_of_templates
from .pronunciation import process_pron
from .section_titles import Heading, POSName


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
    ret_etym_sublevels: POSReturns = []

    wxr.wtp.start_subsection(title)

    section_num = num

    # Extract form_of data
    for i, t_node in enumerate(etym_contents):
        if isinstance(t_node, TemplateNode):
            extract_form_of_templates(wxr, base_data, t_node, etym_contents, i)
        if isinstance(t_node, WikiNode) and t_node.kind == NodeKind.LIST:
            for l_item in t_node.find_child_recursively(NodeKind.LIST_ITEM):
                for j, l_node in enumerate(l_item.children):
                    if isinstance(l_node, TemplateNode):
                        extract_form_of_templates(
                            wxr, base_data, l_node, l_item.children, j
                        )

    # Greek wiktionary doesn't seem to have etymology templates, or at
    # least they're not used as much.
    etym_text = clean_node(wxr, base_data, etym_contents).lstrip(":#").strip()

    if etym_text:
        base_data.etymology_text = etym_text

    for heading_type, pos, title, tags, num, subnode in find_sections(
        wxr, etym_sublevels
    ):
        if heading_type == Heading.POS:
            section_num = num if num > section_num else section_num
            # SAFETY: Since the heading_type is POS, find_sections
            # "pos_or_section" is guaranteed to be a pos: POSName
            pos = cast(POSName, pos)
            ret_etym_sublevels.append(
                (
                    pos,
                    title,
                    tags,
                    num,
                    subnode,
                    base_data.model_copy(deep=True),
                )
            )
        elif heading_type == Heading.Pron:
            section_num = num if num > section_num else section_num

            num, pron_sublevels = process_pron(
                wxr, subnode, base_data, title, section_num
            )

            ret_etym_sublevels.extend(pron_sublevels)

    return section_num, ret_etym_sublevels
