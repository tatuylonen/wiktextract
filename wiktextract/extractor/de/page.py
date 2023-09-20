import copy
import logging

from collections import defaultdict
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wikitextprocessor.parser import LevelNode

from wiktextract.datautils import append_base_data
from wiktextract.wxr_context import WiktextractContext

from .gloss import extract_glosses

# Templates that are used to form panels on pages and that should be ignored in
# various positions
PANEL_TEMPLATES = set()

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = set()

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = set()

FORM_TABLE_TEMPLATES = {
    "Deutsch Substantiv Übersicht",
    "Deutsch Substantiv Übersicht -sch",
    "Deutsch Toponym Übersicht",
    "Deutsch adjektivisch Übersicht",
    "Deutsch Eigenname Übersicht",
    "Deutsch Name Übersicht",
    "Deutsch Vorname Übersicht m",
    "Deutsch Vorname Übersicht f",
    "Deutsch Vorname Übersicht n",
    "Deutsch Verb Übersicht",
    "Deutsch Adjektiv Übersicht",
    "Pronomina-Tabelle",
    "Afrikaans Substantiv Übersicht",
    "Albanisch Verb Übersicht",
    "Altgriechisch Adjektiv Übersicht",
    "Altgriechisch Substantiv Übersicht",
    "Altirisch Substantiv Übersicht",
    "Altnordisch Substantiv Übersicht",
    "Aserbaidschanisch Substantiv Übersicht",
    "Asturisch Substantiv Übersicht",
    "Baschkirisch Substantiv Übersicht",
    "Baskisch Substantiv Übersicht",
    "Bosnisch Substantiv Übersicht",
    "Bretonisch Substantiv Übersicht",
    "Bulgarisch Verb Übersicht",
    "Dänisch Adjektiv Übersicht",
    "Dänisch Possessivpronomen Übersicht",
    "Dänisch Substantiv Übersicht",
    "Dänisch Verb Übersicht",
    "Englisch Adjektiv Übersicht",
    "Englisch Substantiv Übersicht",
    "Englisch Verb Übersicht",
    "Esperanto Substantiv Übersicht",
    "Färöisch Substantiv Übersicht",
    "Färöisch Verb Übersicht",
    "Finnisch Substantiv Übersicht",
    "Finnisch Verb Übersicht",
    "Französisch Adjektiv Übersicht",
    "Französisch Substantiv Übersicht",
    "Französisch Verb Übersicht",
    "Galicisch Substantiv Übersicht",
    "Hausa Adjektiv Übersicht",
    "Hausa Possessiv Übersicht",
    "Hausa Substantiv Übersicht",
    "Hebräisch Substantiv Übersicht",
    "Ido Substantiv Übersicht",
    "Irisch Adjektiv Übersicht",
    "Irisch Substantiv Übersicht",
    "Isländisch Name Übersicht",
    "Isländisch Substantiv Übersicht",
    "Isländisch Verb Übersicht",
    "Italienisch Adjektiv Übersicht",
    "Italienisch Substantiv Übersicht",
    "Italienisch Verb Übersicht",
    "Katalanisch Adjektiv Übersicht",
    "Katalanisch Substantiv Übersicht",
    "Katalanisch Verb Übersicht",
    "Keilschrift Übersicht",
    "Korsisch Substantiv Übersicht",
    "Kroatisch Adjektiv Übersicht",
    "Kroatisch Substantiv Übersicht",
    "Kurdisch Substantiv Übersicht",
    "Latein Adjektiv Übersicht",
    "Latein Adverb Übersicht",
    "Latein Substantiv Übersicht",
    "Lettisch Substantiv Übersicht",
    "Lettisch Verb Übersicht",
    "Mazedonisch Substantiv Übersicht",
    "Nahuatl Substantiv Übersicht",
    "Neugriechisch Substantiv Übersicht",
    "Niederdeutsch Adjektiv Übersicht",
    "Niederländisch Adjektiv Übersicht" "Niederländisch Substantiv Übersicht",
    "Niedersorbisch Substantiv Übersicht",
    "Norwegisch Adjektiv Übersicht",
    "Norwegisch Eigenname Übersicht",
    "Norwegisch Substantiv Übersicht",
    "Norwegisch Verb Übersicht",
    "Okzitanisch Substantiv Übersicht",
    "Okzitanisch Verb Übersicht",
    "Papiamentu Substantiv Übersicht",
    "Polnisch Grundzahl Übersicht",
    "Polnisch Substantiv Übersicht",
    "Portugiesisch Substantiv Übersicht",
    "Rumänisch Numerale Übersicht",
    "Rumänisch Personalpronomen Übersicht",
    "Rumänisch Substantiv Übersicht",
    "Rumänisch Verb Übersicht",
    "Russisch Substantiv Übersicht",
    "Sardisch Substantiv Übersicht",
    "Schwedisch Adjektiv Übersicht",
    "Schwedisch Adverb Übersicht",
    "Schwedisch Eigenname Übersicht",
    "Schwedisch Pronomen Übersicht",
    "Schwedisch Verb Übersicht",
    "Scots Substantiv Übersicht",
    "Serbisch Substantiv Übersicht",
    "Sesotho Substantiv Übersicht",
    "Slowakisch Adjektiv Übersicht",
    "Slowenisch Substantiv Übersicht",
    "Spanisch Adjektiv Übersicht",
    "Spanisch Substantiv Übersicht",
    "Spanisch Verb Übersicht",
    "Suaheli Substantiv Übersicht",
    "Suaheli Verb Übersicht",
    "Symbol Übersicht",
    "Tschechisch universal Übersicht",
    "Türkisch Substantiv Übersicht",
    "Ukrainisch Substantiv Übersicht",
    "Umbrisch Substantiv Übersicht",
    "Ungarisch Adjektiv Übersicht",
    "Ungarisch Substantiv Übersicht",
    "Ungarisch Verb Übersicht",
    "Usbekisch Substantiv Übersicht",
    "Venezianisch Substantiv Übersicht",
    "Walisisch Substantiv Übersicht",
    "Westflämisch Substantiv Übersicht",
}

# Templates that should not be pre-expanded
DO_NOT_PRE_EXPAND_TEMPLATES = {
    "Ü-Tabelle",  # Translation table
    "Quellen",  # Can be ignored since we have the <ref> tags in the tree
}

DO_NOT_PRE_EXPAND_TEMPLATES.update(FORM_TABLE_TEMPLATES)


def fix_level_hierarchy_of_subsections(
    wxr: WiktextractContext, tree: List[WikiNode]
) -> List[WikiNode]:
    """
    This function introduces level hierarchy to subsections and their content.

    The German Wiktionary does generally not use level 4 headings but instead
    uses templates to define the subsections. These templates are usually
    followed by a list of content that belongs to the subsection. Yet, in the
    tree the content is on the same level as the subsection template. In Gernman
    wiktionary, for cosmetic reasons, a level 4 heading is used to introduce the
    translation subsection that then also contains other subsections not related
    to translations.

    See:
    https://de.wiktionary.org/wiki/Hilfe:Formatvorlage#Der_%E2%80%9EEndteil%E2%80%9C
    """
    level_nodes: List[WikiNode] = []
    for node in tree:
        if isinstance(node, WikiNode):
            # A level 4 heading is used to introduce the translation
            # section.
            if node.kind == NodeKind.LEVEL4:
                # Find the index of the first template after the Ü-Tabelle
                # template
                split_idx = len(node.children)
                for idx, child in enumerate(node.children):
                    if split_idx < len(node.children):
                        if (
                            isinstance(child, WikiNode)
                            and child.kind == NodeKind.TEMPLATE
                        ):
                            break
                        else:
                            split_idx = idx + 1
                    if (
                        isinstance(child, WikiNode)
                        and child.kind == NodeKind.TEMPLATE
                        and child.template_name == "Ü-Tabelle"
                    ):
                        split_idx = idx + 1

                children_until_translation_table = node.children[:split_idx]

                children_after_translation_table = node.children[split_idx:]

                node.children = children_until_translation_table
                level_nodes.append(node)

                level_nodes.extend(
                    fix_level_hierarchy_of_subsections(
                        wxr, children_after_translation_table
                    )
                )

            elif node.kind == NodeKind.TEMPLATE:
                level_node = LevelNode(NodeKind.LEVEL4, node.loc)
                level_node.largs = [[node]]
                level_nodes.append(level_node)

            elif node.kind == NodeKind.LIST:
                if len(level_nodes) > 0:
                    level_nodes[-1].children.append(node)
                else:
                    wxr.wtp.debug(
                        f"Unexpected list while introducing level hierarchy: {node}",
                        sortid="extractor/de/page/introduce_level_hierarchy/52",
                    )
                    continue

            # Sometimes links are used outside of a section to link the whole
            # entry to a category. We treat them here as level 4 headings,
            # without any children.
            elif node.kind == NodeKind.LINK:
                level_node = LevelNode(NodeKind.LEVEL4, node.loc)
                level_node.largs = [[node]]
                level_nodes.append(level_node)

            # ignore <br> tags
            elif node.kind == NodeKind.HTML and node.sarg == "br":
                pass
            else:
                wxr.wtp.debug(
                    f"Unexpected WikiNode while introducing level hierarchy: {node}",
                    sortid="extractor/de/page/introduce_level_hierarchy/55",
                )
        else:
            if not len(level_nodes):
                if not isinstance(node, str) or not node.strip() == "":
                    wxr.wtp.debug(
                        f"Unexpected string while introducing level hierarchy: {node}",
                        sortid="extractor/de/page/introduce_level_hierarchy/61",
                    )
                continue
            level_nodes[-1].children.append(node)
    return level_nodes


def parse_section(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    level_node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> None:
    # Page structure: https://de.wiktionary.org/wiki/Hilfe:Formatvorlage

    if isinstance(level_node, list):
        for x in level_node:
            parse_section(wxr, page_data, base_data, x)
        return

    elif not isinstance(level_node, WikiNode):
        if not isinstance(level_node, str) or not level_node.strip() == "":
            wxr.wtp.debug(
                f"Unexpected node type in parse_section: {level_node}",
                sortid="extractor/de/page/parse_section/31",
            )
        return

    # Level 3 headings are used to start POS sections like
    # === {{Wortart|Verb|Deutsch}} ===
    elif level_node.kind == NodeKind.LEVEL3:
        for template_node in level_node.find_content(NodeKind.TEMPLATE):
            # German Wiktionary uses a `Wortart` template to define the POS
            if template_node.template_name == "Wortart":
                process_pos_section(
                    wxr, page_data, base_data, level_node, template_node
                )
        return

    # Level 4 headings were introduced by fix_level_hierarchy_of_subsections()
    # for subsections that are introduced by templates.
    elif level_node.kind == NodeKind.LEVEL4:
        for template_node in level_node.find_content(NodeKind.TEMPLATE):
            section_name = template_node.template_name
            wxr.wtp.start_subsection(section_name)
            if section_name == "Bedeutungen":
                for list_node in level_node.find_child(NodeKind.LIST):
                    extract_glosses(wxr, page_data, list_node)


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
    page_data: List[Dict],
    base_data: Dict,
    level_node: LevelNode,
    pos_template_node: WikiNode,
) -> None:
    # Extract the POS
    pos_argument = pos_template_node.template_parameters.get(1)
    if pos_argument in FORM_POS.union(IGNORE_POS):
        # XXX: Extract forms from form sections
        return
    pos_type = wxr.config.POS_SUBTITLES.get(pos_argument)

    if pos_type is None:
        wxr.wtp.debug(
            f"Unknown POS type: {pos_argument}",
            sortid="extractor/de/page/process_pos_section/55",
        )
        return
    pos = pos_type["pos"]

    wxr.wtp.start_section(page_data[-1]["lang_code"] + "_" + pos)

    base_data["pos"] = pos
    append_base_data(page_data, "pos", pos, base_data)

    # There might be other templates in the level node that define grammatical
    # features other than the POS. Extract them here.
    for template_node in level_node.find_content(NodeKind.TEMPLATE):
        template_name = template_node.template_name

        GENDER_TAGS_TEMPLATES = {
            "m",
            "f",
            "f ",
            "n",
            "n ",
            "mf",
            "mn.",
            "fn",
            "fm",
            "nf",
            "nm",
            "mfn",
            "u",
            "un",
            "Geschlecht",  # placeholder template
        }

        VERB_TAGS_TEMPLATES = {
            "unreg.",
            "intrans.",
            "trans.",
            "refl.",
        }

        ARAB_VERB_STEM_TEMPLATES = {
            "Grundstamm",
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
        }

        NOUN_TAGS_TEMPLATES = {
            "adjektivische Deklination",
            "kPl.",
            "Pl.",
            "mPl.",
            "fPl.",
            "nPl.",
            "Sachklasse",
            "Personenklasse",
            "indekl.",
            "Suaheli Klassen",
        }

        if template_name == "Wortart":
            continue

        elif template_name in GENDER_TAGS_TEMPLATES.union(
            ARAB_VERB_STEM_TEMPLATES
        ).union(NOUN_TAGS_TEMPLATES).union(VERB_TAGS_TEMPLATES):
            # XXX: de: Extract additional grammatical markers
            pass

        else:
            wxr.wtp.debug(
                f"Unexpected template in POS section heading: {template_node}",
                sortid="extractor/de/page/process_pos_section/31",
            )

    subsections = fix_level_hierarchy_of_subsections(wxr, level_node.children)

    for subsection in subsections:
        parse_section(wxr, page_data, base_data, subsection)
    return


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> List[Dict[str, str]]:
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
        do_not_pre_expand=DO_NOT_PRE_EXPAND_TEMPLATES,
    )

    page_data = []
    for node in filter(lambda n: isinstance(n, WikiNode), tree.children):
        # ignore certain top level templates
        if node.kind == NodeKind.TEMPLATE:
            template_name = node.template_name

            # Mostly meta-templates at the top of the page that do not carry
            # any semantic information
            IGNORE_TOP_LEVEL_TEMPLATES = {
                "Wort der Woche",
                "Siehe auch",
                "erweitern",
                "Abschnitte fehlen",
                "überarbeiten",
                "Zeichen",
                "Wortart fehlt",
                "TOC limit",
                "Neuer Eintrag",
                "Löschantrag/Vorlage",
                "keine Belegstelle/Vorlage",
                "Anmerkung Keilschrift",
                "In Arbeit",
                "Halbgeschützte Seite",
                "anpassen",
            }

            if template_name in IGNORE_TOP_LEVEL_TEMPLATES:
                continue

        # ignore certain top level magic words
        if node.kind == NodeKind.MAGIC_WORD and node.sarg in {
            "__TOC__",
            "__NOTOC__",
            "__NOEDITSECTION__",
        }:
            continue

        if node.kind != NodeKind.LEVEL2:
            wxr.wtp.warning(
                f"Unexpected top-level node: {node}",
                sortid="extractor/de/page/parse_page/61",
            )
            continue

        for subtitle_template in node.find_content(NodeKind.TEMPLATE):
            # The language sections are marked with
            # == <title> ({{Sprache|<lang_name>}}) ==
            # where <title> is the title of the page and <lang_name> is the
            # German name of the language of the section.
            if subtitle_template.template_name == "Sprache":
                lang_name = subtitle_template.template_parameters.get(1)
                lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang_name)
                if not lang_code:
                    wxr.wtp.warning(
                        f"Unknown language: {lang_name}",
                        sortid="extractor/de/page/parse_page/76",
                    )
                    continue

                base_data = defaultdict(
                    list,
                    {
                        "lang": lang_name,
                        "lang_code": lang_code,
                        "word": wxr.wtp.title,
                    },
                )
                page_data.append(copy.deepcopy(base_data))
                parse_section(wxr, page_data, base_data, node.children)

    return page_data
