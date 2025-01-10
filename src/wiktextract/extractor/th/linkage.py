from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "col"
        ):
            extract_col_template(wxr, word_entry, node, linkage_type)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_linkage_lite_item(
                    wxr, word_entry, list_item, linkage_type
                )


def extract_col_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for li_tag in expanded_node.find_html_recursively("li"):
        l_data = Linkage(word="")
        for span_tag in li_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            if "Latn" in span_class:
                l_data.roman = clean_node(wxr, None, span_tag)
            elif "lang" in span_tag.attrs:
                l_data.word = clean_node(wxr, None, span_tag)
        if l_data.word != "":
            getattr(word_entry, linkage_type).append(l_data)


def extract_linkage_lite_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
) -> None:
    linkages = []

    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "l":
            l_data = Linkage(
                word=clean_node(wxr, None, node.template_parameters.get(2, ""))
            )
            if l_data.word != "":
                linkages.append(l_data)

    getattr(word_entry, linkage_type).extend(linkages)
