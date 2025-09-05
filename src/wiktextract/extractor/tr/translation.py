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
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    sense: str = "",
    from_trans_see: bool = False,
    source: str = "",
) -> None:
    for node in level_node.children:
        if (
            isinstance(node, TemplateNode)
            and node.template_name.lower() in ["üst", "trans-top"]
            and not (sense != "" and from_trans_see)
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, list_item, sense, source
                )
        elif (
            isinstance(node, TemplateNode)
            and node.template_name
            in [
                "çeviri yönlendirme",
                "Türk dilleri-yönlendirme",
                "tercüme-yönlendirme",
                "çeviri-yönlendirme",
                "tercüme yönlendirme",
            ]
            and not from_trans_see
        ):
            extract_trans_see_template(wxr, word_entry, node)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    source: str,
) -> None:
    lang_name = "unknown"
    after_colon = False
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = clean_node(
                wxr,
                None,
                list_item.children[:index] + [node[: node.rindex(":")]],
            ).strip(": ")
            after_colon = True
        elif isinstance(node, TemplateNode) and node.template_name in [
            "ç",
            "çeviri",
        ]:
            extract_çeviri_template(
                wxr, word_entry, node, sense, lang_name, source
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr, word_entry, child_list_item, sense, source
                )
        elif (
            after_colon
            and isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
        ):
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.translations.append(
                    Translation(
                        word=word,
                        lang=lang_name or "unknown",
                        lang_code=name_to_code(lang_name, "tr") or "unknown",
                        sense=sense,
                        source=source,
                    )
                )


def extract_çeviri_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
    lang_name: str,
    source: str,
) -> None:
    lang_code = clean_node(
        wxr, None, t_node.template_parameters.get(1, "unknown")
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    tr_data = Translation(
        word="",
        lang_code=lang_code,
        lang=lang_name or "unknown",
        sense=sense,
        source=source,
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


def extract_trans_see_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://tr.wiktionary.org/wiki/Şablon:çeviri_yönlendirme
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
        page_body = wxr.wtp.get_page_body(page_title, 0)
        if page_body is None:
            return
        root = wxr.wtp.parse(page_body)
        target_node = find_subpage_section(wxr, root, "Çeviriler")
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
    wxr: WiktextractContext, root: WikiNode, target_section: str
) -> WikiNode | None:
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title == target_section:
            return level_node
    return None
