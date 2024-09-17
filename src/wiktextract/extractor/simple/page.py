import re
from typing import Any

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)
from wikitextprocessor.parser import print_tree
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .models import Sense, WordEntry
from .page_utils import recurse_base_data_sections
from .parse_utils import (
    ADDITIONAL_EXPAND_TEMPLATES,
    PANEL_TEMPLATES,
)
from .pos import process_pos
from .preprocess import preprocess_text
from .text_utils import POS_STARTS_RE


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    """Parse Simple Wiktionary page."""
    # Unlike other wiktionaries, Simple Wikt. has a limited scope: only English
    # words. The pages also tend to be much shorter and simpler in structure,
    # which makes parsing them much simpler.

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

    # If this was a normal wiktionary edition, this is where you would split
    # the page into different language entries; "English", "Gaelic", "Swahili",
    # etc.
    # Each section would be a Level 2 node (`NodeKind.LEVEL2`) child of the
    # page's root node. Wiktionaries do not seem to use LEVEL1 for anything,
    # although there might be (there definitely is...) an exception somewhere.

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
    # down the line, that's where we split the page with a Level 1 section.
    base_data = WordEntry(
        word=wxr.wtp.title or "ERROR_NO_TITLE",
        # Simple English wiktionary entries are always for English words
        lang_code="en",
        lang="English",
        pos="ERROR_UNKNOWN_POS",
    )

    word_datas: list[WordEntry] = []

    for main_level in tree.children:
        # These are LEVEL1 nodes inserted by the preprocessor in
        # preprocess_text. Wiktionaries don't usually use LEVEL1s, so it's
        # sometimes safe to use them as a splitter.

        # Collect Etymology (Word parts), Pronunciation data.
        # Ignore Description for now. XXX maybe implement something if relevant.

        if isinstance(main_level, str):
            # This should never happen; we've inserted a LEVEL 1 node at
            # the start of the page, which makes everything else after it
            # its child, unless there are other LEVEL 1 nodes present.
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
                wxr.wtp.debug(  # "debug": could totally happen, not dangerous
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
                    # newline, ignore
                    continue

            if child.kind == NodeKind.MAGIC_WORD:
                # Magic words like `__NOTOC__` that we don't need to handle.
                continue

            if child.kind == NodeKind.LINK:
                if child.largs[0][0].startswith("File:"):  # type:ignore[union-attr]
                    # Ignore image files
                    continue

            if isinstance(child, WikiNode) and not isinstance(child, LevelNode):
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

            # POS-sections *should* only appear here, at this level.
            if m := POS_STARTS_RE.match(heading_title):
                pos_data = base_data.copy(deep=True)
                pos = m.group(1).strip()
                if num := m.group(2):
                    pos_num = int(num.strip())
                else:
                    pos_num = None
                pos_datas = process_pos(wxr, child, pos_data, pos, pos_num)
                if pos_datas is not None:
                    word_datas.extend(pos_datas)
            else:
                # Pronunciation and Etymology sections should all be in this
                # part of the LEVEL 1 node, because the LEVEL 1 heading should
                # have been inserted by the preprocessor before these sections.
                # Only subsections at the end of the article (that is, no other
                # POS section follows) are children of POS nodes, all others
                # are children of LEVEL 1 or other subnodes that are children
                # of LEVEL 1.
                recurse_base_data_sections(wxr, child, base_data)

    # Transform pydantic objects to normal dicts so that the old code can
    # handle them.
    return [wd.model_dump(exclude_defaults=True) for wd in word_datas]
    # return [base_data.model_dump(exclude_defaults=True)]
