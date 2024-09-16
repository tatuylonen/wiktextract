import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.page import clean_node
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class WiktExtractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path,
            self.wxr.thesaurus_db_conn,  # type:ignore[arg-type]
        )

    def test_bold_node_in_link(self):
        # https://en.wiktionary.org/wiki/ちゃんねる
        # GitHub issue: tatuylonen/wikitextprocessor#170
        wikitext = "{{ja-usex|[[w:ja:2ちゃんねる|2'''ちゃんねる''']]}}"
        self.wxr.wtp.add_page(
            "Template:ja-usex", 10, "{{#invoke:ja-usex|show}}"
        )
        self.wxr.wtp.add_page(
            "Module:ja-usex",
            828,
            """
            local export = {}

            function export.show(frame)
              local first_arg = frame:getParent().args[1]
              if first_arg == "[[w:ja:2ちゃんねる|2'''ちゃんねる''']]" then
                -- bold wikitext shouldn't be removed
                return first_arg .. ", ''italic''"
              end
              return "failed"
            end

            return export
            """,
        )
        self.wxr.wtp.start_page("")
        tree = self.wxr.wtp.parse(wikitext)
        # bold and italic nodes should be converted to plain text
        self.assertEqual(
            clean_node(self.wxr, None, tree.children), "2ちゃんねる, italic"
        )


    def test_clean_node_lists(self):
        from wiktextract.page import clean_node
        wikitext = """
# line 1
## line 2
#: example 1
#: example 2
    """
        self.wxr.wtp.start_page("test")
        tree = self.wxr.wtp.parse(wikitext)
        print(tree)
        cleaned = clean_node(self.wxr, None, tree)
        print(cleaned)
        self.assertEqual(cleaned, wikitext)
