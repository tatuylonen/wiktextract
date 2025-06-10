from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ...wxr_logging import logger
from .etymology import extract_etymology_section
from .example import extract_examples
from .form import extracrt_form_section, extract_transcription_section
from .gloss import extract_glosses
from .inflection import extract_inf_table_template, process_noun_table
from .linkage import extract_descendant_section, extract_linkages
from .models import AltForm, Sense, WordEntry
from .pronunciation import extract_pronunciation_section
from .section_titles import FORM_TITLES, LINKAGE_TITLES, POS_SECTIONS
from .tags import translate_raw_tags
from .translation import extract_translation


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    # Page structure: https://de.wiktionary.org/wiki/Hilfe:Formatvorlage
    # Level 3 headings are used to start POS sections like
    # === {{Wortart|Verb|Deutsch}} ===
    # title templates:
    # https://de.wiktionary.org/wiki/Kategorie:Wiktionary:Textbausteine
    if level_node.kind == NodeKind.LEVEL3:
        process_pos_section(wxr, page_data, base_data, level_node)
    # Level 4 headings were introduced by overriding the default templates.
    # See overrides/de.json for details.
    elif level_node.kind == NodeKind.LEVEL4:
        section_name = clean_node(wxr, None, level_node.largs)
        wxr.wtp.start_subsection(section_name)
        if section_name in ("Bedeutungen", "Grammatische Merkmale"):
            extract_glosses(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif wxr.config.capture_pronunciation and section_name == "Aussprache":
            extract_pronunciation_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif wxr.config.capture_examples and section_name == "Beispiele":
            extract_examples(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif (
            wxr.config.capture_translations and section_name == "Übersetzungen"
        ):
            extract_translation(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif wxr.config.capture_linkages and section_name in LINKAGE_TITLES:
            extract_linkages(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
                LINKAGE_TITLES[section_name],
            )
        elif wxr.config.capture_etymologies and section_name == "Herkunft":
            extract_etymology_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif section_name in FORM_TITLES:
            extracrt_form_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
                FORM_TITLES[section_name],
            )
        elif section_name == "Worttrennung":
            extract_hyphenation_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif section_name == "Anmerkung":
            extract_note_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif section_name == "Umschrift":
            extract_transcription_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif section_name == "Entlehnungen":
            extract_descendant_section(
                wxr,
                page_data[-1] if len(page_data) > 0 else base_data,
                level_node,
            )
        elif section_name not in [
            "Referenzen",
            "Ähnliche Wörter",
            "Bekannte Namensträger",
        ]:
            wxr.wtp.debug(
                f"Unknown section: {section_name}",
                sortid="extractor/de/page/parse_section/107",
            )


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

GENDER_TEMPLATES = {
    "n": ["neuter"],
    "m": ["masculine"],
    "f": ["feminine"],
    "mn.": ["masculine", "neuter"],
    "nm": ["masculine", "neuter"],
    "nf": ["neuter", "feminine"],
    "fn": ["neuter", "feminine"],
    "fm": ["feminine", "masculine"],
    "mf": ["feminine", "masculine"],
    "u": ["common-gender"],
    "un": ["common-gender", "neuter"],
}


def process_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    pos_data_list = []
    pos_title = ""
    for template_node in level_node.find_content(NodeKind.TEMPLATE):
        if template_node.template_name == "Wortart":
            pos_argument = template_node.template_parameters.get(1, "").strip()
            if pos_title == "":
                pos_title = pos_argument
            if pos_argument in IGNORE_POS:
                continue
            elif pos_argument in FORM_POS:
                pos_data_list.append({"pos": "unknown", "tags": ["form-of"]})
            elif pos_argument in POS_SECTIONS:
                pos_data_list.append(POS_SECTIONS[pos_argument])
            elif pos_argument == "Gebundenes Lexem":
                if wxr.wtp.title.startswith("-") and wxr.wtp.title.endswith(
                    "-"
                ):
                    pos_data_list.append({"pos": "infix", "tags": ["morpheme"]})
                elif wxr.wtp.title.endswith("-"):
                    pos_data_list.append(
                        {"pos": "prefix", "tags": ["morpheme"]}
                    )
                elif wxr.wtp.title.startswith("-"):
                    pos_data_list.append(
                        {"pos": "suffix", "tags": ["morpheme"]}
                    )
            else:
                wxr.wtp.debug(
                    f"Unknown Wortart template POS argument: {pos_argument}",
                    sortid="extractor/de/page/process_pos_section/55",
                )
                pos_data_list.append({"pos": "unknown"})

    if len(pos_data_list) == 0:
        return
    page_data.append(base_data.model_copy(deep=True))
    for pos_index, pos_data in enumerate(pos_data_list):
        pos = pos_data["pos"]
        for tag in pos_data.get("tags", []):
            if tag not in page_data[-1].tags:
                page_data[-1].tags.append(tag)
        if pos_index == 0:
            page_data[-1].pos = pos
            page_data[-1].pos_title = pos_title
        elif pos != page_data[-1].pos and pos not in page_data[-1].other_pos:
            page_data[-1].other_pos.append(pos)

    for node in level_node.find_content(NodeKind.TEMPLATE | NodeKind.ITALIC):
        if (
            isinstance(node, TemplateNode)
            and node.template_name in GENDER_TEMPLATES
        ):
            page_data[-1].tags.extend(GENDER_TEMPLATES[node.template_name])
        elif node.kind == NodeKind.ITALIC:
            raw_tag = clean_node(wxr, None, node)
            if raw_tag != "":
                page_data[-1].raw_tags.append(raw_tag)

    wxr.wtp.start_subsection(clean_node(wxr, page_data[-1], level_node.largs))

    for level_4_node in level_node.find_child(NodeKind.LEVEL4):
        parse_section(wxr, page_data, base_data, level_4_node)

    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        extract_inf_table_template(wxr, page_data[-1], t_node)
        if t_node.template_name in ["Alte Schreibweise", "Alte Schreibung"]:
            extract_old_spell_template(wxr, page_data[-1], t_node)

    for table_node in level_node.find_child(NodeKind.TABLE):
        # page "beide"
        process_noun_table(wxr, page_data[-1], table_node)

    if not level_node.contain_node(NodeKind.LEVEL4):
        extract_glosses(wxr, page_data[-1], level_node)
    translate_raw_tags(page_data[-1])


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)

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
                    lang_code = "unknown"
                    if lang_name != "Umschrift":
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
                    lang=lang_name,
                    lang_code=lang_code,
                    word=page_title,
                    pos="unknown",
                )
                clean_node(wxr, base_data, subtitle_template)
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    parse_section(wxr, page_data, base_data, level3_node)
                for t_node in level2_node.find_child(NodeKind.TEMPLATE):
                    if t_node.template_name == "Ähnlichkeiten Umschrift":
                        process_umschrift_template(
                            wxr, page_data, base_data, t_node
                        )
                    elif t_node.template_name in [
                        "Alte Schreibweise",
                        "Alte Schreibung",
                    ]:
                        extract_old_spell_template(wxr, base_data, t_node)
                        page_data.append(base_data)

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


def extract_hyphenation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                if "," in node:
                    word_entry.hyphenation = node[: node.index(",")].strip()
                    break
                else:
                    word_entry.hyphenation += node.strip()
    if word_entry.hyphenation == "?":
        word_entry.hyphenation = ""


def extract_note_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        note = clean_node(
            wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
        )
        if note != "":
            word_entry.notes.append(note)


def extract_old_spell_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://de.wiktionary.org/wiki/Vorlage:Alte_Schreibweise
    word = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if word != "":
        word_entry.senses.append(Sense(alt_of=[AltForm(word=word)]))
    for tag in ["alt-of", "obsolete", "no-gloss"]:
        if tag not in word_entry.tags:
            word_entry.tags.append(tag)
    clean_node(wxr, word_entry, t_node)
