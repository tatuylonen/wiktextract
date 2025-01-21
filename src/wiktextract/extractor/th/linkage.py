from itertools import count

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
    source: str = "",
) -> None:
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "col"
        ):
            extract_col_template(wxr, word_entry, node, linkage_type, source)
        elif isinstance(node, TemplateNode) and node.template_name == "ws":
            extract_ws_template(wxr, word_entry, node, linkage_type, source)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_linkage_lite_item(
                    wxr, word_entry, list_item, linkage_type, source
                )


def extract_col_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    source: str,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for li_tag in expanded_node.find_html_recursively("li"):
        l_data = []
        for span_tag in li_tag.find_html("span"):
            span_class = span_tag.attrs.get("class", "")
            if "Latn" in span_class:
                for data in l_data:
                    data.roman = clean_node(wxr, None, span_tag)
            elif "lang" in span_tag.attrs:
                word = clean_node(wxr, None, span_tag)
                if word != "":
                    l_data.append(Linkage(word=word, source=source))
                    if span_class == "Hant":
                        l_data[-1].tags.append("Traditional Chinese")
                    elif span_class == "Hans":
                        l_data[-1].tags.append("Simplified Chinese")
        getattr(word_entry, linkage_type).extend(l_data)


def extract_linkage_lite_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    source: str,
) -> None:
    linkages = []

    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "l":
            l_data = Linkage(
                word=clean_node(wxr, None, node.template_parameters.get(2, "")),
                source=source,
            )
            if l_data.word != "":
                linkages.append(l_data)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            for link_node in node.find_child(NodeKind.LINK):
                link_str = clean_node(wxr, None, link_node)
                if link_str.startswith("อรรถาภิธาน:"):
                    extract_thesaurus_page(
                        wxr, word_entry, linkage_type, link_str
                    )

    getattr(word_entry, linkage_type).extend(linkages)


def extract_thesaurus_page(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    page_title: str,
) -> None:
    page = wxr.wtp.get_page(page_title, 110)
    if page is None or page.body is None:
        return
    root = wxr.wtp.parse(page.body)
    for level2_node in root.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs).removeprefix(
            "ภาษา"
        )
        if lang_name != word_entry.lang:
            continue
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            pos_title = clean_node(wxr, None, level3_node.largs)
            if pos_title != word_entry.pos_title:
                continue
            for linkage_level_node in level3_node.find_child_recursively(
                LEVEL_KIND_FLAGS
            ):
                linkage_title = clean_node(wxr, None, linkage_level_node.largs)
                if LINKAGE_SECTIONS.get(linkage_title) != linkage_type:
                    continue
                extract_linkage_section(
                    wxr,
                    word_entry,
                    linkage_level_node,
                    linkage_type,
                    page_title,
                )


def extract_ws_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    source: str,
) -> None:
    word = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if word != "":
        l_data = Linkage(word=word, source=source)
        getattr(word_entry, linkage_type).append(l_data)


LINKAGE_TEMPLATES = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "synsee": "synonyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
    "cot": "coordinate_terms",
    "coordinate terms": "coordinate_terms",
    "hyper": "hypernyms",
    "hypernyms": "hypernyms",
    "hypo": "hyponyms",
    "hyponyms": "hyponyms",
}


def extract_syn_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    for arg_name in count(2):
        if arg_name not in t_node.template_parameters:
            break
        arg_value = clean_node(wxr, None, t_node.template_parameters[arg_name])
        if arg_value.startswith("อรรถาภิธาน:"):
            extract_thesaurus_page(wxr, word_entry, linkage_type, arg_value)
        elif arg_value != "":
            getattr(word_entry, linkage_type).append(Linkage(word=arg_value))
