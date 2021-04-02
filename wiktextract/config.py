# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE or https://ylonen.org

import sys
import collections



def int_dict():
    return collections.defaultdict(int)


def int_dict_dict():
    return collections.defaultdict(int_dict)


def list_dict():
    return collections.defaultdict(list)


class WiktionaryConfig(object):
    """This class holds configuration data for Wiktionary parsing."""

    __slots__ = (
        "capture_languages",
        "capture_translations",
        "capture_pronunciation",
        "capture_linkages",
        "capture_compounds",
        "capture_redirects",
        "capture_examples",
        "verbose",
        "num_pages",
        "language_counts",
        "pos_counts",
        "section_counts",
        "word",
        "errors",
        "warnings",
        "debugs",
    )

    def __init__(self,
                 capture_languages=["English", "Translingual"],
                 capture_translations=False,
                 capture_pronunciation=False,
                 capture_linkages=False,
                 capture_compounds=False,
                 capture_redirects=False,
                 capture_examples=False,
                 verbose=False):
        if capture_languages is not None:
            assert isinstance(capture_languages, (list, tuple, set))
            for x in capture_languages:
                assert isinstance(x, str)
        assert (capture_languages is None or
                isinstance(capture_languages, (list, tuple, set)))
        assert capture_translations in (True, False)
        assert capture_pronunciation in (True, False)
        assert capture_linkages in (True, False)
        assert capture_compounds in (True, False)
        assert capture_redirects in (True, False)
        self.capture_languages = capture_languages
        self.capture_translations = capture_translations
        self.capture_pronunciation = capture_pronunciation
        self.capture_linkages = capture_linkages
        self.capture_compounds = capture_compounds
        self.capture_redirects = capture_redirects
        self.capture_examples = capture_examples
        self.verbose = verbose
        # Some fields for statistics
        self.num_pages = 0
        self.language_counts = collections.defaultdict(int)
        self.pos_counts = collections.defaultdict(int)
        self.section_counts = collections.defaultdict(int)
        # Some fields related to errors
        # The word currently being processed.
        self.word = None
        self.errors = []
        self.warnings = []
        self.debugs = []

    def to_kwargs(self):
        return {
            "capture_languages": self.capture_languages,
            "capture_translations": self.capture_translations,
            "capture_pronunciation": self.capture_pronunciation,
            "capture_linkages": self.capture_linkages,
            "capture_compounds": self.capture_compounds,
            "capture_redirects": self.capture_redirects,
            "capture_examples": self.capture_examples,
            "verbose": self.verbose,
        }

    def to_return(self):
        return {
            "num_pages": self.num_pages,
            "language_counts": self.language_counts,
            "pos_counts": self.pos_counts,
            "section_counts": self.section_counts,
        }

    def merge_return(self, ret):
        assert isinstance(ret, dict)
        self.num_pages += ret["num_pages"]
        for k, v in ret["language_counts"].items():
            self.language_counts[k] += v
        for k, v in ret["pos_counts"].items():
            self.pos_counts[k] += v
        for k, v in ret["section_counts"].items():
            self.section_counts[k] += v
        for k in ("errors", "warnings", "debugs"):
            self.errors.extend(ret.get("errors", []))
            self.warnings.extend(ret.get("warnings", []))
            self.debugs.extend(ret.get("debugs", []))
