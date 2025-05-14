import re

from mediawiki_langcodes import code_to_name, name_to_code

# NodeKind is an internal enum for WikiNode and subclasses that specifies
# what kind of WikiNode it is. Subclasses also have the field, but it's
# always NodeKind.TEMPLATE for TemplateNodes etc.
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, NodeKind, WikiNode

# Clean node takes a WikiNode+strings node or tree and gives you a cleanish text
from wiktextract.page import clean_node, clean_value

# The main context object to more easily share state of parsing between
# functions. Contains WiktextractContext.wtp, which is the context for
# wikitextprocessor and usually holds all the good stuff.
from wiktextract.wxr_context import WiktextractContext

# For debug printing when doing batches and log messages that don't make
# sense as word-specific debug, warning or error messages (see those
# in wikitextprocessor's context).
from wiktextract.wxr_logging import logger

from .etymology import process_etym
from .models import WordEntry
from .parse_utils import (
    POSReturns,
    find_sections,
    parse_lower_heading,
    strip_accents,
)
from .pos import process_pos
from .pronunciation import process_pron
from .section_titles import (
    Heading,
    Tags,
)

# from .text_utils import ENDING_NUMBER_RE


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, WordEntry]]:
    """Parse Greek Wiktionary (el.wiktionary.org) page.

    References:
    * https://el.wiktionary.org/wiki/Βικιλεξικό:Δομή_λημμάτων
    """

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    parts = []
    parts.append(page_title)

    # from .debug_bypass import debug_bypass
    # return debug_bypass(wxr, page_title, page_text)

    if page_title.startswith("Πύλη:"):
        return []

    page_root = wxr.wtp.parse(
        page_text,
    )

    # print_tree(page_root)  # WikiNode tree pretty printer
    word_datas: list[WordEntry] = []

    # stuff_outside_main_headings = page_root.invert_find_child(
    #                                                         LEVEL_KIND_FLAGS)

    # Handle stuff at the very top of the page
    # for thing_node in stuff_outside_main_headings:
    #     ...

    previous_empty_language_name: str | None = None
    previous_empty_language_code: str | None = None

    for level in page_root.find_child(LEVEL_KIND_FLAGS):
        # Contents of the heading itself; should be "Languagename".
        # clean_node() is the general purpose WikiNode/string -> string
        # implementation. Things like formatting are stripped; it mimics
        # the output of wikitext when possible.
        # == English ==  # <- This part
        # === Noun ===
        lang_name, lang_code, ok = parse_language_name(
            wxr, clean_node(wxr, None, level.largs).strip()
        )

        section_num = -1

        # print("=====")
        # print(f"{level=}\n => {clean_node(wxr, None, level.largs).strip()}")

        sublevels = list(level.find_child(LEVEL_KIND_FLAGS))

        if not ok:
            if level.kind not in (NodeKind.LEVEL1, NodeKind.LEVEL2):
                # We tried to parse a lower level as a language because it
                # was a direct child of root and failed, so let's just ignore
                # it and not print a warning.
                continue
            if (
                previous_empty_language_name is None
                or previous_empty_language_code is None
            ):
                wxr.wtp.warning(
                    f"Can't parse language header: '{lang_name}'; "
                    "skipping section",
                    sortid="page/111",
                )
                continue
            lang_name = previous_empty_language_name
            lang_code = previous_empty_language_code
            sublevels = [level]

        wxr.wtp.start_section(lang_name)

        base_data = WordEntry(
            word=page_title,
            lang_code=lang_code,
            lang=lang_name,
            pos="ERROR_UNKNOWN_POS",
        )

        prev_data: WordEntry | None = None

        if len(sublevels) == 0 and ok:
            # Someone messed up by putting a Level 1 directly after a language
            # header.
            previous_empty_language_name = lang_name
            previous_empty_language_code = lang_code
            continue

        previous_empty_language_name = None
        previous_empty_language_code = None

        # XXX Some tables are put directly into the language level's content
        # Separate content and sublevels, parse content and put in base_data

        for sublevel in sublevels:
            if len(sublevel.largs) == 0:
                wxr.wtp.debug(
                    f"Sublevel without .largs: {sublevel=}", sortid="page/92"
                )
                continue

            heading_title = (
                clean_node(wxr, None, sublevel.largs[0]).lower().strip("= \n")
            )

            type, pos, heading_name, tags, num, ok = parse_lower_heading(
                wxr, heading_title
            )

            section_num = num if num > section_num else section_num

            if not ok:
                wxr.wtp.warning(
                    f"Sub-language heading '{heading_title}' couldn't be "
                    f"be parsed as a heading; "
                    f"{type=}, {heading_name=}, {tags=}.",
                    sortid="page/103/20241112",
                )
                continue

            if type in (Heading.Err, Heading.Ignored):
                continue
            ## TEMP

            found_pos_sections: POSReturns = []

            if type is Heading.Etym:
                # Update base_data with etymology and maybe sound data.
                # Return any sublevels in the etymology section
                # so that we can check for POS sections.
                num, etym_sublevels = process_etym(
                    wxr, base_data, sublevel, heading_name, section_num
                )

                section_num = num if num > section_num else section_num

                found_pos_sections.extend(etym_sublevels)

                # ...
                # text = clean_node(wxr, None, sublevel)
                # text = wxr.wtp.node_to_wikitext(sublevel)
                # if "\n=" in text:
                #     text = "£ " + "\n£ ".join(text.splitlines())
                #     logger.warning(f"£ {wxr.wtp.title}\n" + text)

                # PRINTS HERE

            # continue

            ## /TEMP

            # Typical pronunciation section that applies to the whole
            # entry
            if type == Heading.Pron:
                # Update base_data with sound and hyphenation data.
                # Return any sublevels in the pronunciation section
                # so that we can check for POS sections.
                num, pron_sublevels = process_pron(
                    wxr, sublevel, base_data, heading_name, section_num
                )

                section_num = num if num > section_num else section_num

                found_pos_sections.extend(pron_sublevels)

            if type is Heading.POS:
                found_pos_sections.append(
                    (
                        pos,
                        heading_name,
                        tags,
                        section_num,
                        sublevel,
                        base_data.model_copy(deep=True),
                    )
                )

            #################################################
            # Finally handle all POS sections we've extracted
            for (
                pos,
                title,
                tags,
                num,
                pos_section,
                pos_base_data,
            ) in found_pos_sections:
                if (
                    pos_ret := process_pos(
                        wxr,
                        pos_section,
                        pos_base_data.model_copy(deep=True),
                        prev_data,
                        pos,  # heading_name is the English pos
                        title,
                        tags,
                        num,
                    )
                ) is not None:
                    word_datas.append(pos_ret)
                    prev_data = pos_ret
                else:
                    wxr.wtp.error(
                        f"Couldn't parse PoS section {pos}",
                        sortid="page.py/20250110",
                    )

    # logger.info("%%" + "\n%%".join(parts))
    # Transform pydantic objects to normal dicts so that the old code can
    # handle them.
    return [wd.model_dump(exclude_defaults=True) for wd in word_datas]
    # return [base_data.model_dump(exclude_defaults=True)]


LANGUAGE_HEADINGS_RE = re.compile(r"([\w\s]+)\(([-\w]+)\)")

IRREGULAR_LANGUAGE_HEADINGS = {
    "διαγλωσσικοί όροι": {"name": "Translingual", "code": "mul"},
    "διεθνείς όροι": {"name": "Translingual", "code": "mul"},
    "νέα ελληνικά (el)": {"code": "el"},
    "μεσαιωνικά ελληνικά (gkm)": {"name": "Medieval Greek", "code": "gkm"},
    "μεσαιωνικά ελληνικά": {"name": "Medieval Greek", "code": "gkm"},
    "αρωμουνικά (βλάχικα) (roa-rup)": {"code": "roa-rup"},
    "κρητικά (el-crt)": {"code": "el-crt", "name": "Cretan Greek"},
    "κυπριακά (el-cyp)": {"code": "el-cyp", "name": "Cypriot Greek"},
    "χαρακτήρας unicode": {"code": "mul", "name": "Translingual"},
    # "": {"code": ""},
}


def parse_language_name(
    wxr: WiktextractContext, lang_heading: str
) -> tuple[str, str, bool]:
    lang_heading = lang_heading.strip()
    irregulars = IRREGULAR_LANGUAGE_HEADINGS.get(lang_heading.lower(), None)
    if irregulars is not None:
        return (
            irregulars.get("name") or code_to_name(irregulars["code"], "en"),
            irregulars["code"],
            True,
        )

    m = LANGUAGE_HEADINGS_RE.match(lang_heading)
    if m is None:
        lang_code = name_to_code(lang_heading, "el")
        if not lang_code:
            return lang_heading, "", False
        english_lang_name = code_to_name(lang_code, "en")
        if not english_lang_name:
            wxr.wtp.warning(
                f"Invalid lang_code '{lang_code}'", sortid="page/194"
            )
            return lang_heading, "", False
        return english_lang_name, lang_code, True
    else:
        matched_name = m.group(1).lower().strip()
        lang_code = m.group(2)
        greek_lang_name = code_to_name(lang_code, "el")
        english_lang_name = code_to_name(lang_code, "en")
        if not english_lang_name:
            wxr.wtp.warning(
                f"Invalid lang_code '{lang_code}'", sortid="page/43a"
            )
            return lang_heading, "", False
        if not strip_accents(greek_lang_name).lower() == strip_accents(
            matched_name
        ):
            wxr.wtp.debug(
                f"Language code '{lang_code}' "
                f"Greek name '{greek_lang_name}' does not match "
                f"original string '{lang_heading}'; "
                f"outputting {english_lang_name}",
                sortid="page/45",
            )
        return english_lang_name, lang_code, True
