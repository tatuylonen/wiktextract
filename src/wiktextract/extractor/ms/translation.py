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
        if isinstance(node, TemplateNode) and node.template_name in [
            "ter-atas",
            "teratas",
            "trans-top",
        ]:
            sense = clean_node(wxr, word_entry, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(wxr, word_entry, list_item, sense)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
) -> None:
    lang_name = "unknown"
    for node in list_item.children:
        if (
            isinstance(node, str)
            and node.strip().endswith(":")
            and lang_name == "unknown"
        ):
            lang_name = node.strip(": ")
        elif isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "trad",
            "tø",
            "t-",
            "t+",
        ]:
            extract_t_template(wxr, word_entry, node, sense, lang_name)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense
                )


def extract_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
    lang_name: str,
) -> None:
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if lang_code == "":
        lang_code = "unknown"
    tr_data = Translation(
        word="", lang=lang_name, lang_code=lang_code, sense=sense
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        if span_tag.attrs.get("lang") == lang_code and tr_data.word == "":
            tr_data.word = clean_node(wxr, None, span_tag)
        elif span_tag.attrs.get("class", "") == "gender":
            for abbr_tag in span_tag.find_html("abbr"):
                raw_tag = clean_node(wxr, None, abbr_tag)
                if raw_tag not in ["", "?", "jantina tidak diberi"]:
                    tr_data.raw_tags.append(raw_tag)
        elif "tr" in span_tag.attrs.get("class", ""):
            tr_data.roman = clean_node(wxr, None, span_tag)
    if tr_data.word != "":
        translate_raw_tags(tr_data)
        word_entry.translations.append(tr_data)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, word_entry, link_node)
