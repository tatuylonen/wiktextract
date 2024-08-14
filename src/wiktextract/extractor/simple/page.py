import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import HTMLNode, TemplateNode, print_tree
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .etymology import process_etym
from .models import WordEntry
from .parse_utils import ADDITIONAL_EXPAND_TEMPLATES, PANEL_TEMPLATES
from .pos import process_pos
from .preprocess import preprocess_text
from .pronunciation import process_pron
from .text_utils import POS_STARTS_RE


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[WordEntry]:
    if page_title.startswith("Appendix:") or page_title == "Main Page":
        return []

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    page_text = preprocess_text(page_text, page_title=page_title)

    #####
    # Temporary debug print stuff goes into debug_bypass

    # from .debug_bypass import debug_bypass
    # return debug_bypass(wxr, page_title, page_text)

    #####

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing; these are problematic templates that generate stuff
    # that "should" be present for the page to parse better
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

    # print_tree(tree)
    # Some data that is collected is shared among several entries; things like
    # pronunciation data and etymological data is collected and updated in this
    # base_data object that can be copied for more specific entries.
    # Simple English Wiktionary has these sections under Level 3 ("===")
    # headers, which put them in an awkward hierarchy with the main page and
    # Part-of-Speech sections, which are higher; they usually appear before
    # POS sections, but a few pages have a more complex structure. We handle
    # this, specifically for Simple, by preprocessing the text (above) so that
    # the page is divided into one or more Level 1 nodes.
    # If the preprocessor has encountered a structure where you have something
    # that looks like the start of a section (like "Pronunciation") which comes
    # after POS data has already started, *and* is followed by a POS section
    # down the line, that's where the page is split by a Level 1 section.
    base_data = WordEntry(
        word=wxr.wtp.title or "NO_TITLE",
        # Simple English wiktionary entries are always for English words
        lang_code="en",
        lang="English",
        pos="unknown",
    )

    word_datas: list[WordEntry] = []

    for main_level in tree.children:
        # These are LEVEL1 nodes inserted by the preprocessor.
        # Wiktionaries don't usually use LEVEL1s, so it's sometimes safe to
        # use them as a splitter.

        # Collect Etymology (Word parts), Pronunciation data.
        # Ignore Description for now XXX maybe implement something if relevant.

        if isinstance(main_level, str):
            # This should never happen
            wxr.wtp.error(  # three levels: `debug`, `warning` and `error`
                f"Text outside of a main level: {str(main_level)[:255]}...",
                sortid="page.py/232",
            )
            continue

        for child in main_level.children:
            # Fail early block
            if isinstance(child, TemplateNode):
                # Template outside of a proper section, ignore, usually just
                # panels. These messages are handy if you want to clean up
                # articles.
                # Cases where someone has forgotten to add a heading before
                # a POS template (like {{verb}}) should already be handled
                # by the preprocessor which inserts a heading before these
                # orphaned templates.
                if child.template_name in PANEL_TEMPLATES:
                    # We just ignore these
                    continue
                wxr.wtp.debug(  # Could totally happen, not dangerous
                    f"Template node outside of a sublevel: "
                    f"'{str(child)[:255].strip()}'...",
                    sortid="page.py/232",
                )
                continue
            if isinstance(child, str):
                # Usually text outside of other nodes can be ignored.
                if not child.strip():
                    # An empty line
                    continue
                wxr.wtp.debug(
                    f"Text outside of a sublevel: "
                    f"'{str(child)[:255].strip()}'...",
                    sortid="page.py/232",
                )
                continue

            if isinstance(child, HTMLNode):
                if child.sarg == "br":
                    # Empty line
                    continue

            if child.kind == NodeKind.MAGIC_WORD:
                # Magic words like `__NOTOC__` that we don't need to handle.
                continue

            if child.kind == NodeKind.LINK:
                if child.largs[0][0].startswith("File:"):  # type:ignore[union-attr]
                    continue

            if child.kind not in LEVEL_KINDS:
                # Some lists created with ":"-formatting, some italics nodes
                # with text content, that sort of stuff usually containing
                # skippable meta-information. At the time of writing this
                # code, nothing was worth processing, and if it was, I would
                # have changed it on the Wiktionary side to a `Usage note`
                # section or similar.
                wxr.wtp.debug(
                    f"Node that is not a heading outside of a sublevel: "
                    f"'{str(child)[:255].strip()}'...",
                    sortid="page.py/232",
                )
                continue

            ############################
            # Main processing of headings levels

            heading_title = clean_node(wxr, None, child.largs[0]).lower()
            # print(f"=== {heading_title=}")

            if POS_STARTS_RE.match(heading_title):
                pos_datas = process_pos(wxr, child, heading_title, base_data)
                if pos_datas is not None:
                    word_datas.extend(pos_datas)
            elif heading_title.startswith("pronunciation"):
                process_pron(child, base_data)
            elif heading_title.startswith(
                "etymology"
            ) or heading_title.startswith("word parts"):
                process_etym(child, base_data)

    return []
