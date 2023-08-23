# Definition of the configuration object for Wiktionary data extraction.
# The same object is also used for collecting statistics.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE or https://ylonen.org

import collections
import json
from importlib.resources import files
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from wikitextprocessor.core import StatsData


def int_dict():
    return collections.defaultdict(int)


def int_dict_dict():
    return collections.defaultdict(int_dict)


def list_dict():
    return collections.defaultdict(list)


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
        "LANGUAGES_BY_NAME",
        "LANGUAGES_BY_CODE",
        "FORM_OF_TEMPLATES",
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
        self.init_languages()
        self.set_attr_from_json("ZH_PRON_TAGS", "zh_pron_tags.json")
        if dump_file_lang_code == "zh":
            self.set_attr_from_json(
                "FORM_OF_TEMPLATES", "form_of_templates.json"
            )

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
            "capture_descendants": self.capture_descendants,
            "verbose": self.verbose,
            "expand_tables": self.expand_tables,
        }

    def to_return(self) -> "StatsData":
        return {
            "num_pages": self.num_pages,
            "language_counts": self.language_counts,
            "pos_counts": self.pos_counts,
            "section_counts": self.section_counts,
        }

    def merge_return(self, ret):
        assert isinstance(ret, dict)
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

    def init_languages(self):
        def canon_warn(name, use_code, not_use_code):
            print(
                f"WARNING: Non-unique language canonical name '{name}'."
                f" Mapping to '{use_code}' instead of '{not_use_code}'."
            )

        def alias_info(name, new_code, kind, old_code, use_code, not_use_code):
            if self.verbose:
                print(
                    f"Language alias '{name}' for code '{new_code}'"
                    f" is already a{kind} for {old_code}."
                    f" Mapping to '{use_code}' instead of '{not_use_code}'."
                )

        self.set_attr_from_json("LANGUAGES_BY_CODE", "languages.json")

        self.LANGUAGES_BY_NAME = {}

        # add canonical names first to avoid overwriting them
        canonical_names = {}
        for lang_code, lang_names in self.LANGUAGES_BY_CODE.items():
            canonical_name = lang_names[0]
            if canonical_name in canonical_names:
                lang_code0 = canonical_names[canonical_name]
                if len(lang_code) < len(lang_code0):
                    canon_warn(canonical_name, lang_code, lang_code0)
                    canonical_names[canonical_name] = lang_code
                    self.LANGUAGES_BY_NAME[canonical_name] = lang_code
                else:
                    canon_warn(canonical_name, lang_code0, lang_code)
            else:
                canonical_names[canonical_name] = lang_code
                self.LANGUAGES_BY_NAME[canonical_name] = lang_code

        # add other names
        for lang_code, lang_names in self.LANGUAGES_BY_CODE.items():
            for lang_name in lang_names[1:]:
                if lang_name in canonical_names:
                    lang_code0 = canonical_names[lang_name]
                    alias_info(
                        lang_name,
                        lang_code,
                        " canonical name",
                        lang_code0,
                        lang_code0,
                        lang_code,
                    )
                    continue
                if lang_name in self.LANGUAGES_BY_NAME:
                    lang_code0 = self.LANGUAGES_BY_NAME[lang_name]
                    if len(lang_code) < len(lang_code0):
                        alias_info(
                            lang_name,
                            lang_code,
                            "n alias",
                            lang_code0,
                            lang_code,
                            lang_code0,
                        )
                        self.LANGUAGES_BY_NAME[lang_name] = lang_code
                    else:
                        alias_info(
                            lang_name,
                            lang_code,
                            "n alias",
                            lang_code0,
                            lang_code0,
                            lang_code,
                        )
                else:
                    self.LANGUAGES_BY_NAME[lang_name] = lang_code
