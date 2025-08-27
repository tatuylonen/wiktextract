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
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
    sense: str = "",
    source: str = "",
    from_trans_see: bool = False,
) -> None:
    tr_list = []
    cats = {}
    for node in level_node.children:
        if (
            isinstance(node, TemplateNode)
            and node.template_name
            in [
                "ter-atas",
                "teratas",
                "trans-top",
            ]
            and not (sense != "" and from_trans_see)
        ):
            sense = clean_node(wxr, cats, node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                tr_list.extend(
                    extract_translation_list_item(wxr, list_item, sense, source)
                )
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in ["ter-lihat", "trans-see"]
            and not from_trans_see
        ):
            extract_trans_see_template(wxr, page_data, base_data, node)

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
    wxr: WiktextractContext, list_item: WikiNode, sense: str, source: str
) -> None:
    tr_list = []
    lang_name = "unknown"
    for node in list_item.children:
        if (
            isinstance(node, str)
            and node.strip().endswith(":")
            and lang_name == "unknown"
        ):
            lang_name = node.strip(": ") or "unknown"
        elif isinstance(node, TemplateNode) and node.template_name in [
            "t",
            "trad",
            "tø",
            "t-",
            "t+",
        ]:
            tr_list.append(
                extract_t_template(wxr, node, sense, lang_name, source)
            )
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
                    extract_translation_list_item(
                        wxr, child_list_item, sense, source
                    )
                )
    return tr_list


def extract_t_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: str,
    lang_name: str,
    source: str,
) -> Translation:
    lang_code = (
        clean_node(wxr, None, t_node.template_parameters.get(1, ""))
        or "unknown"
    )
    tr_data = Translation(
        word="", lang=lang_name, lang_code=lang_code, sense=sense, source=source
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


def extract_trans_see_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    t_node: TemplateNode,
):
    # https://ms.wiktionary.org/wik/Templat:ter-lihat
    sense = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    page_titles = []
    if 2 in t_node.template_parameters:
        for index in range(2, 11):
            if index not in t_node.template_parameters:
                break
            page_titles.append(
                clean_node(wxr, None, t_node.template_parameters[index])
            )
    else:
        page_titles.append(
            clean_node(wxr, None, t_node.template_parameters.get(1, ""))
        )
    for page_title in page_titles:
        if "#" in page_title:
            page_title = page_title[: page_title.index("#")]
        page = wxr.wtp.get_page(page_title)
        if page is None:
            return
        root = wxr.wtp.parse(page.body)
        target_node = find_subpage_section(wxr, root, "Terjemahan")
        if target_node is not None:
            extract_translation_section(
                wxr,
                page_data,
                base_data,
                target_node,
                sense=sense,
                source=page_title,
                from_trans_see=True,
            )


def find_subpage_section(
    wxr: WiktextractContext, root: WikiNode, target_section: str
) -> WikiNode | None:
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title == target_section:
            return level_node
    return None
