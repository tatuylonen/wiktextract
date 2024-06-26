from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.linkage import (
    extract_linkages,
    extract_phrase_section,
    process_related_block_template,
)
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
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
                {
                    "word": "кацап",
                    "raw_tags": ["экзоэтнонимы"],
                    "sense_index": 1,
                },
                {
                    "word": "москаль",
                    "raw_tags": ["экзоэтнонимы"],
                    "sense_index": 1,
                },
                {
                    "word": "шурави",
                    "raw_tags": ["экзоэтнонимы"],
                    "sense_index": 1,
                },
                {
                    "word": "русня",
                    "tags": ["collective", "derogatory"],
                    "sense_index": 1,
                },
            ],
        )

    def test_related_words_sections(self):
        word_entry = WordEntry(
            word="вода", pos="noun", lang_code="ru", lang="Русский"
        )
        self.wxr.wtp.start_page("вода")
        self.wxr.wtp.add_page(
            "Шаблон:родств-блок",
            10,
            """{|
|class="block-head" | Ближайшее родство
|-
| colspan=2 class="block-body"|
* <span>уменьш.-ласк. формы:</span> [[водичечка]], [[водичка]]
|}""",
        )
        root = self.wxr.wtp.parse("{{родств-блок}}")
        process_related_block_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [r.model_dump(exclude_defaults=True) for r in word_entry.related],
            [
                {
                    "word": "водичечка",
                    "raw_tags": ["Ближайшее родство", "уменьш.-ласк. формы"],
                },
                {
                    "word": "водичка",
                    "raw_tags": ["Ближайшее родство", "уменьш.-ласк. формы"],
                },
            ],
        )

    def test_phrase_section(self):
        word_entry = WordEntry(
            word="вода", pos="noun", lang_code="ru", lang="Русский"
        )
        self.wxr.wtp.start_page("вода")
        self.wxr.wtp.add_page("Шаблон:-", 10, " — ")
        root = self.wxr.wtp.parse("""=== Фразеологизмы и устойчивые сочетания ===
* [[большая вода]]; [[прибылая вода]] / [[малая вода]]

==== Типичные сочетания ====
* вода [[литься|льётся]], [[плескаться|плещется]]; [[бить|бьёт]] ([[ключ]]ом, [[фонтан]]ом); [[брызгать|брызгает]]
* водой (реже{{-}}водою) [[захлёбываться|захлёбываются]]

==== Пословицы и поговорки ====
* [[обжёгшись на молоке, дуют на воду]]
** [[обжёгся на молоке, дует и на воду]]""")
        extract_phrase_section(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in word_entry.derived],
            [
                {"word": "большая вода"},
                {"word": "прибылая вода"},
                {"word": "малая вода"},
                {
                    "word": "вода льётся",
                    "raw_tags": ["Типичные сочетания"],
                },
                {
                    "word": "вода плещется",
                    "raw_tags": ["Типичные сочетания"],
                },
                {
                    "word": "вода бьёт (ключом, фонтаном)",
                    "raw_tags": ["Типичные сочетания"],
                },
                {
                    "word": "вода брызгает",
                    "raw_tags": ["Типичные сочетания"],
                },
                {
                    "word": "водой (реже — водою) захлёбываются",
                    "raw_tags": ["Типичные сочетания"],
                },
                {
                    "word": "обжёгшись на молоке, дуют на воду",
                    "raw_tags": ["Пословицы и поговорки"],
                },
                {
                    "word": "обжёгся на молоке, дует и на воду",
                    "raw_tags": ["Пословицы и поговорки"],
                },
            ],
        )

    def test_semantics_template(self):
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "красный",
                """= {{-ru-}} =

=== Морфологические и синтаксические свойства ===
{{прил ru 1*a/c"
|основа = кра́сн
|основа1 = кра́сен
|основа2 = красн
|тип=качественное
}}

=== Семантические свойства ===
==== Значение ====
# имеющий [[цвет]] [[кровь|крови]], [[червлёный]] {{семантика
|синонимы=алый, червонный
|антонимы=-
}}
# то же, что красивый {{семантика|синонимы=красивый}}""",
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "pos": "adj",
                    "word": "красный",
                    "senses": [
                        {"glosses": ["имеющий цвет крови, червлёный"]},
                        {"glosses": ["то же, что красивый"]},
                    ],
                    "synonyms": [
                        {"word": "алый", "sense_index": 1},
                        {"word": "червонный", "sense_index": 1},
                        {"word": "красивый", "sense_index": 2},
                    ],
                }
            ],
        )
