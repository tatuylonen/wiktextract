# Tests for miscellanous functions in the En extractor
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

from unittest import TestCase

from wiktextract.extractor.en.page import synch_splits_with_args


class MiscTests(TestCase):
    def test_synch_splits_with_args1(self) -> None:
        # "―" and "—" are the accepted hyphens (somewhere in the high
        # unicode range, so NOT "–", which looks identical...
        res = synch_splits_with_args("Foo ― Bar", {2: "Foo", 3: "Bar"})
        self.assertEqual(res, ["Foo", "Bar"])

    def test_synch_splits_with_args2(self) -> None:
        # The other accepted hyphen, "—"
        res = synch_splits_with_args("Foo — Bar", {2: "Foo", 3: "Bar"})
        self.assertEqual(res, ["Foo", "Bar"])

    def test_synch_splits_with_args3(self) -> None:
        # Somethings gone wrong
        res = synch_splits_with_args("Foo Bar", {2: "Foo", 3: "Bar"})
        self.assertEqual(res, None)

    def test_synch_splits_with_args4(self) -> None:
        # Result None because there's no " ― " in the arguments
        res = synch_splits_with_args("Foo ―  ― Bar", {2: "Foo", 3: "Bar"})
        self.assertEqual(res, None)

    def test_synch_splits_with_args5(self) -> None:
        res = synch_splits_with_args(
            "Foo ― baz ― Bar", {2: "Foo ― baz", 3: "Bar"}
        )
        self.assertEqual(res, ["Foo ― baz", "Bar"])

    def test_synch_splits_with_args6(self) -> None:
        res = synch_splits_with_args(
            "Foo ― baz ― Bar ― fizz", {2: "Foo ― baz", 3: "Bar ― fizz"}
        )
        self.assertEqual(res, ["Foo ― baz", "Bar ― fizz"])

    def test_synch_splits_with_args7(self) -> None:
        res = synch_splits_with_args(
            "Foo baz ― Bar ― fizz", {2: "Foo baz", 3: "Bar ― fizz"}
        )
        self.assertEqual(res, ["Foo baz", "Bar ― fizz"])

    def test_synch_splits_with_args8(self) -> None:
        res = synch_splits_with_args(
            "Foo baz ― Bar ― fizz ― three", {2: "Foo baz", 3: "Bar ― fizz"}
        )
        self.assertEqual(res, ["Foo baz", "Bar ― fizz", "three"])

    def test_synch_splits_with_args9(self) -> None:
        res = synch_splits_with_args(
            "Foo baz ― Bar ― fizz ― three ― four",
            {2: "Foo baz", 3: "Bar ― fizz"},
        )
        self.assertEqual(res, ["Foo baz", "Bar ― fizz", "three", "four"])

    def test_synch_splits_with_args10(self) -> None:
        res = synch_splits_with_args(
            "Foo baz ― Bar ― fizz ― fuzz ― three ― four",
            {2: "Foo baz", 3: "Bar ― fizz ― fuzz"},
        )
        self.assertEqual(res, ["Foo baz", "Bar ― fizz ― fuzz", "three", "four"])
