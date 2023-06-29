from functools import partial
from typing import Dict, List, Union, Optional

from wikitextprocessor import WikiNode, NodeKind
from wiktextract.datautils import data_append
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_linkages(
    wxr: WiktextractContext,
    page_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
    linkage_type: str,
    sense: Optional[str],
) -> Optional[str]:
    """
    Return linkage sense text for `sense` template inside a list item node.
    """
    strip_sense_chars = "()（）:："
    sense_template_names = {"s", "sense"}
    for node in nodes:
        if isinstance(node, str) and len(node.strip()) > 0 and sense is None:
            sense = node.strip(strip_sense_chars)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.LIST_ITEM:
                for item_child in node.children:
                    if (
                        isinstance(item_child, WikiNode)
                        and item_child.kind == NodeKind.TEMPLATE
                    ):
                        template_name = item_child.args[0][0].lower()
                        if template_name in sense_template_names:
                            return clean_node(wxr, None, item_child).strip(
                                strip_sense_chars
                            )
                else:
                    linkage_data = {
                        "word": clean_node(wxr, None, node.children).strip(
                            strip_sense_chars
                        )
                    }
                    if sense is not None:
                        linkage_data["sense"] = sense
                    add_linkage_data(wxr, page_data, linkage_type, linkage_data)
            elif node.kind == NodeKind.TEMPLATE:
                template_name = node.args[0][0].lower()
                if template_name in {"s", "sense"}:
                    sense = clean_node(wxr, None, node).strip(strip_sense_chars)
                elif template_name.endswith("-saurus"):
                    extract_saurus_template(
                        wxr, node, page_data, linkage_type, sense
                    )
                else:
                    expanded_node = wxr.wtp.parse(
                        wxr.wtp.node_to_wikitext(node), expand_all=True
                    )
                    extract_linkages(
                        wxr,
                        page_data,
                        [expanded_node],
                        linkage_type,
                        sense,
                    )
            elif node.children:
                returned_sense = extract_linkages(
                    wxr, page_data, node.children, linkage_type, sense
                )
                if returned_sense is not None:
                    sense = returned_sense


def extract_saurus_template(
    wxr: WiktextractContext,
    node: WikiNode,
    page_data: Dict,
    linkage_type: str,
    sense: str
) -> None:
    from wiktextract.thesaurus import search_thesaurus

    thesaurus_page_title = node.args[-1][0]
    for thesaurus in search_thesaurus(
            wxr.thesaurus_db_conn,
            thesaurus_page_title,
            page_data[-1].get("lang_code"),
            page_data[-1].get("pos"),
            linkage_type,
    ):
        linkage_data = {"word": thesaurus.term}
        if thesaurus.roman is not None:
            linkage_data["roman"] = thesaurus.roman
        if thesaurus.tags is not None:
            linkage_data["tags"] = thesaurus.tags.split("|")
        if thesaurus.language_variant is not None:
            linkage_data[
                "language_variant"
            ] = thesaurus.language_variant
        if sense is not None:
            linkage_data["sense"] = sense
        elif thesaurus.sense is not None:
            linkage_data["sense"] = thesaurus.sense
        add_linkage_data(
            wxr, page_data, linkage_type, linkage_data
        )


def add_linkage_data(
    wxr: WiktextractContext,
    page_data: List[Dict],
    linkage_type: str,
    linkage_data: Dict,
) -> None:
    """
    Append the linkage data dictionary to a sense dictionary if the linkage
    sense is similar to the word gloss. Otherwise append to the base dictionary.
    """
    if "sense" in linkage_data:
        from rapidfuzz.fuzz import partial_token_set_ratio
        from rapidfuzz.process import extractOne
        from rapidfuzz.utils import default_process

        choices = {
            sense_dict.get("glosses", [None])[0]: sense_dict
            for sense_dict in page_data[-1]["senses"]
        }
        if match_result := extractOne(
            linkage_data["sense"],
            choices.keys(),
            score_cutoff=85,
            scorer=partial(partial_token_set_ratio, processor=default_process),
        ):
            match_gloss = match_result[0]
            data_append(wxr, choices[match_gloss], linkage_type, linkage_data)
            return

    data_append(wxr, page_data[-1], linkage_type, linkage_data)
