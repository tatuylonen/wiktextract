# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE or https://ylonen.org

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
        "errors",
        "warnings",
        "debugs",
        "unrecognized_template_counts",
        "unrendered_template_counts",
        "unrecognized_template_samples",
        "unrendered_template_samples",
        "unknown_value_counts",
        "word",
        "language",
        "pos",
        "subsection",
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
        self.errors = []
        self.warnings = []
        self.debugs = []
        self.unrecognized_template_counts = collections.defaultdict(int)
        self.unrendered_template_counts = collections.defaultdict(int)
        # These map [tag][sorted(argkeys)] -> list of (lang, pos, str(template)
        self.unrecognized_template_samples = collections.defaultdict(list_dict)
        self.unrendered_template_samples = collections.defaultdict(list_dict)
        # This maps [lang][tag][value] to int
        self.unknown_value_counts = collections.defaultdict(int_dict_dict)
        # The word, language, and part-of-speech currently being processed.
        # These are here to avoid having to pass so many arguments to so many
        # functions.
        self.word = None
        self.language = None
        self.pos = None
        self.subsection = None

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
            "errors": self.errors,
            "warnings": self.warnings,
            "debugs": self.debugs,
            "unrecognized_template_counts": self.unrecognized_template_counts,
            "unrendered_template_counts": self.unrendered_template_counts,
            "unrecognized_template_samples": self.unrecognized_template_samples,
            "unrendered_template_samples": self.unrendered_template_samples,
            "unknown_value_counts": self.unknown_value_counts,
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
        self.errors.extend(ret["errors"])
        self.warnings.extend(ret["warnings"])
        self.debugs.extend(ret["debugs"])
        for k, v in ret["unrecognized_template_counts"].items():
            self.unrecognized_template_counts[k] += v
        for k, v in ret["unrendered_template_counts"].items():
            self.unrendered_template_counts[k] += v
        for k, v in ret["unrecognized_template_samples"].items():
            for kk, vv in v.items():
                self.unrecognized_template_samples[k][kk].extend(vv)
        for k, v in ret["unrendered_template_samples"].items():
            for kk, vv in v.items():
                self.unrendered_template_samples[k][kk].extend(vv)
        for k, v in ret["unknown_value_counts"].items():
            for kk, vv in v.items():
                for kkk, vvv in vv.items():
                    self.unknown_value_counts[k][kk][kkk] += vvv

    def error(self, msg):
        assert isinstance(msg, str)
        self.errors.append({"word": self.word, "lang": self.language,
                            "pos": self.pos, "msg": msg})
        pos = self.pos if self.pos else "top-level"
        if self.subsection:
            pos += " in " + self.subsection
        print("{}: {}/{}: ERROR: {}"
              "".format(self.word, self.language, pos, msg))
        sys.stdout.flush()

    def warning(self, msg):
        assert isinstance(msg, str)
        self.warnings.append({"word": self.word, "lang": self.language,
                              "pos": self.pos, "msg": msg})
        pos = self.pos if self.pos else "top-level"
        if self.subsection:
            pos += " in " + self.subsection
        print("{}: {}/{}: WARNING: {}"
              "".format(self.word, self.language, pos, msg))
        sys.stdout.flush()

    def debug(self, msg):
        assert isinstance(msg, str)
        self.debugs.append({"word": self.word, "lang": self.language,
                            "pos": self.pos, "msg": msg})
        pos = self.pos if self.pos else "top-level"
        if self.subsection:
            pos += " in " + self.subsection
        print("{}: {}/{}: DEBUG: {}"
              "".format(self.word, self.language, pos, msg))
        sys.stdout.flush()

    def unrecognized_template(self, t, ctx):
        assert isinstance(ctx, str)
        self.error("unrecognized template in {}: {}".format(ctx, t))
        name = t.name.strip()
        self.unrecognized_template_counts[name] += 1
        argnames = tuple(sorted(x.name.strip() for x in t.arguments
                                if x.value.strip()))
        argnames = ", ".join(argnames)
        if len(self.unrecognized_template_samples[name][argnames]) < 2:
            self.unrecognized_template_samples[name][argnames].append(
                (self.language, self.pos, str(t)))

    def unrendered_template(self, t, name, args, ctx):
        assert isinstance(ctx, str)
        assert isinstance(t, str)
        assert isinstance(name, str)
        assert isinstance(args, (list, tuple))
        for x in args:
            assert isinstance(x, str)
        self.debug("unrenderable template: {}: {}".format(ctx, t))
        self.unrendered_template_counts[name] += 1
        argnames = tuple(sorted(args))
        argnames = ", ".join(argnames)
        if len(self.unrendered_template_samples[name][argnames]) < 2:
            self.unrendered_template_samples[name][argnames].append(
                (self.language, self.pos, str(t)))

    def unknown_value(self, t, value):
        assert isinstance(value, str)
        self.error("unknown value {!r} in {}".format(value, t))
        name = t.name.strip()
        self.unknown_value_counts[self.language][name][value] += 1
