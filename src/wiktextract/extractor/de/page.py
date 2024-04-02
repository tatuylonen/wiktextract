import logging
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .example import extract_examples
from .gloss import extract_glosses
from .linkage import extract_linkages
from .models import Sense, WordEntry
from .pronunciation import extract_pronunciation
from .section_titles import LINKAGE_TITLES, POS_SECTIONS
from .translation import extract_translation

# Templates that are used to form panels on pages and that should be ignored in
# various positions
PANEL_TEMPLATES = set()

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = set()

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = {"NoCat"}


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    # Page structure: https://de.wiktionary.org/wiki/Hilfe:Formatvorlage
    # Level 3 headings are used to start POS sections like
    # === {{Wortart|Verb|Deutsch}} ===
    if level_node.kind == NodeKind.LEVEL3:
        process_pos_section(wxr, page_data, base_data, level_node)
    # Level 4 headings were introduced by overriding the default templates.
    # See overrides/de.json for details.
    elif level_node.kind == NodeKind.LEVEL4:
        section_name = clean_node(wxr, None, level_node.largs)
        wxr.wtp.start_subsection(section_name)
        if not len(page_data) > 0:
            wxr.wtp.debug(
                f"Reached section without extracting some page data first: {level_node}",
                sortid="extractor/de/page/parse_section/55",
            )
            return
        if section_name == "Bedeutungen":
            extract_glosses(wxr, page_data[-1], level_node)
        elif wxr.config.capture_pronunciation and section_name == "Aussprache":
            extract_pronunciation(wxr, page_data[-1], level_node)
        elif wxr.config.capture_examples and section_name == "Beispiele":
            extract_examples(wxr, page_data[-1], level_node)
        elif (
            wxr.config.capture_translations and section_name == "Übersetzungen"
        ):
            extract_translation(wxr, page_data[-1], level_node)
        elif wxr.config.capture_linkages and section_name in LINKAGE_TITLES:
            extract_linkages(wxr, page_data[-1], level_node)


FORM_POS = {
    "Konjugierte Form",
    "Deklinierte Form",
    "Dekliniertes Gerundivum",
    "Komparativ",
    "Superlativ",
    "Supinum",
    "Partizip",
    "Partizip I",
    "Partizip II",
    "Erweiterter Infinitiv",
    "Adverbialpartizip",
    "Exzessiv",
    "Gerundium",
}

IGNORE_POS = {"Albanisch", "Pseudopartizip", "Ajami"}


def process_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    pos_arguments = []
    for template_node in level_node.find_content(NodeKind.TEMPLATE):
        if template_node.template_name == "Wortart":
            pos_argument = template_node.template_parameters.get(1, "")
            if pos_argument in IGNORE_POS:
                continue
            if pos_argument in FORM_POS:
                # XXX: Extract form from form pages. Investigate first if this is needed
                # at all or redundant with form tables.
                continue
            if pos_argument in POS_SECTIONS:
                pos_arguments.append(pos_argument)
            else:
                wxr.wtp.debug(
                    f"Unknown Wortart template POS argument: {pos_argument}",
                    sortid="extractor/de/page/process_pos_section/55",
                )
        elif template_node.template_name != "Geschlecht":
            # ignore placeholder gender template "Geschlecht"
            base_data.raw_tags.append(clean_node(wxr, base_data, template_node))

    if len(pos_arguments) == 0:
        return
    for pos_index, pos_argument in enumerate(pos_arguments):
        pos = POS_SECTIONS[pos_argument]["pos"]
        pos_tags = POS_SECTIONS[pos_argument].get("tags", [])
        base_data.tags.extend(pos_tags)
        if pos_index == 0:
            base_data.pos = pos
        else:
            base_data.other_pos.append(pos)
    page_data.append(base_data.model_copy(deep=True))
    wxr.wtp.start_subsection(clean_node(wxr, None, level_node.largs))

    for level_4_node in level_node.find_child(NodeKind.LEVEL4):
        parse_section(wxr, page_data, base_data, level_4_node)

    for non_l4_node in level_node.invert_find_child(NodeKind.LEVEL4):
        if (
            isinstance(non_l4_node, WikiNode)
            and non_l4_node.kind == NodeKind.TEMPLATE
            and "Übersicht" in non_l4_node.template_name
        ):
            # XXX: de: Extract form table templates
            pass
        elif (
            isinstance(non_l4_node, WikiNode)
            and non_l4_node.kind == NodeKind.TABLE
            and "inflection-table" in non_l4_node.attrs.get("class", "")
        ):
            # XXX: de: Extract html form table
            pass
        elif (
            isinstance(non_l4_node, WikiNode)
            and non_l4_node.kind == NodeKind.LINK
            and len(non_l4_node.largs) > 0
            and len(non_l4_node.largs[0]) > 0
            and "Kategorie" in non_l4_node.largs[0][0]
        ):
            # XXX Process categories
            pass
        else:
            wxr.wtp.debug(
                f"Unexpected node in pos section: {non_l4_node}",
                sortid="extractor/de/page/process_pos_section/41",
            )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    if wxr.config.verbose:
        logging.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        for subtitle_template in level2_node.find_content(NodeKind.TEMPLATE):
            # The language sections are marked with
            # == <title> ({{Sprache|<lang>}}) ==
            # where <title> is the title of the page and <lang> is the
            # German name of the language of the section.
            if subtitle_template.template_name == "Sprache":
                lang_name = subtitle_template.template_parameters.get(1, "")
                lang_code = name_to_code(lang_name, "de")
                if lang_code == "":
                    wxr.wtp.warning(
                        f"Unknown language: {lang_name}",
                        sortid="extractor/de/page/parse_page/76",
                    )
                if (
                    wxr.config.capture_language_codes is not None
                    and lang_code not in wxr.config.capture_language_codes
                ):
                    continue
                base_data = WordEntry(
                    lang=lang_name, lang_code=lang_code, word=page_title
                )
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    parse_section(wxr, page_data, base_data, level3_node)
                for template_node in level2_node.find_child(NodeKind.TEMPLATE):
                    if template_node.template_name == "Ähnlichkeiten Umschrift":
                        process_umschrift_template(
                            wxr, page_data, base_data, template_node
                        )

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [d.model_dump(exclude_defaults=True) for d in page_data]


def process_umschrift_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Ähnlichkeiten_Umschrift
    # soft-redirect template, similar to en edition's "zh-see"
    data = base_data.model_copy(deep=True)
    data.pos = "soft-redirect"
    for key, value in template_node.template_parameters.items():
        if isinstance(key, int):
            redirect_page = clean_node(wxr, None, value)
            link_arg = template_node.template_parameters.get(f"link{key}", "")
            link_text = clean_node(wxr, None, link_arg)
            if len(link_text) > 0:
                redirect_page = link_text
            if len(redirect_page) > 0:
                data.redirects.append(redirect_page)
    if len(data.redirects) > 0:
        page_data.append(data)
