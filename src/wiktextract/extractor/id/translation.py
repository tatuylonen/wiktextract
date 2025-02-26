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
        if isinstance(node, TemplateNode) and node.template_name in [
            "trans-top",
            "kotak mulai",
            "kotak awal",
        ]:
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
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
    lang_code = "unknown"
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = (
                clean_node(wxr, None, list_item.children[:index])
                + node[: node.index(":")].strip()
            )
            lang_name = lang_name.removeprefix("bahasa ").strip()
            if lang_name == "":
                lang_name = "unknown"
            if lang_name != "unknown":
                lang_code = name_to_code(lang_name, "id")
                if lang_code == "":
                    lang_code = "unknown"
        elif isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "t+",
            "trad-",
            "trad+",
            "t-simple",
        ]:
            extract_t_template(wxr, word_entry, node, lang_name, sense)
        elif isinstance(node, TemplateNode) and node.template_name in [
            "qualifier",
            "q",
            "qual",
            "f",
            "n",
            "p",
        ]:
            extract_qualifier_template(wxr, word_entry, node)
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
                    )
                )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense
                )


def extract_t_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    lang_name: str,
    sense: str,
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
    for span_tag in expanded_node.find_html_recursively("span"):
        if span_tag.attrs.get("lang") == lang_code and tr_data.word == "":
            tr_data.word = clean_node(wxr, None, span_tag)
        elif "tr Latn" == span_tag.attrs.get("class", ""):
            tr_data.roman = clean_node(wxr, None, span_tag)

    tr_data.lit = clean_node(
        wxr, None, t_node.template_parameters.get("lit", "")
    )
    for abbr_tag in expanded_node.find_html_recursively("abbr"):
        tr_data.raw_tags.append(clean_node(wxr, None, abbr_tag))

    if tr_data.word != "":
        translate_raw_tags(tr_data)
        word_entry.translations.append(tr_data)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, word_entry, link_node)


def extract_qualifier_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    t_str = clean_node(wxr, None, t_node).strip("() ")
    for raw_tag in t_str.split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "" and len(word_entry.translations) > 0:
            word_entry.translations[-1].raw_tags.append(raw_tag)
    if len(word_entry.translations) > 0:
        translate_raw_tags(word_entry.translations[-1])
