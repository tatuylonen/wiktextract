# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE or https://ylonen.org

import collections
import json
import sys
from typing import Callable, Optional

from wikitextprocessor.core import CollatedErrorReturnData

if sys.version_info < (3, 10):
    from importlib_resources import files
else:
    from importlib.resources import files


class WiktionaryConfig:
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
        "capture_descendants",
        "expand_tables",
        "verbose",
        "num_pages",
        "language_counts",
        "pos_counts",
        "section_counts",
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
        "FR_FORM_TABLES",
        "DE_FORM_TABLES",
        "FORM_OF_TEMPLATES",
        "analyze_templates",
        "extract_thesaurus_pages",
    )

    def __init__(
        self,
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
        capture_descendants=True,
        verbose=False,
        expand_tables=False,
    ):
        if capture_language_codes is not None:
            assert isinstance(capture_language_codes, (list, tuple, set))
            for x in capture_language_codes:
                assert isinstance(x, str)
        assert capture_language_codes is None or isinstance(
            capture_language_codes, (list, tuple, set)
        )
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
        self.capture_descendants = capture_descendants
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
        self.redirects = {}
        self.data_folder = files("wiktextract") / "data" / dump_file_lang_code
        self.init_subtitles()
        self.set_attr_from_json("ZH_PRON_TAGS", "zh_pron_tags.json")
        if dump_file_lang_code == "zh":
            self.set_attr_from_json(
                "FORM_OF_TEMPLATES", "form_of_templates.json"
            )
        self.analyze_templates = True  # find templates that need pre-expand
        self.extract_thesaurus_pages = True
        self.load_edition_settings()

    def merge_return(self, ret: CollatedErrorReturnData):
        if "num_pages" in ret:
            self.num_pages += ret["num_pages"]
            for k, v in ret["language_counts"].items():
                self.language_counts[k] += v
            for k, v in ret["pos_counts"].items():
                self.pos_counts[k] += v
            for k, v in ret["section_counts"].items():
                self.section_counts[k] += v
        if "errors" in ret:
            self.errors.extend(ret.get("errors", []))
            self.warnings.extend(ret.get("warnings", []))
            self.debugs.extend(ret.get("debugs", []))

    def set_attr_from_json(
        self,
        attr_name: str,
        file_name: str,
        convert_func: Optional[Callable] = None,
    ) -> None:
        file_path = self.data_folder.joinpath(file_name)
        json_value = {}
        if file_path.exists():
            with file_path.open(encoding="utf-8") as f:
                json_value = json.load(f)
                if convert_func:
                    json_value = convert_func(json_value)
        setattr(self, attr_name, json_value)

    def init_subtitles(self) -> None:
        self.set_attr_from_json("LINKAGE_SUBTITLES", "linkage_subtitles.json")
        self.set_attr_from_json("POS_SUBTITLES", "pos_subtitles.json")
        self.POS_TYPES = set(x["pos"] for x in self.POS_SUBTITLES.values())
        for k, v in self.POS_SUBTITLES.items():
            if "tags" in v:
                assert isinstance(v["tags"], (list, tuple))
        self.set_attr_from_json("OTHER_SUBTITLES", "other_subtitles.json")

    def load_edition_settings(self):
        file_path = self.data_folder / "config.json"
        if file_path.exists():
            with file_path.open(encoding="utf-8") as f:
                for key, value in json.load(f).items():
                    setattr(self, key, value)
