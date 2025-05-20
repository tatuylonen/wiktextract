import re
from typing import Any

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...config import POSSubtitleData
from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .etymology import extract_etymology
from .gloss import extract_gloss, process_meaning_template
from .inflection import (
    extract_прил_ru_comparative_forms,
    parse_html_forms_table,
    parse_wikitext_forms_table,
)
from .linkage import (
    extract_alt_form_section,
    extract_linkage_section,
    extract_phrase_section,
)
from .models import AltForm, Form, Sense, Sound, WordEntry
from .pronunciation import (
    extract_homophone_section,
    extract_pronunciation_section,
)
from .section_titles import (
    ALT_FORM_SECTIONS,
    LINKAGE_TITLES,
    POS_TEMPLATE_NAMES,
    POS_TITLES,
)
from .tags import MORPHOLOGICAL_TEMPLATE_TAGS
from .translation import extract_translations


def process_semantic_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for template_node in list_node.find_child_recursively(
            NodeKind.TEMPLATE
        ):
            if template_node.template_name == "значение":
                sense = process_meaning_template(
                    wxr, None, page_data[-1], template_node
                )
                if len(sense.glosses) > 0:
                    page_data[-1].senses.append(sense)


MORPH_TEMPLATE_ARGS = {
    "p": "prefix",
    "prefix": "prefix",
    "i": "interfix",
    "interfix": "interfix",
    "in": "infix",
    "infix": "infix",
    "s": "suffix",
    "suffix": "suffix",
    "t": "transfix",
    "transfix": "transfix",
    "po": "suffix",
    "postfix": "suffix",
    "c": "circumfix",
    "confix": "circumfix",
    "circumfix": "circumfix",
    "r": "root",
    "e": "suffix",
    "ending": "suffix",
}


def get_pos_from_template(
    wxr: WiktextractContext, template_node: TemplateNode
) -> POSSubtitleData | None:
    # Search for POS in template names
    template_name = template_node.template_name.lower()
    if template_name == "morph":
        # https://ru.wiktionary.org/wiki/Шаблон:morph
        pos_type = template_node.template_parameters.get("тип", "")
        if pos_type in MORPH_TEMPLATE_ARGS:
            return {
                "pos": MORPH_TEMPLATE_ARGS[pos_type],
                "tags": ["morpheme"],
            }
    elif (
        template_name in {"заголовок", "з"}
        and 1 in template_node.template_parameters
    ):
        pos_text = clean_node(
            wxr, None, template_node.template_parameters[1]
        ).strip("()")
        if len(pos_text) == 0:
            return
        pos_text = pos_text.split()[0]
        if pos_text in POS_TITLES:
            return POS_TITLES[pos_text]

    if template_name.startswith("прил ru"):
        pos_arg = clean_node(
            wxr, None, template_node.template_parameters.get("часть речи", "")
        ).lower()
        if pos_arg != "":
            for pos_string in POS_TITLES.keys():
                if pos_string in pos_arg:
                    return POS_TITLES[pos_string]
        else:
            return {"pos": "adj"}

    for part in template_name.split(maxsplit=2):
        for subpart in part.split("-", maxsplit=2):
            if subpart in POS_TEMPLATE_NAMES:
                return POS_TEMPLATE_NAMES[subpart]


def get_pos(
    wxr: WiktextractContext, level_node: WikiNode
) -> POSSubtitleData | None:
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        pos_data = get_pos_from_template(wxr, template_node)
        if pos_data is not None:
            return pos_data
    # POS text could also in level node content
    for template_node in level_node.find_content(NodeKind.TEMPLATE):
        pos_data = get_pos_from_template(wxr, template_node)
        if pos_data is not None:
            return pos_data

    # Search for POS in section text
    text = clean_node(
        wxr, None, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
    )
    for pos_string in POS_TITLES.keys():
        if pos_string in text.lower():
            return POS_TITLES[pos_string]


def extract_morphological_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: WikiNode
) -> None:
    pos_data = get_pos(wxr, level_node)
    if pos_data is not None:
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))
    for child_node in level_node.find_child(NodeKind.TEMPLATE):
        expanded_template = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(child_node), expand_all=True
        )
        clean_node(wxr, page_data[-1], expanded_template)  # add category links
        if child_node.template_name.startswith(
            (
                "прил ru",
                "прил-ru",
                "сущ ",
                "сущ-ru",
                "гл ",
                "мест ru ",
                "числ ru ",
                "числ-",
                "прич ru ",
                "Фам ru ",
                "падежи ",
            )
        ):
            for table_node in expanded_template.find_child_recursively(
                NodeKind.TABLE
            ):
                parse_wikitext_forms_table(wxr, page_data[-1], table_node)
            for table_tag in expanded_template.find_html("table"):
                parse_html_forms_table(wxr, page_data[-1], table_tag)
            page_data[-1].hyphenation = clean_node(
                wxr, None, child_node.template_parameters.get("слоги", "")
            )

        if child_node.template_name.startswith("прил ru"):
            extract_прил_ru_comparative_forms(
                wxr, page_data[-1], expanded_template
            )

        for node in expanded_template.children:
            node_text = clean_node(wxr, page_data[-1], node)
            for text in node_text.split(","):
                text = text.strip()
                if text in MORPHOLOGICAL_TEMPLATE_TAGS:
                    tr_tag = MORPHOLOGICAL_TEMPLATE_TAGS[text]
                    if isinstance(tr_tag, str):
                        page_data[-1].tags.append(tr_tag)
                    elif isinstance(tr_tag, list):
                        page_data[-1].tags.extend(tr_tag)


def parse_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: WikiNode
) -> None:
    section_title = clean_node(wxr, None, level_node.largs).lower()
    wxr.wtp.start_subsection(section_title)
    if section_title in [
        # Morphological and syntactic properties
        "морфологические и синтаксические свойства",
        # Type and syntactic properties of the word combination
        "тип и синтаксические свойства сочетания",
        "тип и свойства сочетания",
    ]:
        extract_morphological_section(wxr, page_data, level_node)
    elif section_title in POS_TITLES:
        pos_data = POS_TITLES[section_title]
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))
        extract_gloss(wxr, page_data[-1], level_node)
    elif section_title == "произношение" and wxr.config.capture_pronunciation:
        extract_pronunciation_section(wxr, page_data[-1], level_node)
    elif section_title == "семантические свойства":  # Semantic properties
        process_semantic_section(wxr, page_data, level_node)
    elif section_title in [
        "значение",
        "значения",
        "как самостоятельный глагол",
        "в значении вспомогательного глагола или связки",
    ]:
        extract_gloss(wxr, page_data[-1], level_node)
    elif section_title == "этимология" and wxr.config.capture_etymologies:
        extract_etymology(wxr, page_data[-1], level_node)
    elif (
        section_title
        in [
            "фразеологизмы и устойчивые сочетания",
            "типичные сочетания",
            "фразеологизмы",
            "пословицы и поговорки",
        ]
        and wxr.config.capture_linkages
    ):
        extract_phrase_section(wxr, page_data[-1], level_node, section_title)
    elif (
        section_title in ["перевод", "иноязычные аналоги"]
        and wxr.config.capture_translations
    ):
        extract_translations(wxr, page_data[-1], level_node)
    elif section_title in LINKAGE_TITLES and wxr.config.capture_linkages:
        extract_linkage_section(
            wxr, page_data[-1], LINKAGE_TITLES[section_title], level_node
        )
    elif section_title == "библиография":
        pass
    elif section_title in ["латиница (latinça)", "латиница (latinca)"]:
        parse_roman_section(wxr, page_data[-1], level_node)
    elif section_title == "прочее":
        pass
    elif section_title == "омофоны" and wxr.config.capture_pronunciation:
        extract_homophone_section(wxr, page_data[-1], level_node)
    elif section_title in ALT_FORM_SECTIONS:
        extract_alt_form_section(
            wxr, page_data[-1], level_node, ALT_FORM_SECTIONS[section_title]
        )
    else:
        wxr.wtp.debug(
            f"Unprocessed section {section_title}",
            sortid="wixtextract/extractor/ru/page/parse_section/66",
        )

    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, next_level_node)

    extract_section_end_templates(wxr, page_data[-1], level_node)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # Help site describing page structure:
    # https://ru.wiktionary.org/wiki/Викисловарь:Правила_оформления_статей

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")
    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []

    for level1_node in tree.find_child(NodeKind.LEVEL1):
        lang_code = ""
        for subtitle_template in level1_node.find_content(NodeKind.TEMPLATE):
            lang_code = subtitle_template.template_name.strip(" -")
            break
        if lang_code == "":
            lang_code = "unknown"
        if (
            wxr.config.capture_language_codes is not None
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        categories = {"categories": []}
        lang_name = clean_node(wxr, categories, level1_node.largs)
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            lang=lang_name,
            lang_code=lang_code,
            word=page_title,
            pos="unknown",
        )
        base_data.categories.extend(categories["categories"])
        extract_section_end_templates(wxr, base_data, level1_node)
        pos_data = get_pos(wxr, level1_node)
        if pos_data is not None:
            base_data.pos = pos_data["pos"]
            base_data.tags.extend(pos_data.get("tags", []))

        for level2_node in level1_node.find_child(NodeKind.LEVEL2):
            if base_data.pos == "unknown":
                pos_data = get_pos(wxr, level2_node)
                if pos_data is not None:
                    base_data.pos = pos_data["pos"]
                    base_data.tags.extend(pos_data.get("tags", []))
            page_data.append(base_data.model_copy(deep=True))
            extract_level2_node_contents(wxr, page_data[-1], level2_node)
            has_level3 = False
            for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                parse_section(wxr, page_data, level3_node)
                has_level3 = True
            if page_data[-1] == base_data or not has_level3:
                page_data.pop()
            extract_low_quality_page(wxr, page_data, base_data, level2_node)

        for any_level_index, any_level_node in enumerate(
            level1_node.find_child(LEVEL_KIND_FLAGS & ~NodeKind.LEVEL2)
        ):
            if any_level_index == 0 and (
                len(page_data) == 0
                or page_data[-1].lang_code != base_data.lang_code
            ):
                page_data.append(base_data.model_copy(deep=True))
            parse_section(wxr, page_data, any_level_node)

        if len(page_data) > 0 and page_data[-1] == base_data:
            page_data.pop()
        extract_low_quality_page(wxr, page_data, base_data, level1_node)

    for d in page_data:
        if len(d.senses) == 0:
            d.senses.append(Sense(tags=["no-gloss"]))
    return [d.model_dump(exclude_defaults=True) for d in page_data]


def extract_low_quality_page(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    for node in level_node.invert_find_child(LEVEL_KIND_FLAGS):
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "Форма-"
        ):
            process_form_template(wxr, page_data, base_data, node)
        elif isinstance(node, WikiNode):
            for template_node in node.find_child_recursively(NodeKind.TEMPLATE):
                if template_node.template_name.startswith("Форма-"):
                    process_form_template(
                        wxr, page_data, base_data, template_node
                    )


def process_form_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:Форма-сущ
    # Шаблон:Форма-гл, "Шаблон:форма-гл en"
    pos_data = get_pos_from_template(wxr, template_node)
    if pos_data is not None:
        base_data.pos = pos_data["pos"]
        base_data.tags.extend(pos_data.get("tags", []))

    form_of = clean_node(
        wxr,
        None,
        template_node.template_parameters.get(
            "база", template_node.template_parameters.get(1, "")
        ),
    )
    ipa = clean_node(
        wxr, None, template_node.template_parameters.get("МФА", "")
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    current_data = base_data.model_copy(deep=True)
    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        gloss_text = clean_node(wxr, None, list_item.children)
        if len(gloss_text) > 0:
            sense = Sense(glosses=[gloss_text])
            if len(form_of) > 0:
                sense.form_of.append(AltForm(word=form_of))
                sense.tags.append("form-of")
            current_data.senses.append(sense)

    if len(ipa) > 0:
        current_data.sounds.append(Sound(ipa=ipa))
    if len(current_data.senses) > 0 or len(current_data.sounds) > 0:
        clean_node(wxr, current_data, template_node)
        page_data.append(current_data)


def parse_roman_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    for link_node in level_node.find_child(NodeKind.LINK):
        form_text = clean_node(wxr, None, link_node)
        if form_text != "":
            form = Form(form=form_text, tags=["romanization"])
            word_entry.forms.append(form)


def extract_section_end_templates(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    # category link templates
    # https://ru.wiktionary.org/wiki/Категория:Викисловарь:Шаблоны_категоризации
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in {
            "-ание",
            "-атель",
            "-ация",
            "-ение",
            "-ка",
            "длина слова",
            "Категория",
            "Омонимы",
            "forms",
            "multilang",
        }:
            clean_node(wxr, word_entry, template_node)
        elif template_node.template_name == "zh-forms":
            extract_zh_forms_template(wxr, word_entry, template_node)


def extract_zh_forms_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:zh-forms
    # https://ru.wiktionary.org/wiki/Модуль:zh-forms
    # similar to en and zh edition template
    for p_name, p_value in template_node.template_parameters.items():
        if not isinstance(p_name, str):
            continue
        if re.fullmatch(r"s\d*", p_name):
            form_data = Form(
                form=clean_node(wxr, None, p_value), tags=["Simplified Chinese"]
            )
            if form_data.form not in ["", wxr.wtp.title]:
                base_data.forms.append(form_data)
        elif re.fullmatch(r"t\d*", p_name):
            form_data = Form(
                form=clean_node(wxr, None, p_value),
                tags=["Traditional Chinese"],
            )
            if form_data.form not in ["", wxr.wtp.title]:
                base_data.forms.append(form_data)
        elif p_name == "lit":
            base_data.literal_meaning = clean_node(wxr, None, p_value)


def extract_level2_node_contents(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for t_node in level_node.find_content(NodeKind.TEMPLATE):
        if t_node.template_name in ["заголовок", "з"]:
            # https://ru.wiktionary.org/wiki/Шаблон:з
            stressed_form = clean_node(
                wxr, None, t_node.template_parameters.get("ударение", "")
            )
            if "(" in stressed_form:
                stressed_form = stressed_form[
                    : stressed_form.index("(")
                ].strip()
            if stressed_form not in ["", wxr.wtp.title]:
                word_entry.forms.append(
                    Form(form=stressed_form, tags=["stressed"])
                )
