import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor import Page
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...thesaurus import ThesaurusTerm
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .section_titles import LINKAGE_TITLES, POS_TITLES
from .tags import translate_raw_tags

SENSE_SUBTITLE_PREFIX = "詞義："
IGNORED_SUBTITLES = frozenset(
    [
        "參見",  # see also
        "参见",
        "延伸閱讀",  # further reading
        "延伸阅读",
    ]
)


def parse_section(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    level_node: WikiNode,
) -> list[ThesaurusTerm]:
    data = []
    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        next_level_title = clean_node(wxr, None, next_level_node.largs)
        if next_level_title in IGNORED_SUBTITLES:
            continue
        elif next_level_node.kind == NodeKind.LEVEL3:
            local_pos_name = next_level_title
            english_pos = POS_TITLES.get(local_pos_name, {}).get("pos")
            if english_pos is None:
                logger.warning(
                    f"Unrecognized POS subtitle: {local_pos_name} in page "
                    f"Thesaurus:{entry_word}"
                )
                english_pos = local_pos_name
            data.extend(
                parse_section(
                    wxr,
                    entry_word,
                    lang_code,
                    english_pos,
                    "",
                    "",
                    next_level_node,
                )
            )
        elif next_level_node.kind == NodeKind.LEVEL4:
            sense_text = next_level_title
            sense_text = sense_text.removeprefix(SENSE_SUBTITLE_PREFIX)
            data.extend(
                parse_section(
                    wxr,
                    entry_word,
                    lang_code,
                    pos,
                    sense_text,
                    "",
                    next_level_node,
                )
            )
        elif next_level_node.kind == NodeKind.LEVEL5:
            local_linkage_name = next_level_title
            english_linkage = LINKAGE_TITLES.get(local_linkage_name)
            if english_linkage is None:
                logger.warning(
                    f"Unrecognized linkage subtitle: {local_linkage_name} "
                    f"in page Thesaurus:{entry_word}"
                )
                english_linkage = local_linkage_name
            for node in next_level_node.find_child(
                NodeKind.LIST | NodeKind.TEMPLATE
            ):
                if isinstance(node, TemplateNode):
                    data.extend(
                        process_linkage_template(
                            wxr,
                            entry_word,
                            lang_code,
                            pos,
                            sense,
                            english_linkage,
                            node,
                        )
                    )
                elif node.kind == NodeKind.LIST:
                    data.extend(
                        process_list_node(
                            wxr,
                            entry_word,
                            lang_code,
                            pos,
                            sense,
                            english_linkage,
                            node,
                        )
                    )

    return data


def process_linkage_template(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    template_node: TemplateNode,
) -> list[ThesaurusTerm]:
    if re.fullmatch(r"col\d", template_node.template_name.strip(), re.I):
        return process_col_template(
            wxr, entry_word, lang_code, pos, sense, linkage_type, template_node
        )
    elif template_node.template_name.lower() in (
        "zh-der",
        "zh-syn-list",
        "zh-ant-list",
    ):
        return process_obsolete_zh_der_template(
            wxr, entry_word, lang_code, pos, sense, linkage_type, template_node
        )

    return []


def process_list_node(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    list_node: WikiNode,
) -> list[ThesaurusTerm]:
    term_list = []
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        current_data = []
        raw_tags = []
        for list_child_template in list_item_node.find_child(NodeKind.TEMPLATE):
            if list_child_template.template_name.lower() in (
                "qual",
                "i",
                "qf",
                "qualifier",
            ):
                for (
                    param_value
                ) in list_child_template.template_parameters.values():
                    raw_tags.append(clean_node(wxr, None, param_value))
            elif list_child_template.template_name == "ja-r":
                current_data.append(
                    process_thesaurus_ja_r_template(
                        wxr,
                        entry_word,
                        lang_code,
                        pos,
                        sense,
                        linkage_type,
                        list_child_template,
                    )
                )

        for data in current_data:
            data.raw_tags.extend(raw_tags)
            translate_raw_tags(data)
        term_list.extend(current_data)

    return term_list


def process_col_template(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    template_node: TemplateNode,
) -> list[ThesaurusTerm]:
    # https://zh.wiktionary.org/wiki/Template:Col3
    term_list = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for ui_tag in expanded_template.find_html_recursively("li"):
        current_data = []
        roman = ""
        raw_tags = []
        for span_tag in ui_tag.find_html("span"):
            if span_tag.attrs.get("lang", "").endswith("-Latn"):
                roman = clean_node(wxr, None, span_tag)
            elif "qualifier-content" in span_tag.attrs.get("class", ""):
                raw_tags.append(clean_node(wxr, None, span_tag))
            elif span_tag.attrs.get("lang", "") != "":
                term_text = clean_node(wxr, None, span_tag)
                term_data = ThesaurusTerm(
                    entry_word,
                    lang_code,
                    pos,
                    linkage_type,
                    term_text,
                    sense=sense,
                )
                class_names = span_tag.attrs.get("class", "")
                if class_names == "Hant":
                    term_data.tags.append("Traditional Chinese")
                elif class_names == "Hans":
                    term_data.tags.append("Simplified Chinese")
                current_data.append(term_data)

        for data in current_data:
            data.raw_tags.extend(raw_tags)
            data.roman = roman
            translate_raw_tags(data)
        term_list.extend(current_data)

    return term_list


def process_obsolete_zh_der_template(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    template_node: TemplateNode,
) -> list[ThesaurusTerm]:
    # https://zh.wiktionary.org/wiki/Template:Zh-der
    term_list = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for list_item_node in expanded_template.find_child_recursively(
        NodeKind.LIST_ITEM
    ):
        current_data = []
        roman = ""
        for span_tag in list_item_node.find_html_recursively("span"):
            if "Latn" in span_tag.attrs.get("class", ""):
                roman = clean_node(wxr, None, span_tag)
            elif span_tag.attrs.get("lang", "") != "":
                term_text = clean_node(wxr, None, span_tag)
                if term_text == "／":
                    continue
                current_data.append(
                    ThesaurusTerm(
                        entry_word,
                        lang_code,
                        pos,
                        linkage_type,
                        term_text,
                        sense=sense,
                    )
                )
        for data in current_data:
            data.roman = roman
        term_list.extend(current_data)

    return term_list


def process_thesaurus_ja_r_template(
    wxr: WiktextractContext,
    entry_word: str,
    lang_code: str,
    pos: str,
    sense: str,
    linkage_type: str,
    template_node: TemplateNode,
) -> ThesaurusTerm:
    from .linkage import process_ja_r_template

    linkage_data = process_ja_r_template(wxr, [], template_node, "", "")
    return ThesaurusTerm(
        entry_word,
        lang_code,
        pos,
        linkage_type,
        linkage_data.word,
        sense=sense,
        roman=linkage_data.roman,
    )


def extract_thesaurus_page(
    wxr: WiktextractContext, page: Page
) -> list[ThesaurusTerm]:
    entry = page.title[page.title.find(":") + 1 :]
    wxr.wtp.start_page(page.title)
    root = wxr.wtp.parse(page.body)
    data = []
    for level2_node in root.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        lang_code = name_to_code(lang_name, "zh")
        if lang_code == "":
            logger.warning(
                f"Unrecognized language: {lang_name} in page Thesaurus:{entry}"
            )
        data.extend(
            parse_section(wxr, entry, lang_code, "", "", "", level2_node)
        )
    return data
