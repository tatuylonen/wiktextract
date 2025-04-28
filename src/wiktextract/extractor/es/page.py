from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .conjugation import extract_conjugation_section
from .etymology import extract_etymology_section
from .linkage import (
    extract_additional_information_section,
    extract_alt_form_section,
    extract_linkage_section,
)
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .pronunciation import process_pron_graf_template
from .section_titles import (
    IGNORED_TITLES,
    LINKAGE_TITLES,
    POS_TITLES,
    TRANSLATIONS_TITLES,
)
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    """
    Parses indidividual sibling sections of an entry,
    e.g. https://es.wiktionary.org/wiki/amor:

    === Etimología ===
    === {{sustantivo masculino|es}} ===
    === Locuciones ===
    """

    categories = {}
    section_title = clean_node(wxr, categories, level_node.largs)
    original_section_title = section_title
    section_title = section_title.lower()
    wxr.wtp.start_subsection(original_section_title)

    pos_template_name = ""
    for level_node_template in level_node.find_content(NodeKind.TEMPLATE):
        pos_template_name = level_node_template.template_name
        break

    if section_title in IGNORED_TITLES:
        pass
    elif pos_template_name in POS_TITLES or section_title in POS_TITLES:
        pos_data = POS_TITLES.get(
            pos_template_name, POS_TITLES.get(section_title)
        )
        pos_type = pos_data["pos"]
        page_data.append(base_data.model_copy(deep=True))
        page_data[-1].pos = pos_type
        page_data[-1].pos_title = original_section_title
        page_data[-1].tags.extend(pos_data.get("tags", []))
        page_data[-1].categories.extend(categories.get("categories", []))
        extract_pos_section(wxr, page_data[-1], level_node)
        if len(page_data[-1].senses) == 0 and "form-of" in page_data[-1].tags:
            page_data.pop()
    elif (
        section_title.startswith("etimología")
        and wxr.config.capture_etymologies
    ):
        if level_node.contain_node(LEVEL_KIND_FLAGS):
            base_data = base_data.model_copy(deep=True)
        extract_etymology_section(wxr, base_data, level_node)
    elif (
        section_title in TRANSLATIONS_TITLES and wxr.config.capture_translations
    ):
        if len(page_data) == 0:
            page_data.append(base_data.model_copy(deep=True))
        extract_translation_section(wxr, page_data, level_node)
    elif section_title in LINKAGE_TITLES:
        if len(page_data) == 0:
            page_data.append(base_data.model_copy(deep=True))
        extract_linkage_section(
            wxr, page_data, level_node, LINKAGE_TITLES[section_title]
        )
    elif section_title == "conjugación":
        if len(page_data) == 0:
            page_data.append(base_data.model_copy(deep=True))
        extract_conjugation_section(wxr, page_data, level_node)
    elif section_title == "formas alternativas":
        extract_alt_form_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif section_title == "información adicional":
        extract_additional_information_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    else:
        wxr.wtp.debug(
            f"Unprocessed section: {section_title}",
            sortid="extractor/es/page/parse_section/48",
        )

    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, link_node
        )

    for next_level_node in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level_node)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, any]]:
    # style guide
    # https://es.wiktionary.org/wiki/Wikcionario:Guía_de_estilo
    # entry layout
    # https://es.wiktionary.org/wiki/Wikcionario:Estructura
    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        categories = {}
        lang_code = "unknown"
        lang_name = "unknown"
        section_title = clean_node(wxr, None, level2_node.largs)
        if section_title.lower() == "referencias y notas":
            continue
        for subtitle_template in level2_node.find_content(NodeKind.TEMPLATE):
            # https://es.wiktionary.org/wiki/Plantilla:lengua
            # https://es.wiktionary.org/wiki/Apéndice:Códigos_de_idioma
            if subtitle_template.template_name == "lengua":
                lang_code = subtitle_template.template_parameters.get(1).lower()
                lang_name = clean_node(wxr, categories, subtitle_template)
                break
        if (
            wxr.config.capture_language_codes is not None
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            lang=lang_name,
            lang_code=lang_code,
            word=page_title,
            pos="unknown",
            categories=categories.get("categories", []),
        )
        for node in level2_node.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
            if (
                isinstance(node, TemplateNode)
                and node.template_name == "pron-graf"
            ):
                process_pron_graf_template(wxr, base_data, node)
            elif node.kind == NodeKind.LINK:
                clean_node(wxr, base_data, node)

        for next_level_node in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [d.model_dump(exclude_defaults=True) for d in page_data]
