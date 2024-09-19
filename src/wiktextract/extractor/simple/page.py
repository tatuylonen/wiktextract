import re
from typing import Any

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, print_tree
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .etymology import process_etym
from .models import WordEntry
from .pos import process_pos
from .preprocess import preprocess_text
from .pronunciation import process_pron
from .section_titles import POS_DATA


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    """Parse Simple Wiktionary page."""
    # Unlike other wiktionaries, Simple Wikt. has a limited scope: only English
    # words. The pages also tend to be much shorter and simpler in structure,
    # which makes parsing them much simpler.
    # https://simple.wiktionary.org/wiki/Wiktionary:Entry_layout_explained

    if page_title in (
        "Main Page",
        "Main page",
    ) or page_title.startswith("Appendix:"):
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

    for level in tree.find_child_recursively(LEVEL_KIND_FLAGS):
        # Ignore everything outside of a section with a heading; there shouldn't
        # be anything there. Previous version of this code looked through that
        # stuff and would spit out warnings.

        # Collect Etymology (Word parts), Pronunciation data.
        # Ignore Description for now. XXX maybe implement something if relevant.

        # print(f"=== {heading_title=}")
        heading_title = clean_node(wxr, None, level.largs[0]).lower()

        if m := re.search(r"\s+\d+h$", heading_title):
            pos_num = int(m.group(0).strip())
            heading_title = heading_title[:m.start()]
        else:
            pos_num = -1
        if heading_title in POS_DATA:
            pos = POS_DATA[heading_title]["pos"]
            pos_data = base_data.copy(deep=True)
            new_data = process_pos(wxr, level, pos_data, pos, pos_num)
            if new_data is not None:
                word_datas.append(new_data)
        else:
            # Process pronunciation and etym sections.
            # On Simple Wiktionary, these appear as level-3 nodes under the
            # previous POS node; that's why we flatten everything with the
            # recursive iterator
            if heading_title.startswith("pronunciation"):
                # Replace sound data in target_data with new data, if applicable
                process_pron(wxr, level, base_data)
            elif heading_title.startswith(("etymology", "word parts")):
                # Replace etymology data in target_data with new data, if
                # applicable
                process_etym(wxr, level, base_data)

    # Transform pydantic objects to normal dicts so that the old code can
    # handle them.
    return [wd.model_dump(exclude_defaults=True) for wd in word_datas]
    # return [base_data.model_dump(exclude_defaults=True)]
