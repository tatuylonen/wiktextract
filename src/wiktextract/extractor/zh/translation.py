from mediawiki_langcodes import code_to_name, name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .section_titles import TRANSLATIONS_TITLES
from .tags import TEMPLATE_TAG_ARGS, translate_raw_tags


def extract_translation(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    sense: str = "",
    is_subpage: bool = False,
) -> None:
    for child in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        if isinstance(child, TemplateNode):
            template_name = child.template_name.lower()
            if (
                template_name in {"trans-top", "翻譯-頂", "trans-top-also"}
                and 1 in child.template_parameters
            ):
                sense = clean_node(wxr, None, child.template_parameters.get(1))
            elif (
                template_name in {"see translation subpage", "trans-see"}
                and not is_subpage
            ):
                translation_subpage(wxr, page_data, child)
            elif template_name == "multitrans":
                wikitext = "".join(
                    wxr.wtp.node_to_wikitext(c)
                    for c in child.template_parameters.get("data", [])
                )
                multitrans = wxr.wtp.parse(wikitext)
                extract_translation(wxr, page_data, multitrans, sense)
        else:
            for list_item in child.find_child_recursively(NodeKind.LIST_ITEM):
                process_translation_list_item(
                    wxr,
                    page_data,
                    list_item,
                    sense,
                )


def process_translation_list_item(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_item: WikiNode,
    sense: str,
) -> None:
    tr_data = Translation(
        word="", sense=sense, lang="unknown", lang_code="unknown"
    )

    for child_index, child in enumerate(list_item.filter_empty_str_child()):
        if child_index == 0:
            lang_text = ""
            if isinstance(child, str):
                if "：" in child:
                    lang_text = child[: child.index("：")]
                elif ":" in child:
                    lang_text = child[: child.index(":")]
            else:
                lang_text = clean_node(wxr, None, child)
            if len(lang_text) > 0:
                tr_data.lang = lang_text.strip()
                tr_data.lang_code = name_to_code(tr_data.lang, "zh")
        elif isinstance(child, TemplateNode):
            template_name = child.template_name.lower()
            if template_name in {
                "t",
                "t+",
                "tt",
                "tt+",
                "t-check",
                "t+check",
                "l",
            }:
                if len(tr_data.word) > 0:
                    page_data[-1].translations.append(
                        tr_data.model_copy(deep=True)
                    )
                    tr_data = Translation(
                        word="",
                        lang=tr_data.lang,
                        lang_code=tr_data.lang_code,
                        sense=sense,
                    )
                if tr_data.lang_code == "":
                    tr_data.lang_code = child.template_parameters.get(1, "")
                if tr_data.lang == "":
                    tr_data.lang = code_to_name(tr_data.lang_code, "zh")
                tr_data.word = clean_node(
                    wxr, None, child.template_parameters.get(2, "")
                )
                tr_data.roman = clean_node(
                    wxr, None, child.template_parameters.get("tr", "")
                )
                tr_data.alt = clean_node(
                    wxr, None, child.template_parameters.get("alt", "")
                )
                tr_data.lit = clean_node(
                    wxr, None, child.template_parameters.get("lit", "")
                )
                for arg_key, arg_value in child.template_parameters.items():
                    if (
                        isinstance(arg_key, int) and arg_key >= 3
                    ) or arg_key == "g":  # template "l" uses the "g" arg
                        for tag_arg in arg_value.split("-"):
                            if tag_arg in TEMPLATE_TAG_ARGS:
                                tag = TEMPLATE_TAG_ARGS[tag_arg]
                                if isinstance(tag, str):
                                    tr_data.tags.append(tag)
                                elif isinstance(tag, list):
                                    tr_data.tags.extend(tag)

            elif template_name == "t-needed":
                # ignore empty translation
                continue
            elif template_name in ("qualifier", "q"):
                raw_tag = clean_node(wxr, None, child)
                tr_data.raw_tags.append(raw_tag.strip("()"))
            else:
                # zh qualifier templates that use template "注释"
                # https://zh.wiktionary.org/wiki/Template:注释
                raw_tag = clean_node(wxr, None, child)
                if raw_tag.startswith("〈") and raw_tag.endswith("〉"):
                    tr_data.raw_tags.append(raw_tag.strip("〈〉"))
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LINK:
            if len(tr_data.word) > 0:
                page_data[-1].translations.append(tr_data.model_copy(deep=True))
                tr_data = Translation(
                    word="",
                    lang=tr_data.lang,
                    lang_code=tr_data.lang_code,
                    sense=sense,
                )
            tr_data.word = clean_node(wxr, None, child)

    if len(tr_data.word) > 0:
        translate_raw_tags(tr_data)
        page_data[-1].translations.append(tr_data.model_copy(deep=True))


def translation_subpage(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
) -> None:
    # https://zh.wiktionary.org/wiki/Template:翻譯-見
    # https://zh.wiktionary.org/wiki/Template:See_translation_subpage

    page_title = wxr.wtp.title
    target_section = None
    if template_node.template_name == "see translation subpage":
        target_section = template_node.template_parameters.get(1)
    page_title = clean_node(
        wxr, None, template_node.template_parameters.get(2, wxr.wtp.title)
    )
    if "#" in page_title:
        page_title = page_title[: page_title.index("#")]

    translation_subpage_title = page_title
    if page_title == wxr.wtp.title:
        translation_subpage_title = f"{page_title}/翻譯"
    subpage = wxr.wtp.get_page(translation_subpage_title)
    if subpage is None:
        return

    root = wxr.wtp.parse(subpage.body)
    target_section_node = (
        find_subpage_section(wxr, root, target_section) or root
    )
    if target_section_node is not None:
        extract_translation(
            wxr, page_data, target_section_node, is_subpage=True
        )


def find_subpage_section(
    wxr: WiktextractContext,
    node: WikiNode | str,
    target_section: str | None = None,
) -> WikiNode | None:
    if not isinstance(node, WikiNode):
        return None
    for level_node in node.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if isinstance(target_section, str) and section_title == target_section:
            return level_node
        if section_title in TRANSLATIONS_TITLES:
            return level_node
    return None
