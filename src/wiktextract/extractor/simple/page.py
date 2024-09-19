import re
from typing import Any

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, print_tree
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .etymology import process_etym
from .models import WordEntry
from .pos import process_pos
from .pronunciation import process_pron
from .section_titles import POS_HEADINGS


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

    #####  Debug printing #####
    # Temporary debug print stuff without page parsing goes into debug_bypass.
    # If you're running a full extraction to find data, multiprocessing
    # *will* sometimes mess up your prints by overlaying some prints
    # with others. For quick and dirt stuff this might not matter, but if
    # you really want to be sure to get good prints you need to use
    # something like the logging package, which here is represented by
    # `logger`; the only annoyance is that it's not easy to get rid of
    # the datetime string at the start on the fly, so I just do it crudely
    # by inserting a `\n` in the message after `f"{wxr.wtp.title}..."`.

    # from .debug_bypass import debug_bypass
    # return debug_bypass(wxr, page_title, page_text)

    #####

    ##### Main page parse #####
    page_root = wxr.wtp.parse(
        page_text,
    )

    # print_tree(page_root)

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
    # POS sections, but a few pages have a more complex structure. This
    # is handled by simply flattening the parse tree later, and handling
    # sections in a linear order.
    base_data = WordEntry(
        word=wxr.wtp.title or "ERROR_NO_TITLE",
        # Simple English wiktionary entries are always for English words
        lang_code="en",
        lang="English",
        pos="ERROR_UNKNOWN_POS",
    )

    word_datas: list[WordEntry] = []

    for level in page_root.find_child_recursively(LEVEL_KIND_FLAGS):
        # Ignore everything outside of a section with a heading; there shouldn't
        # be anything there. Previous version of this code looked through that
        # stuff and would spit out warnings.

        # .find_child_recursively() (in contrast with find_child()) yields
        # a flattened tree, not just direct children of root

        # print(f"=== {heading_title=}")
        heading_title = clean_node(wxr, None, level.largs[0]).lower()

        if m := re.search(r"\s+\d+h$", heading_title):
            pos_num = int(m.group(0).strip())
            heading_title = heading_title[:m.start()]
        else:
            pos_num = -1
        if heading_title in POS_HEADINGS:
            pos = POS_HEADINGS[heading_title]["pos"]
            pos_data = base_data.copy(deep=True)
            new_data = process_pos(wxr, level, pos_data, pos, pos_num)
            if new_data is not None:
                word_datas.append(new_data)
        else:
            # Process pronunciation and etym sections.
            # Ignore other sections, like 'Description'
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
