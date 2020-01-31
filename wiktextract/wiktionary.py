# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import bz2
from lxml import etree
from wiktextract import wiktlangs
from .page import parse_page
from .config import WiktionaryConfig

# These XML tags are ignored when parsing.
ignore_xml_tags = set(["sha1", "comment", "username", "timestamp",
                       "sitename", "dbname", "base", "generator", "case",
                       "ns", "restrictions", "contributor", "username",
                       "minor", "parentid", "namespaces", "revision",
                       "siteinfo", "mediawiki",
])

# Other tags are ignored inside these tags.
xml_stack_ignore = ["contributor"]


class WiktionaryTarget(object):
    """This class is used for XML parsing the Wiktionary dump file."""

    def __init__(self, config, word_cb, capture_cb):
        assert isinstance(config, WiktionaryConfig)
        assert callable(word_cb)
        assert capture_cb is None or callable(capture_cb)
        self.word_cb = word_cb
        self.capture_cb = capture_cb
        self.config = config
        self.tag = None
        self.namespaces = {}
        self.stack = []
        self.text = None
        self.title = None
        self.pageid = None
        self.redirect = None
        self.model = None
        self.format = None

    def start(self, tag, attrs):
        """This is called whenever an XML start tag is encountered."""
        idx = tag.find("}")
        if idx >= 0:
            tag = tag[idx + 1:]
        attrs = {re.sub(r".*}", "", k): v for k, v in attrs.items()}
        tag = tag.lower()
        #while tag in self.stack:
        #    self.end(self.stack[-1])
        self.tag = tag
        self.stack.append(tag)
        self.attrs = attrs
        self.data = []
        if tag == "page":
            self.text = None
            self.title = None
            self.pageid = None
            self.redirect = None
            self.model = None
            self.format = None

    def end(self, tag):
        """This function is called whenever an XML end tag is encountered."""
        idx = tag.find("}")
        if idx >= 0:
            tag = tag[idx + 1:]
        tag = tag.lower()
        ptag = self.stack.pop()
        assert tag == ptag
        attrs = self.attrs
        data = "".join(self.data).strip()
        self.data = []
        if tag in ignore_xml_tags:
            return
        for t in xml_stack_ignore:
            if t in self.stack:
                return
        if tag == "id":
            if "revision" in self.stack:
                return
            self.pageid = data
        elif tag == "title":
            self.title = data
        elif tag == "text":
            self.text = data
        elif tag == "redirect":
            self.redirect = attrs.get("title")
        elif tag == "namespace":
            key = attrs.get("key")
            self.namespaces[key] = data
        elif tag == "model":
            self.model = data
            if data not in ("wikitext", "Scribunto", "css", "javascript",
                            "sanitized-css", "json"):
                print("UNRECOGNIZED MODEL", data)
        elif tag == "format":
            self.format = data
            if data not in ("text/x-wiki", "text/plain",
                            "text/css", "text/javascript", "application/json"):
                print("UNRECOGNIZED FORMAT", data)
        elif tag == "page":
            pageid = self.pageid
            title = self.title
            redirect = self.redirect
            if self.model in ("css", "sanitized-css", "javascript",
                              "Scribunto"):
                return
            if redirect:
                if self.config.capture_redirects:
                    data = {"redirect": redirect, "word": title}
                    self.word_cb(data)
            else:
                # If a capture callback has been provided, skip this page.
                if self.capture_cb and not self.capture_cb(title, self.text):
                    return
                # Parse the page, and call ``word_cb`` for each captured
                # word.
                ret = parse_page(title, self.text, self.config)
                for data in ret:
                    self.word_cb(data)
        else:
            print("UNSUPPORTED", tag, len(data), attrs)

    def data(self, data):
        """This function is called for data within an XML tag."""
        self.data.append(data)

    def close(self):
        """This function is called when parsing is complete."""
        return None


def parse_wiktionary(path, config, word_cb, capture_cb=None):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls ``capture_cb(title)`` for each raw page (if provided), and
    if it returns True, and calls ``word_cb(data)`` for all words
    defined for languages in ``languages``."""
    assert isinstance(path, str)
    assert isinstance(config, WiktionaryConfig)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    languages = config.capture_languages
    if languages is not None:
        assert isinstance(languages, (list, tuple, set))
        for x in languages:
            assert isinstance(x, str)
            assert x in wiktlangs.languages

    # Open the input file.
    if path.endswith(".bz2"):
        wikt_f = bz2.BZ2File(path, "r", buffering=(4 * 1024 * 1024))
    else:
        wikt_f = open(path, "rb", buffering=(4 * 1024 * 1024))

    try:
        # Create parsing context.
        ctx = WiktionaryTarget(config, word_cb, capture_cb)
        # Parse the XML file.
        parser = etree.XMLParser(target=ctx)
        etree.parse(wikt_f, parser)
    finally:
        wikt_f.close()

    # Return the parsing context.
    return ctx


# XXX pages linked under "Category:English glossaries" may be interesting
# to check out

# XXX pages linked under "Category:English appendices" may be interesting
# to check out

# XXX pages like "Appendix:Glossary of ..." seem interesting, might want to
# extract data from them?

# XXX "Appendix:Animals" seems to contain helpful information that we might
# want to extract.

# XXX Thesaurus:* pages seem potentially useful

# XXX Check out: Appendix:Roget's thesaurus classification.  Could this be
# helpful in hypernyms etc?

# Category:<langcode>:All topics and its subcategories seems very interesting.
# The English category tree looks very promising.  XXX where are the
# category relationships defined?  Wikimedia Commons?

# XXX check Unsupported titles/* and how to get their real title

# XXX test "sama" (Finnish) to check that linkages for list items are correct

# XXX test "juttu" (Finnish) to check that sense is correctly included in
# linkages

# XXX check pronunciations for "house" to see that "noun" and "verb" senses
# are correctly parsed

# XXX test "cat" (english) linkage - stuff at end in parenthesis

# XXX test "Friday" - it has embedded template in Related terms (currently
# handled wrong)

# XXX Finnish ällös seems to leave [[w:Optative mood|optative]] in gloss ???

# XXX Finnish binääri leaves binäärinen#Compounds in gloss
