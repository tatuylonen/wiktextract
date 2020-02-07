# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import bz2
import subprocess
from lxml import etree
from .wiktlangs import wiktionary_languages
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
            self.config.num_pages += 1

            # Enforce limit on number of pages (for debugging)
            # XXX how do we abort reading
            if self.config.limit and self.config.num_pages > self.config.limit:
                if self.config.num_pages == self.config.limit + 1:
                    print("REACHED MAXIMUM NUMBER OF PAGES TO PROCESS")
                    self.aborted = True
                return

            if self.model in ("css", "sanitized-css", "javascript",
                              "Scribunto"):
                return

            if redirect:
                if self.config.capture_redirects:
                    data = {"redirect": redirect, "word": title}
                    self.word_cb(data)
                    return

            # If a capture callback has been provided and returns False,
            # skip this page.
            if self.capture_cb and not self.capture_cb(title, self.text):
                return

            if title.endswith("/translations"):
                # XXX parse as a special translation page
                pass
            else:
                # Parse the page, and call ``word_cb`` for each captured
                # word.
                ret = parse_page(title, self.text, self.config)
                for data in ret:
                    # XXX check for "translation_link" and postpone if
                    # present, process after all others using
                    # translations from separate translation pages
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
            assert x in wiktionary_languages

    # Open the input file.
    subp = None
    if path.endswith(".bz2"):
        subp = subprocess.Popen(["bzcat", path], stdout=subprocess.PIPE,
                                bufsize=8*1024*1024)
        wikt_f = subp.stdout
        #wikt_f = bz2.BZ2File(path, "r", buffering=(4 * 1024 * 1024))
    else:
        wikt_f = open(path, "rb", buffering=(4 * 1024 * 1024))

    try:
        # Create parsing context.
        ctx = WiktionaryTarget(config, word_cb, capture_cb)
        ctx.aborted = False
        # Parse the XML file.
        parser = etree.XMLParser(target=ctx)
        while not ctx.aborted:
            data = wikt_f.read(1024 * 1024)
            if not data:
                break
            parser.feed(data)
    finally:
        wikt_f.close()
        if subp:
            subp.kill()
            subp.wait()

    # Return the parsing context.
    return ctx
