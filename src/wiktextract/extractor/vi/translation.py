from itertools import count

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .section_titles import TRANSLATION_SECTIONS
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    sense: str = "",
    from_trans_see: bool = False,
    source: str = "",
):
    for node in level_node.children:
        if isinstance(node, TemplateNode):
            if node.template_name == "trans-top" and not (
                sense != "" and from_trans_see
            ):
                sense = clean_node(
                    wxr, None, node.template_parameters.get(1, "")
                )
                clean_node(wxr, word_entry, node)
            elif node.template_name == "trans-see" and not from_trans_see:
                extract_trans_see_template(wxr, word_entry, node)
            elif node.template_name == "multitrans":
                extract_multitrans_template(wxr, word_entry, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, list_item, sense, source
                )


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    source: str,
):
    lang_name = "unknown"
    lang_code = "unknown"
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = (
                clean_node(wxr, None, list_item.children[:index])
                + node[: node.index(":")].strip()
            ) or "unknown"
            if lang_name != "unknown":
                lang_code = name_to_code(lang_name, "vi") or "unknown"
        elif isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "t-",
            "t+",
            "t2",
            "t2+",
            "tt+",
        ]:
            extract_t_template(wxr, word_entry, node, lang_name, sense, source)
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and lang_name != "unknown"
        ):
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.translations.append(
                    Translation(
                        word=word,
                        lang=lang_name,
                        lang_code=lang_code,
                        sense=sense,
                        source=source,
                    )
                )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense, source
                )


def extract_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    lang_name: str,
    sense: str,
    source: str,
) -> None:
    lang_code = (
        clean_node(wxr, None, t_node.template_parameters.get(1, ""))
        or "unknown"
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for e_node in expanded_node.find_child(NodeKind.TEMPLATE):
        if e_node.template_name in ["t", "t+"]:
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(e_node), expand_all=True
            )
    lit = clean_node(wxr, None, t_node.template_parameters.get("lit", ""))
    raw_tags = []
    roman = ""
    for abbr_tag in expanded_node.find_html_recursively("abbr"):
        gender = abbr_tag.attrs.get("title", "")
        if gender != "":
            raw_tags.append(gender)
    for span_tag in expanded_node.find_html_recursively("span"):
        if span_tag.attrs.get("lang", "").endswith("-Latn"):
            roman = clean_node(wxr, None, span_tag)
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "").split()
        if span_tag.attrs.get("lang") == lang_code:
            word = clean_node(wxr, None, span_tag)
            if word != "":
                tr_data = Translation(
                    word=word,
                    lang=lang_name,
                    lang_code=lang_code,
                    sense=sense,
                    source=source,
                    roman=roman,
                    lit=lit,
                    raw_tags=raw_tags,
                )
                if "Hant" in span_class:
                    tr_data.tags.append("Traditional-Chinese")
                elif "Hans" in span_class:
                    tr_data.tags.append("Simplified-Chinese")
                translate_raw_tags(tr_data)
                word_entry.translations.append(tr_data)

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)


def extract_trans_see_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    sense = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    page_titles = []
    if 2 in t_node.template_parameters:
        for index in count(2):
            if index not in t_node.template_parameters:
                break
            page_titles.append(
                clean_node(wxr, None, t_node.template_parameters[index])
            )
    else:
        page_titles.append(sense)
    for page_title in page_titles:
        if "#" in page_title:
            page_title = page_title[: page_title.index("#")]
        page = wxr.wtp.get_page(page_title)
        if page is None:
            return
        root = wxr.wtp.parse(page.body, pre_expand=True)
        target_node = find_subpage_section(wxr, root, TRANSLATION_SECTIONS)
        if target_node is not None:
            extract_translation_section(
                wxr,
                word_entry,
                target_node,
                sense=sense,
                from_trans_see=True,
                source=page_title,
            )


def find_subpage_section(
    wxr: WiktextractContext, root: WikiNode, target_sections: set[str]
) -> WikiNode | None:
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title in target_sections:
            return level_node
    return None


def extract_multitrans_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node.template_parameters.get("data", ""))
    )
    extract_translation_section(wxr, word_entry, arg)
