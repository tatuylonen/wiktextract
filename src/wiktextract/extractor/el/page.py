from mediawiki_langcodes import name_to_code  # Thanks for xxyzz!

# NodeKind is an internal enum for WikiNode and subclasses that specifies
# what kind of WikiNode it is. Subclasses also have the field, but it's
# always NodeKind.TEMPLATE for TemplateNodes etc.
from wikitextprocessor.parser import LEVEL_KIND_FLAGS  # , print_tree

# Clean node takes a WikiNode+strings node or tree and gives you a cleanish text
from wiktextract.page import clean_node

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
from .pos import process_pos
from .section_titles import POS_HEADINGS
from .text_utils import ENDING_NUMBER_RE

# ===========================
# EXTRACTOR STARTING TEMPLATE
# MAIN ENTRY TO EXTRACTOR
# =======================

# Every extractor has a subfolder in src/wiktextract/extractor that contains
# meta-data, config files and source code for that particular extractor. The
# main Wiktextract code calls these modules by loading them dynamically using
# importlib, then calls parse_page(); this is the main entry point for your
# extractor.

# WordEntry is a Pydantic model (or just a dict in the original English
# extractor) that will eventually be outputted as a json object; each
# entry is, in general, either a redirect page (which you do not have to
# worry about) or a Part of Speech section's data. If a word has a `Noun`
# section and an `Adjective` section, they're processed into different entries;
# different Etymologies are also separate and can have several entries within
# them.

# WordEntries are composed of smaller data sections, like lists of Senses,
# Sounds and Etymology data. Your extractor does not need to handle everything,
# and there is rarely any need to add new fields (because often they already
# exist in the English extractor), but it is possible to add them if needed;
# please check first with an issue to keep everyone in synch.

# To see an actually working extractor with relatively simple code, take a look
# at src/wiktextract/extractor/simple/ for the Simple English Wiktionary
# extractor. This template, and its comments, is partially built on that, so
# some of it might seem repetitive, but the SEW extractor has more specific
# examples of things that could be needed in an extractor.


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, WordEntry]]:
    """Parse __EXAMPLE_TEMPLATE__ Wiktionary page."""

    if wxr.config.verbose:
        logger.info(f"Parsing page: {page_title}")

    # In a larger edition, we might need to handle more complex titles that have
    # been changed due to the restrictions of WikiMedia article names.
    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    #####  Debug printing in early stages #####
    # Temporary debug print stuff without page parsing went into debug_bypass.
    # If you're running a full extraction to find data, multiprocessing
    # *will* sometimes mess up your prints by overlaying some prints
    # with others. For quick and dirty stuff this might not matter; but if
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

    # `Wtp.parse()` always returns a `NodeKind.ROOT` node, which has as its
    # children everything else that was parsed from the string.

    page_root = wxr.wtp.parse(
        page_text,
    )

    # print_tree(page_root)  # WikiNode tree pretty printer

    # This is our return list. Each page will return a list Part-of-speech
    # word entries that are just collected into one big list and eventually
    # concatenated as a JSONL file. No hierarchies between words, just a flat
    # list.
    word_datas: list[WordEntry] = []

    # TIP:
    # It is good to keep in mind for the parse-tree: things like headings
    # (nodes with NodeKind.LEVEL) will consume the rest of the document
    # so that everything after them is a child node of that level, until
    # the next heading comes along; this is the same for lists inside lists,
    # etc.
    # This means that you can get the "immediate" contents of a heading, or
    # the root node, by finding all child nodes that appear before another
    # heading of the same level.

    stuff_outside_main_headings = page_root.invert_find_child(LEVEL_KIND_FLAGS)

    # Handle stuff at the very top of the page
    for thing_node in stuff_outside_main_headings:
        ...

    # Usually in most Wiktionary editions this is where where you split the page
    # into different language entries; "English", "Gaelic", "Swahili", etc.
    # Each section would be a Level 2 node (`NodeKind.LEVEL2`) child of the
    # page's root node. Wiktionaries do not seem to use LEVEL1 for anything,
    # although there might be (there definitely is...) an exception somewhere.
    # LEVEL_KIND_FLAGS is an enum union for all NodeKind.LEVEL:s. We hope we
    # only get LEVEL2s at the the top level.
    for level in page_root.find_child(LEVEL_KIND_FLAGS):
        # Contents of the heading itself; should be "Languagename".
        # clean_node() is the general purpose WikiNode/string -> string
        # implementation. Things like formatting are stripped; it mimics
        # the output of wikitext when possible.
        # == English ==  # <- This part
        # === Noun ===
        lang_name = clean_node(wxr, None, level.largs)
        lang_code = name_to_code(lang_name, "__EXAMPLE_LANG_CODE__")

        base_data = WordEntry(
            word=page_title,
            lang_code=lang_code,
            lang=lang_name,
            pos="ERROR_UNKNOWN_POS",
        )

        ##### Looping over sections #####
        # Each wiktionary has its own standards and lack of standards. Usually,
        # an article is made out of Level 2 Language headings, under which we
        # have more specific headings, like Etymology sections that contain
        # Parts of Speech sections or POS sections if not etymology is provided
        # (etym sections usually Level 3, POS usually Level 4 ("====").
        # YMMV! For an example of something quite different, take a look at the
        # Simple English Wiktionary code.
        for level_etym in level.find_child(LEVEL_KIND_FLAGS):
            heading_title = (
                clean_node(wxr, None, level_etym.largs[0]).lower().strip()
            )
            # print(f"=== {heading_title=}")

            # Sometimes headings have a number at the end ("Etymology 2", "Noun
            # 2")
            if m := ENDING_NUMBER_RE.search(heading_title):
                heading_num = int(m.group(0).strip())
                heading_title = heading_title[: m.start()]
            else:
                heading_num = -1  # default: see models.py/Sense

            new_data: list[WordEntry] = []
            if heading_title.startswith(("etymology",)):
                # USUALLY this is a LEVEL 3 node with Part of speech headings
                # inside of it. The template assumes if there is an Etym section
                # then it has POS sections inside of it.
                etym_data = base_data.model_copy(deep=True)
                new_data = process_etym(
                    wxr,
                    etym_data,
                    level_etym,
                    heading_title,
                    heading_num,
                )
            elif heading_title in POS_HEADINGS:
                pos_data = base_data.model_copy(deep=True)
                # Assume we'll get only one WordEntry or nothing.
                if (
                    nd := process_pos(
                        wxr, level, pos_data, heading_title, heading_num
                    )
                ) is not None:
                    new_data.append(nd)
            else:
                ...
            if new_data is not None:
                # new_data would be one WordEntry object, for one Part of
                # Speech section ("Noun", "Verb"); this is generally how we
                # want it.
                word_datas.extend(new_data)

    # Transform pydantic objects to normal dicts so that the old code can
    # handle them.
    return [wd.model_dump(exclude_defaults=True) for wd in word_datas]
    # return [base_data.model_dump(exclude_defaults=True)]
