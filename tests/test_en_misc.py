# Tests for miscellanous functions in the En extractor
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

from unittest import TestCase

from wiktextract.extractor.en.inflection import handle_mixed_lines
from wiktextract.extractor.en.page import TableContext, synch_splits_with_args


class MiscTests(TestCase):
    def setUp(self):
        self.ctx = TableContext()

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

    def test_mixed_lines_1(self) -> None:
        ret = handle_mixed_lines(["test"], self.ctx)
        expected = [("test", "", "")]
        self.assertEqual(ret, expected)

    def test_mixed_lines_2(self) -> None:
        ret = handle_mixed_lines([], self.ctx)
        expected: list[str] = []
        self.assertEqual(ret, expected)

    def test_mixed_lines_3a(self) -> None:
        ret = handle_mixed_lines(["test", "/test/"], self.ctx)
        expected = [("test", "", "/test/")]
        self.assertEqual(ret, expected)

    def test_mixed_lines_3(self) -> None:
        ret = handle_mixed_lines(["test", "tast", "/test/", "/tast/"], self.ctx)
        expected = [("test", "", "/test/"), ("tast", "", "/tast/")]
        self.assertEqual(ret, expected)

    def test_mixed_lines_4(self) -> None:
        ret = handle_mixed_lines(
            ["test", "tast", "tost", "/test/", "/tast/", "/tost/"], self.ctx
        )
        expected = [
            ("test", "", "/test/"),
            ("tast", "", "/tast/"),
            ("tost", "", "/tost/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_5(self) -> None:
        ret = handle_mixed_lines(
            [
                "test",
                "tast",
                "tost",
                "tust",
                "/test/",
                "/tast/",
                "/tost/",
                "/tust/",
            ],
            self.ctx,
        )
        expected = [
            ("test", "", "/test/"),
            ("tast", "", "/tast/"),
            ("tost", "", "/tost/"),
            ("tust", "", "/tust/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_6(self) -> None:
        ret = handle_mixed_lines(
            [
                "test",
                "tast",
                "tost",
                "tust",
                "tist",
                "/test/",
                "/tast/",
                "/tost/",
                "/tust/",
                "/tist/",
            ],
            self.ctx,
        )
        expected = [
            ("test", "", "/test/"),
            ("tast", "", "/tast/"),
            ("tost", "", "/tost/"),
            ("tust", "", "/tust/"),
            ("tist", "", "/tist/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_7(self) -> None:
        # many base forms, one ipa at the end
        ret = handle_mixed_lines(
            [
                "test",
                "tast",
                "tost",
                "tust",
                "tist",
                "/test/",
            ],
            self.ctx,
        )
        expected = [
            ("test", "", "/test/"),
            ("tast", "", "/test/"),
            ("tost", "", "/test/"),
            ("tust", "", "/test/"),
            ("tist", "", "/test/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_8(self) -> None:
        # one base form, many ipa at the end
        ret = handle_mixed_lines(
            [
                "test",
                "/test/",
                "/tast/",
                "/tost/",
                "/tust/",
            ],
            self.ctx,
        )
        expected = [
            ("test", "", "/test/"),
            ("test", "", "/tast/"),
            ("test", "", "/tost/"),
            ("test", "", "/tust/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_9(self) -> None:
        # one base form, many ipa at the end, even number of entries
        ret = handle_mixed_lines(
            [
                "test",
                "/test/",
                "/tast/",
                "/tost/",
                "/tust/",
                "/tist/",
            ],
            self.ctx,
        )
        expected = [
            ("test", "", "/test/"),
            ("test", "", "/tast/"),
            ("test", "", "/tost/"),
            ("test", "", "/tust/"),
            ("test", "", "/tist/"),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_10(self) -> None:
        # base-form other script, romanization, no ipa
        ret = handle_mixed_lines(
            [
                "дддд",
                "dddd",
            ],
            self.ctx,
        )
        expected = [
            ("дддд", "dddd", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_11(self) -> None:
        # base-form other script, romanization, no ipa
        ret = handle_mixed_lines(
            [
                "дддд",
                "ддддд",
                "дддддд",
                "dddd",
                "ddddd",
                "dddddd",
            ],
            self.ctx,
        )
        expected = [
            ("дддд", "dddd", ""),
            ("ддддд", "ddddd", ""),
            ("дддддд", "dddddd", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_12(self) -> None:
        # base-form other script, romanization, no ipa, alternating
        ret = handle_mixed_lines(
            [
                "дддд",
                "dddd",
                "ддддд",
                "ddddd",
                "дддддд",
                "dddddd",
            ],
            self.ctx,
        )
        expected = [
            ("дддд", "dddd", ""),
            ("ддддд", "ddddd", ""),
            ("дддддд", "dddddd", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_13(self) -> None:
        # georgian stuff where you have complex parentheses
        ka_table_context = TableContext(template_name="ka-decl-noun")
        ret = handle_mixed_lines(
            ["ამერიკის შეერთებულ შტატებს(ა) (ameriḳis šeertebul šṭaṭebs(a))"],
            ka_table_context,
        )
        expected = [
            (
                "ამერიკის შეერთებულ შტატებს",
                "ameriḳis šeertebul šṭaṭebs",
                "",
            ),
            (
                "ამერიკის შეერთებულ შტატებსა",
                "ameriḳis šeertebul šṭaṭebsa",
                "",
            ),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_14(self) -> None:
        # base-form other script, followed by different romanizations
        ret = handle_mixed_lines(
            [
                "дддд",
                "dddd",
                "ddddd",
            ],
            self.ctx,
        )
        expected = [
            ("дддд", "dddd", ""),
            ("дддд", "ddddd", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_15(self) -> None:
        # base-form other script, followed by different romanizations
        ret = handle_mixed_lines(
            [
                "дддд",
                "dddd",
                "ddddd",
                "dddddd",
            ],
            self.ctx,
        )
        expected = [
            ("дддд", "dddd", ""),
            ("дддд", "ddddd", ""),
            ("дддд", "dddddd", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_16(self) -> None:
        # parentheses on/off
        ret = handle_mixed_lines(
            [
                "kind(er)",
            ],
            self.ctx,
        )
        expected = [
            ("kind", "", ""),
            ("kinder", "", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_17(self) -> None:
        # parentheses complementary alternatives
        ret = handle_mixed_lines(
            [
                "lampai(den/tten)",
            ],
            self.ctx,
        )
        expected = [
            ("lampaiden", "", ""),
            ("lampaitten", "", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_18(self) -> None:
        # parentheses with following stuff
        ret = handle_mixed_lines(
            [
                "foo(bar)baz",
            ],
            self.ctx,
        )
        expected = [
            ("foobaz", "", ""),
            ("foobarbaz", "", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_19(self) -> None:
        # everything is in parens
        ret = handle_mixed_lines(
            [
                "(baz)",
            ],
            self.ctx,
        )
        expected = [
            ("(baz)", "", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_20(self) -> None:
        # leave tag text unhandled
        ret = handle_mixed_lines(
            [
                "(ergative)baz",
            ],
            self.ctx,
        )
        expected = [
            ("(ergative)baz", "", ""),
        ]
        self.assertEqual(ret, expected)

    def test_mixed_lines_21(self) -> None:
        # parentheses on/off
        ret = handle_mixed_lines(
            [
                "kind(er)",
                "lampai(den/tten)",
            ],
            self.ctx,
        )
        expected = [
            ("kind", "", ""),
            ("kinder", "", ""),
            ("lampaiden", "", ""),
            ("lampaitten", "", ""),
        ]
        self.assertEqual(ret, expected)
