from mediawiki_langcodes import code_to_name, name_to_code
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
from .section_titles import TRANSLATIONS_TITLES
from .tags import TEMPLATE_TAG_ARGS, translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    sense: str = "",
    is_subpage: bool = False,
) -> None:
    for child in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LIST):
        if isinstance(child, TemplateNode):
            template_name = child.template_name.lower()
            if (
                template_name in ("trans-top", "翻譯-頂", "trans-top-also")
                and 1 in child.template_parameters
                and not (sense != "" and is_subpage)
            ):
                sense = clean_node(wxr, None, child.template_parameters.get(1))
            elif template_name == "see translation subpage" and not is_subpage:
                extract_see_trans_subpage_template(wxr, word_entry, child)
            elif (
                template_name in ("trans-see", "翻译-见", "翻譯-見")
                and not is_subpage
            ):
                extract_trans_see_template(wxr, word_entry, child)
            elif template_name == "multitrans":
                wikitext = "".join(
                    wxr.wtp.node_to_wikitext(c)
                    for c in child.template_parameters.get("data", [])
                )
                multitrans = wxr.wtp.parse(wikitext)
                extract_translation_section(wxr, word_entry, multitrans, sense)
        else:
            for list_item in child.find_child_recursively(NodeKind.LIST_ITEM):
                process_translation_list_item(wxr, word_entry, list_item, sense)


def process_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
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
                    word_entry.translations.append(
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
                word_entry.translations.append(tr_data.model_copy(deep=True))
                tr_data = Translation(
                    word="",
                    lang=tr_data.lang,
                    lang_code=tr_data.lang_code,
                    sense=sense,
                )
            tr_data.word = clean_node(wxr, None, child)

    if len(tr_data.word) > 0:
        translate_raw_tags(tr_data)
        word_entry.translations.append(tr_data.model_copy(deep=True))


def extract_trans_see_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://zh.wiktionary.org/wiki/Template:翻譯-見
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
        target_node = find_subpage_section(wxr, root, TRANSLATIONS_TITLES)
        if target_node is not None:
            extract_translation_section(
                wxr, word_entry, target_node, sense=sense, is_subpage=True
            )


def extract_see_trans_subpage_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://zh.wiktionary.org/wiki/Template:See_translation_subpage
    target_pos = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if 2 in t_node.template_parameters:
        subpage_title = clean_node(
            wxr, None, t_node.template_parameters.get(2, "")
        )
        if "#" in subpage_title:
            subpage_title = subpage_title[: subpage_title.index("#")]
    else:
        subpage_title = f"{wxr.wtp.title}/翻譯"

    page = wxr.wtp.get_page(subpage_title)
    if page is None:
        return
    root = wxr.wtp.parse(page.body)
    target_section = find_subpage_section(wxr, root, target_pos)
    if target_section is not None:
        new_target_section = find_subpage_section(
            wxr, target_section, TRANSLATIONS_TITLES
        )
        if new_target_section is not None:
            target_section = new_target_section
    if target_section is not None:
        extract_translation_section(
            wxr, word_entry, target_section, is_subpage=True
        )


def find_subpage_section(
    wxr: WiktextractContext, root: WikiNode, target_sections: set[str]
) -> WikiNode | None:
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title in target_sections:
            return level_node
    return None
