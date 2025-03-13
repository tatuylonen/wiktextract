from mediawiki_langcodes import name_to_code
from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    sense = ""
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name.lower() in [
            "üst",
            "trans-top",
        ]:
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_translation_list_item(wxr, word_entry, list_item, sense)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
) -> None:
    lang_name = "unknown"
    for node in list_item.children:
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = node[: node.index(":")].strip()
        elif isinstance(node, TemplateNode) and node.template_name in [
            "ç",
            "çeviri",
        ]:
            extract_çeviri_template(wxr, word_entry, node, sense, lang_name)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense
                )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.translations.append(
                    Translation(
                        word=word,
                        lang=lang_name,
                        lang_code=name_to_code(lang_name, "tr") or "unknown",
                    )
                )


def extract_çeviri_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
    lang_name: str,
) -> None:
    lang_code = clean_node(
        wxr, None, t_node.template_parameters.get(1, "unknown")
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    tr_data = Translation(
        word="", lang_code=lang_code, lang=lang_name, sense=sense
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        tr_data.word = clean_node(wxr, None, span_tag)
        break
    for abbr_tag in expanded_node.find_html_recursively("abbr"):
        raw_tag = clean_node(wxr, None, abbr_tag)
        if raw_tag != "":
            tr_data.raw_tags.append(raw_tag)
    for span_tag in expanded_node.find_html("span"):
        span_class = span_tag.attrs.get("class", "")
        if span_class in ["tr", "tr Latn"]:
            tr_data.roman = clean_node(wxr, None, span_tag)
            break
    if tr_data.word != "":
        translate_raw_tags(tr_data)
        word_entry.translations.append(tr_data)
    clean_node(wxr, word_entry, expanded_node)
