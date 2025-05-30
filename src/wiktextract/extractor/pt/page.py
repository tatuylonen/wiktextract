from typing import Any

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .inflection import extract_conjugation_section, extract_degree_section
from .linkage import (
    extract_abbr_section,
    extract_expression_section,
    extract_linkage_section,
    extract_phraseology_section,
)
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .pronunciation import extract_pronunciation_section
from .section_titles import LINKAGE_SECTIONS, LINKAGE_TAGS, POS_DATA
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    cats = {}
    title_text = clean_node(wxr, cats, level_node.largs).strip(
        "⁰¹²³⁴⁵⁶⁷⁸⁹0123456789: \n"
    )
    if title_text.lower() in POS_DATA:
        extract_pos_section(
            wxr,
            page_data,
            base_data,
            level_node,
            title_text,
            cats.get("categories", []),
        )
        if len(page_data[-1].senses) == 0 and title_text == "Sigla":
            page_data.pop()
            extract_abbr_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
    elif title_text in ["Tradução", "Traduções", "Cognatos", "Descendentes"]:
        extract_translation_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            title_text,
        )
    elif title_text == "Expressões":
        extract_expression_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text.lower() in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_SECTIONS[title_text.lower()],
            "",
            0,
            "",
            LINKAGE_TAGS.get(title_text.lower(), []),
        )
    elif title_text == "Etimologia":
        extract_etymology_section(wxr, page_data, level_node)
    elif title_text == "Pronúncia":
        extract_pronunciation_section(wxr, page_data, level_node)
    elif title_text == "Fraseologia":
        extract_phraseology_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif title_text.startswith(("Nota", "Uso")):
        extract_note_section(wxr, page_data, level_node)
    elif title_text == "Conjugação":
        extract_conjugation_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif title_text == "Graus":
        extract_degree_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif title_text.lower() not in [
        "ver também",
        "ligação externa",
        "ligações externas",
        "ligação extena",
        "referências",
        "referência",
        "no wikcionário",
        "na wikipédia",
        "no wikiquote",
        "no wikispecies",
        "no wikisaurus",
        "no commons",
        "no wikimedia commons",
        "na internet",
        "galeria",
        "galeria de imagens",
    ]:
        wxr.wtp.debug(f"unknown section: {title_text}")

    if title_text.lower() not in POS_DATA:
        save_section_cats(
            cats.get("categories", []), page_data, level_node, True
        )
    cats = {}
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(wxr, cats, link_node)
    save_section_cats(cats.get("categories", []), page_data, level_node, False)

    if title_text.lower() not in ["pronúncia", "ver também"]:
        for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level)


def save_section_cats(
    cats: list[str],
    page_data: list[WordEntry],
    level_node: LevelNode,
    from_title: bool,
) -> None:
    if not from_title or (from_title and level_node.kind == NodeKind.LEVEL2):
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(cats)
    elif len(page_data) > 0:
        page_data[-1].categories.extend(cats)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://pt.wiktionary.org/wiki/Wikcionário:Livro_de_estilo
    if "/traduções" in page_title or page_title.startswith("Wikisaurus:"):
        # skip translation and thesaurus pages
        return []
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level1_node in tree.find_child(NodeKind.LEVEL1):
        lang_cats = {}
        lang_name = clean_node(wxr, lang_cats, level1_node.largs)
        if lang_name == "":
            lang_name = "unknown"
        lang_code = "unknown"
        for lang_template in level1_node.find_content(NodeKind.TEMPLATE):
            lang_code = lang_template.template_name.strip("-")
            if lang_code == "":  # template "--"
                lang_code = "unknown"
            break
        if (
            wxr.config.capture_language_codes is not None
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
            categories=lang_cats.get("categories", []),
        )
        for next_level_node in level1_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]


def extract_note_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
) -> None:
    notes = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        note = clean_node(
            wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
        )
        if note != "":
            notes.append(note)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.notes.extend(notes)
