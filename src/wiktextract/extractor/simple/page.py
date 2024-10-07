from wikitextprocessor.parser import LEVEL_KIND_FLAGS  #, print_tree

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .etymology import process_etym
from .models import WordEntry
from .pos import process_pos
from .pronunciation import process_pron
from .section_titles import POS_HEADINGS
from .text_utils import POS_ENDING_NUMBER_RE

# =========================
# Simple English Wiktionary
# =========================

# Every Wiktionary is different from others, and Simple English Wiktionary
# is no different; but it is usually pretty simple and reasonably regular
# in its structure, small enough so that its extractor doesn't get completely
# out of hand, and in English so that you can follow along much more easily,
# which is why it works well as an example case.

# Every extractor has a subfolder in src/wiktextract/extractor that contains
# meta-data, config files and source code for that particular extractor. The
# main Wiktextract code calls these modules by loading them dynamically using
# importlib, then calls parse_page(); this is the main entry point for your
# extractor data.

# WordEntry is a Pydantic model (or just a dict in the original English
# extractor) that will eventually be outputted as a json object; each
# entry is, in general, either a redirect page (which you do not have to
# worry about) or a Part of Speech section's data. If a word has a `Noun`
# section and an `Adjective` section, they're processed into different entries;
# different Etymologies are also separate and can have several entries within
# them.

# WordEntries are composed of smaller data sections, like lists of Senses,
# Sounds and Etymology data. Your extractor does not need to handle everything,
# and there is rarely any need to add more fields (because often they already
# exist in the English extractor), but it is possible to add fields if needed;
# please check first with an issue to keep everyone in synch.

def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, WordEntry]]:
    """Parse Simple English Wiktionary page."""
    # Unlike other wiktionaries, Simple Wikt. has a limited scope: only English
    # words. The pages also tend to be much shorter and simpler in structure,
    # which makes parsing them much simpler.
    # https://simple.wiktionary.org/wiki/Wiktionary:Entry_layout_explained

    # Usually things like this are handled by checking a page's namespace
    # code; in SEW's case, Main Page and the Appendices share the same
    # namespace as the word articles.
    if page_title == "Main Page" or page_title.startswith("Appendix:"):
        return []

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    #####  Debug printing #####
    # Temporary debug print stuff without page parsing went into debug_bypass.
    # If you're running a full extraction to find data, multiprocessing
    # *will* sometimes mess up your prints by overlaying some prints
    # with others. For quick and dirty stuff this might not matter, but if
    # you really want to be sure to get good prints you need to use
    # something like the logging package, which here is represented by
    # `logger`; the only annoyance is that it's not easy to get rid of
    # the datetime string at the start on the fly, so I just do it crudely
    # by inserting a `\n` in the message after `f"{wxr.wtp.title}..."`.

    # from .debug_bypass import debug_bypass
    # return debug_bypass(wxr, page_title, page_text)

    #####

    ##### Main page parse #####
    # `Wtp.parse()` (Wtp being the main context class of Wikitextprocessor
    # imbedded into the Wiktextract context object) takes wikitext and
    # returns a tree of parsed nodes: strings and WikiNodes.

    # `Wtp.parse()` returns a `NodeKind.ROOT` node, which has as its children
    # everything else that was parsed from the string.
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
        word=page_title,
        # Simple English wiktionary entries are always for English words
        lang_code="en",
        lang="English",
        pos="ERROR_UNKNOWN_POS",
    )

    # This is our ret.
    word_datas: list[WordEntry] = []

    for level in page_root.find_child_recursively(LEVEL_KIND_FLAGS):
        # Ignore everything outside of a section with a heading; there shouldn't
        # be anything there. Previous version of this code looked through that
        # stuff and would spit out warnings, which can be useful when figuring
        # out what kind of stuff there can be found in an article.

        # .find_child_recursively() (in contrast with find_child()) yields
        # a flattened tree, not just direct children of root

        # clean_node() is the general purpose WikiNode/string -> string
        # implementation. Things like formatting are stripped; it mimics
        # the output of wikitext when possible.
        # WikiNodes have a list of lists of anything as their "arguments",
        # if applicable. Some WikiNode subclasses have .sarg (string argument)
        # instead to make things easier. Mainly this stems from stuff like
        # Template nodes having their arguments parsed as nodes themselves;
        # each `|` separated parameter is a list of nodes.
        heading_title = clean_node(wxr, None, level.largs[0]).lower()
        # print(f"=== {heading_title=}")

        # Sometimes headings in SWE have a number at the end ("Noun 2")
        if m := POS_ENDING_NUMBER_RE.search(heading_title):
            pos_num = int(m.group(0).strip())
            heading_title = heading_title[: m.start()]
        else:
            pos_num = -1  # default: see models.py/Sense
        if heading_title in POS_HEADINGS:
            pos_data = base_data.model_copy(deep=True)
            new_data = process_pos(wxr, level, pos_data, heading_title, pos_num)
            if new_data is not None:
                # new_data would be one WordEntry object, for one Part of
                # Speech section ("Noun", "Verb"); this is generally how we
                # want it.
                word_datas.append(new_data)
        else:
            # Process pronunciation and etym sections.
            # Ignore other sections, like 'Description'
            # On Simple Wiktionary, these appear as level-3 nodes under the
            # **previous** POS node; that's why we flatten everything with the
            # recursive iterator. At least these are in "order".
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
