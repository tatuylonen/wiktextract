import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.datautils import split_at_comma_semi
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class DescTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_comma_semi1(self):
        self.assertEqual(split_at_comma_semi(""), [])

    def test_comma_semi2(self):
        self.assertEqual(split_at_comma_semi("foo bar"), ["foo bar"])

    def test_comma_semi3(self):
        self.assertEqual(split_at_comma_semi("foo bar, zappa"),
                         ["foo bar", "zappa"])

    def test_comma_semi4(self):
        self.assertEqual(split_at_comma_semi("foo , bar; zappa"),
                         ["foo", "bar", "zappa"])

    def test_comma_semi5(self):
        self.assertEqual(split_at_comma_semi("a (foo, bar); zappa"),
                         ["a (foo, bar)", "zappa"])

    def test_comma_semi5b(self):
        self.assertEqual(split_at_comma_semi("a (foo, bar)[1; zappa], z"),
                         ["a (foo, bar)[1; zappa]", "z"])

    def test_comma_semi6(self):
        self.assertEqual(split_at_comma_semi("foo bar, zappa",
                                             separators=[" "]),
                         ["foo", "bar,", "zappa"])

    def test_comma_semi7(self):
        self.assertEqual(split_at_comma_semi("foo or bar, zappa"),
                         ["foo or bar", "zappa"])

    def test_comma_semi8(self):
        self.assertEqual(split_at_comma_semi("foo or bar, zappa",
                                             extra=[" or "]),
                         ["foo", "bar", "zappa"])

    def test_comma_semi9(self):
        self.assertEqual(split_at_comma_semi("foo bar; zappa"),
                         ["foo bar", "zappa"])

    def test_comma_semi10(self):
        # Special unicode comma as separator
        self.assertEqual(split_at_comma_semi("foo bar，zappa"),
                         ["foo bar", "zappa"])

    def test_comma_semi11(self):
        self.assertEqual(split_at_comma_semi("foo bar,zappa;zip"),
                         ["foo bar", "zappa", "zip"])

    def test_comma_semi12(self):
        self.assertEqual(split_at_comma_semi("foo bar\nzappa"),
                         ["foo bar\nzappa"])

    def test_comma_semi13(self):
        self.assertEqual(split_at_comma_semi("foo bar\nzappa",
                                             extra=[r"\n"]),
                         ["foo bar", "zappa"])

    def test_comma_semi14(self):
        self.assertEqual(split_at_comma_semi("foo (bar\nzappa)",
                                             extra=[r"\n"]),
                         ["foo (bar\nzappa)"])
