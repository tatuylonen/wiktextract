from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.linkage import extract_linkages
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"), WiktionaryConfig(dump_file_lang_code="ru")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_linkage(self):
        word_entry = WordEntry(
            word="русский", pos="adj", lang_code="ru", lang="Русский"
        )
        self.wxr.wtp.start_page("русский")
        self.wxr.wtp.add_page("Шаблон:помета", 10, "<span>экзоэтнонимы</span>")
        self.wxr.wtp.add_page(
            "Шаблон:собир.",
            10,
            '[[Викисловарь:Условные сокращения|<span title="собирательное">собир.</span>]]',
        )
        self.wxr.wtp.add_page(
            "Шаблон:уничиж.",
            10,
            '[[Викисловарь:Условные сокращения|<span title="уничижительное">уничиж.</span>]]',
        )
        root = self.wxr.wtp.parse(
            "# {{помета|экзоэтнонимы}}: [[кацап]], [[москаль]], [[шурави]]; {{собир.|-}}, {{уничиж.|-}}: [[русня]]"
        )
        extract_linkages(self.wxr, word_entry, "synonyms", root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in word_entry.synonyms],
            [
                {"word": "кацап", "raw_tags": ["экзоэтнонимы"]},
                {"word": "москаль", "raw_tags": ["экзоэтнонимы"]},
                {"word": "шурави", "raw_tags": ["экзоэтнонимы"]},
                {
                    "word": "русня",
                    "raw_tags": ["собирательное", "уничижительное"],
                },
            ],
        )
