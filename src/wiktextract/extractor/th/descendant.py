from mediawiki_langcodes import code_to_name
from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Descendant, WordEntry


def extract_descendant_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_desc_list_item(wxr, word_entry, [], list_item)


def extract_desc_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    parent_data: list[Descendant],
    list_item: WikiNode,
) -> None:
    desc_list = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "desc",
            "descendant",
            "desctree",
            "descendants tree",
        ]:
            desc_list.extend(
                extract_desc_template(wxr, word_entry, parent_data, node)
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_desc_list_item(
                    wxr, word_entry, desc_list, child_list_item
                )


def extract_desc_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    parent_data: list[Descendant],
    t_node: TemplateNode,
) -> list[Descendant]:
    desc_data = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    lang_name = code_to_name(lang_code, "th") or "unknown"
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "")
        if span_lang == lang_code:
            desc_data.append(
                Descendant(
                    lang_code=lang_code,
                    lang=lang_name,
                    word=clean_node(wxr, None, span_tag),
                )
            )
        elif span_lang.endswith("-Latn") and len(desc_data) > 0:
            desc_data[-1].roman = clean_node(wxr, None, span_tag)
        elif span_class == "mention-gloss" and len(desc_data) > 0:
            desc_data[-1].sense = clean_node(wxr, None, span_tag)

    if len(parent_data) > 0:
        for p_data in parent_data:
            p_data.descendants.extend(desc_data)
    else:
        word_entry.descendants.extend(desc_data)
    clean_node(wxr, word_entry, expanded_node)
    return desc_data
