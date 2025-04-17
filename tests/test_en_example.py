from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestEnExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_two_ux_templates_in_one_list(self):
        self.wxr.wtp.add_page(
            "Template:uxi",
            10,
            """{{#switch:{{{3}}}
| eastward = <span class="h-usage-example"><i class="Latn mention e-example" lang="ang">[[:easteweard#Old&#95;English|ēaste'''weard''']]</i> ― <span class="e-translation">eastward</span></span>[[Category:Old English terms with usage examples|WEARD]]
| #default = <span class="h-usage-example"><i class="Latn mention e-example" lang="ang">[[:toweard#Old&#95;English|tō'''weard''']]</i> <span class="e-qualifier"><span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">adjective and noun</span><span class="ib-brac qualifier-brac">)</span></span> ― <span class="e-translation">future</span></span>[[Category:Old English terms with usage examples|WEARD]]
}}""",
        )
        page_data = parse_page(
            self.wxr,
            "-weard",
            """==Old English==
===Suffix===
# gloss
#: {{uxi|ang|[[ēasteweard|ēaste'''weard''']]|eastward}}, {{uxi|ang|[[tōweard|tō'''weard''']]|future|q=adjective and noun}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["examples"],
            [
                {
                    "text": "ēasteweard",
                    "bold_text_offsets": [(5, 10)],
                    "english": "eastward",
                    "type": "example",
                },
                {
                    "text": "tōweard",
                    "bold_text_offsets": [(2, 7)],
                    "english": "future",
                    "type": "example",
                    "raw_tags": ["adjective and noun"],
                },
            ],
        )
