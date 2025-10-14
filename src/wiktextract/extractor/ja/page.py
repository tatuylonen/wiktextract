import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .conjugation import extract_conjugation_section
from .etymology import extract_etymology_section
from .linkage import extract_alt_form_section, extract_linkage_section
from .models import Sense, WordEntry
from .pos import extract_note_section, parse_pos_section
from .section_titles import LINKAGES, POS_DATA
from .sound import extract_homophone_section, extract_sound_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_texts = re.sub(
        r"[\s\d]+$", "", clean_node(wxr, None, level_node.largs)
    )
    for title_text in re.split(r"：|:|・", title_texts):
        if title_text in POS_DATA:
            pre_len = len(page_data)
            parse_pos_section(wxr, page_data, base_data, level_node, title_text)
            if (
                len(page_data) == pre_len
                and title_text in LINKAGES
                and pre_len > 0
            ):
                extract_linkage_section(
                    wxr, page_data[-1], level_node, LINKAGES[title_text]
                )
            break
        elif (
            title_text in ["語源", "由来", "字源", "出典", "語誌"]
            and wxr.config.capture_etymologies
        ):
            extract_etymology_section(wxr, page_data, base_data, level_node)
            break
        elif (
            title_text.startswith(("発音", "音価"))
            and wxr.config.capture_pronunciation
        ):
            extract_sound_section(wxr, page_data, base_data, level_node)
            break
        elif title_text in ["翻訳", "訳語"] and wxr.config.capture_translations:
            extract_translation_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
            break
        elif title_text in LINKAGES and wxr.config.capture_linkages:
            extract_linkage_section(
                wxr,
                page_data[-1]
                if len(page_data) > 0
                and page_data[-1].lang_code == base_data.lang_code
                else base_data,
                level_node,
                LINKAGES[title_text],
            )
            break
        elif (
            title_text in ["活用", "サ変動詞"]
            and wxr.config.capture_inflections
        ):
            extract_conjugation_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
            break
        elif title_text in [
            "異表記",
            "別表記",
            "代替表記",
            "異形",
            "表記揺れ",
        ]:  # "異表記・別形", Template:alter
            extract_alt_form_section(
                wxr,
                page_data[-1]
                if len(page_data) > 0
                and page_data[-1].lang_code == base_data.lang_code
                else base_data,
                level_node,
            )
            break
        elif title_text in [
            "用法",
            "注意点",
            "留意点",
            "注意",
            "備考",
            "表記",
            "補足",
            "語法",
        ]:
            extract_note_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
            break
        elif title_text == "同音異義語":
            extract_homophone_section(wxr, page_data, base_data, level_node)
            break
    else:
        if title_text not in [
            "脚注",
            "参照",
            "参考文献",
            "参考",
            "同音の漢字",
            "参考辞書",
            "外部リンク",
        ]:
            wxr.wtp.debug(
                f"Unknown section: {title_text}",
                sortid="extractor/ja/page/parse_section/93",
            )

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.endswith("-cat"):
            clean_node(
                wxr, page_data[-1] if len(page_data) > 0 else base_data, t_node
            )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://ja.wiktionary.org/wiki/Wiktionary:スタイルマニュアル
    if page_title.startswith(
        ("Appendix:", "シソーラス:")
    ) or page_title.endswith("(活用)"):
        return []
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        if lang_name == "":
            lang_name = "unknown"
            lang_code = "unknown"
        else:
            lang_code = name_to_code(lang_name, "ja")
        if lang_code == "":
            for template in level2_node.find_content(NodeKind.TEMPLATE):
                if template.template_name == "L":
                    lang_code = template.template_parameters.get(1, "")
                elif re.fullmatch(r"[a-z-]+", template.template_name):
                    lang_code = template.template_name
        if lang_code == "":
            lang_code = "unknown"
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        for link_node in level2_node.find_child(NodeKind.LINK):
            clean_node(wxr, base_data, link_node)
        for t_node in level2_node.find_child(NodeKind.TEMPLATE):
            if t_node.template_name.endswith("-cat"):
                clean_node(wxr, base_data, t_node)
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]
