# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE or https://ylonen.org

import collections


class WiktionaryConfig(object):
    """This class holds configuration data for Wiktionary parsing."""
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
        self.language_counts = collections.defaultdict(int)
        self.pos_counts = collections.defaultdict(int)
        self.section_counts = collections.defaultdict(int)
