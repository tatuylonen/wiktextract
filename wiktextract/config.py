# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE or https://ylonen.org

import json
import collections
from pathlib import Path


def int_dict():
    return collections.defaultdict(int)


def int_dict_dict():
    return collections.defaultdict(int_dict)


def list_dict():
    return collections.defaultdict(list)


class WiktionaryConfig(object):
    """This class holds configuration data for Wiktionary parsing."""

    __slots__ = (
        "dump_file_lang_code",
        "capture_language_codes",
        "capture_translations",
        "capture_pronunciation",
        "capture_linkages",
        "capture_compounds",
        "capture_redirects",
        "capture_examples",
        "capture_etymologies",
        "capture_inflections",
        "expand_tables",
        "verbose",
        "num_pages",
        "language_counts",
        "pos_counts",
        "section_counts",
        "thesaurus_data",
        "word",
        "errors",
        "warnings",
        "debugs",
        "redirects",
        "data_folder",
        "LINKAGE_SUBTITLES",
        "POS_SUBTITLES",
        "POS_TYPES",
        "OTHER_SUBTITLES",
        "ZH_PRON_TAGS",
        "LANGUAGES_BY_NAME",
        "LANGUAGES_BY_CODE"
    )

    def __init__(self,
                 dump_file_lang_code="en",
                 capture_language_codes=["en", "mul"],
                 capture_translations=True,
                 capture_pronunciation=True,
                 capture_linkages=True,
                 capture_compounds=True,
                 capture_redirects=True,
                 capture_examples=True,
                 capture_etymologies=True,
                 capture_inflections=True,
                 verbose=False,
                 expand_tables=False):
        if capture_language_codes is not None:
            assert isinstance(capture_language_codes, (list, tuple, set))
            for x in capture_language_codes:
                assert isinstance(x, str)
        assert (capture_language_codes is None or
                isinstance(capture_language_codes, (list, tuple, set)))
        assert capture_translations in (True, False)
        assert capture_pronunciation in (True, False)
        assert capture_linkages in (True, False)
        assert capture_compounds in (True, False)
        assert capture_redirects in (True, False)
        assert capture_etymologies in (True, False)
        self.dump_file_lang_code = dump_file_lang_code
        self.capture_language_codes = capture_language_codes
        self.capture_translations = capture_translations
        self.capture_pronunciation = capture_pronunciation
        self.capture_linkages = capture_linkages
        self.capture_compounds = capture_compounds
        self.capture_redirects = capture_redirects
        self.capture_examples = capture_examples
        self.capture_etymologies = capture_etymologies
        self.capture_inflections = capture_inflections
        self.verbose = verbose
        self.expand_tables = expand_tables
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
        self.thesaurus_data = {}
        self.redirects = {}

        self.data_folder = Path(__file__).parent.joinpath(f"data/{dump_file_lang_code}")
        self.init_subtitles()
        self.init_zh_pron_tags()
        self.init_languages()

    def to_kwargs(self):
        return {
            "dump_file_lang_code": self.dump_file_lang_code,
            "capture_language_codes": self.capture_language_codes,
            "capture_translations": self.capture_translations,
            "capture_pronunciation": self.capture_pronunciation,
            "capture_linkages": self.capture_linkages,
            "capture_compounds": self.capture_compounds,
            "capture_redirects": self.capture_redirects,
            "capture_examples": self.capture_examples,
            "capture_etymologies": self.capture_etymologies,
            "capture_inflections": self.capture_inflections,
            "verbose": self.verbose,
            "expand_tables": self.expand_tables
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
        self.errors.extend(ret.get("errors", []))
        self.warnings.extend(ret.get("warnings", []))
        self.debugs.extend(ret.get("debugs", []))

    def init_subtitles(self) -> None:
        with self.data_folder.joinpath("linkage_subtitles.json").open(encoding="utf-8") as f:
            self.LINKAGE_SUBTITLES = json.load(f)

        with self.data_folder.joinpath("pos_subtitles.json").open(encoding="utf-8") as f:
            self.POS_SUBTITLES = json.load(f)
            self.POS_TYPES = set(x["pos"] for x in self.POS_SUBTITLES.values())

        with self.data_folder.joinpath("other_subtitles.json").open(encoding="utf-8") as f:
            self.OTHER_SUBTITLES = json.load(f)

    def init_zh_pron_tags(self) -> None:
        with self.data_folder.joinpath("zh_pron_tags.json").open(encoding="utf-8") as f:
            self.ZH_PRON_TAGS = json.load(f)

    def init_languages(self):
        with self.data_folder.joinpath("languages.json").open(encoding="utf-8") as f:
            self.LANGUAGES_BY_CODE = json.load(f)
        self.LANGUAGES_BY_NAME = {}
        for lang_code, lang_names in self.LANGUAGES_BY_CODE.items():
            for lang_name in lang_names:
                self.LANGUAGES_BY_NAME[lang_name] = lang_code
