from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    sense = ""
    tr_list = []
    cats = {}
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "ter-atas",
            "teratas",
            "trans-top",
        ]:
            sense = clean_node(wxr, cats, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                tr_list.extend(
                    extract_translation_list_item(wxr, list_item, sense)
                )

    if len(page_data) == 0 or page_data[-1].lang_code != base_data.lang_code:
        base_data.categories.extend(cats.get("categories", []))
        for tr_data in tr_list:
            if tr_data.word != "":
                base_data.translations.append(tr_data)
                base_data.categories.extend(tr_data.categories)
    elif level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(cats.get("categories", []))
                for tr_data in tr_list:
                    if tr_data.word != "":
                        data.translations.append(tr_data)
                        data.categories.extend(tr_data.categories)
    else:
        page_data[-1].categories.extend(cats.get("categories", []))
        for tr_data in tr_list:
            if tr_data.word != "":
                page_data[-1].translations.append(tr_data)
                page_data[-1].categories.extend(tr_data.categories)


def extract_translation_list_item(
    wxr: WiktextractContext, list_item: WikiNode, sense: str
) -> None:
    tr_list = []
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
            tr_list.append(extract_t_template(wxr, node, sense, lang_name))
        elif (
            isinstance(node, TemplateNode)
            and node.template_name
            in ["penerang", "qualifier", "i", "q", "qual"]
            and len(tr_list) > 0
        ):
            raw_tag = clean_node(wxr, None, node).strip("() ")
            if raw_tag != "":
                tr_list[-1].raw_tags.append(raw_tag)
                translate_raw_tags(tr_list[-1])
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                tr_list.extend(
                    extract_translation_list_item(wxr, child_list_item, sense)
                )
    return tr_list


def extract_t_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: str,
    lang_name: str,
) -> Translation:
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
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, tr_data, link_node)
    return tr_data
