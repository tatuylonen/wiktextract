import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.inflection import parse_inflection_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        self.wxr.wtp.start_subsection(pos)
        tree = self.wxr.wtp.parse(text)
        data = {}
        parse_inflection_section(self.wxr, data, word, lang, pos, section, tree)
        return data

    def test_Japanese_verb_ja_conj_ex(self):
        # https://en.wiktionary.org/wiki/走る
        # {{ja-conj-ex|はし|る}}, simplified
        ret = self.xinfl(
            "走る",
            "Japanese",
            "verb",
            "Conjugation",
            """
<div class="inflection-table-wrapper inflection-box inflection-table-narrow inflection-table-collapsible inflection-table-collapsed no-vc tr-alongside flow-vertical" style="width: fit-content" data-toggle-category="inflection">
{| class="inflection-box-content"
|+ class="inflection-table-title" | Extended conjugation of ''hashiru'' "<span class="Jpan" lang="ja">走る</span>" (Class:&nbsp;[[Appendix:Japanese verbs#Five-grade_(五段_godan)|''godan'']] "pentagrade")
|-
|
<div class="inflection-table-wrapper inflection-table-no-title" style="width: fit-content" data-wikt-palette-p="magenta" data-toggle-category="inflection">
{| class="inflection-table"
|-
! colspan="3" class="outer" | (See [[Appendix:Japanese verbs]] and [[w:Japanese conjugation|Japanese conjugation]])
|-
! | [[Appendix:Japanese_glossary#ren'yōkei|''Ren’yōkei'']] ("continuative form")
| colspan="2" | <span class="Jpan" lang="ja">[[:走り#Japanese|走り]]</span> <span >[hashiri]</span>
|-
! colspan="3" class="outer" | Causative
|-
! | Verb stem
| colspan="2" | <span class="Jpan" lang="ja">走ら[[:せる#Etymology 1|せ]]</span> <span >[hashirase]</span>
|-
!
! | Positive
! | Negative
|-
! | Plain
| | <span class="Jpan" lang="ja">[[:走らせる#Japanese|走らせる]]</span> <span >[hashiraseru]</span><br>''short form:'' <span class="Jpan" lang="ja">[[:走らす#Japanese|走らす]]</span> <span >[hashirasu]</span>
| | <span class="Jpan" lang="ja">走らせ[[:ない#Japanese|ない]]</span> <span >[hashirasenai]</span>
|-
! | Polite
| | <span class="Jpan" lang="ja">走らせ[[:ます#Japanese|ます]]</span> <span >[hashirasemasu]</span>
| | <span class="Jpan" lang="ja">走らせ[[:ません#Japanese|ません]]</span> <span >[hashirasemasen]</span>
|-
! colspan="3" class="outer" | Causative passive
|-
!
! | Positive
! | Negative
|-
! | Plain
| | <span class="Jpan" lang="ja">[[:走らせられる#Japanese|走らせられる]]</span> <span >[hashiraserareru]</span><br>''colloquial:'' <span class="Jpan" lang="ja">[[:走らされる#Japanese|走らされる]]</span> <span >[hashirasareru]</span>
| | <span class="Jpan" lang="ja">走らせられ[[:ない#Japanese|ない]]</span> <span >[hashiraserarenai]</span>
|}
</div>
|}
</div>
""",
        )
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "走り",
                    "roman": "hashiri",
                    "source": "Conjugation",
                    "tags": ["continuative"],
                },
                {
                    "form": "走らせ",
                    "roman": "hashirase",
                    "source": "Conjugation",
                    "tags": ["causative", "stem"],
                },
                {
                    "form": "走らせる",
                    "roman": "hashiraseru",
                    "source": "Conjugation",
                    "tags": ["causative"],
                },
                {
                    "form": "走らす",
                    "roman": "hashirasu",
                    "source": "Conjugation",
                    "tags": ["causative", "short-form"],
                },
                {
                    "form": "走らせない",
                    "roman": "hashirasenai",
                    "source": "Conjugation",
                    "tags": ["causative", "negative"],
                },
                {
                    "form": "走らせます",
                    "roman": "hashirasemasu",
                    "source": "Conjugation",
                    "tags": ["causative", "polite"],
                },
                {
                    "form": "走らせません",
                    "roman": "hashirasemasen",
                    "source": "Conjugation",
                    "tags": ["causative", "negative", "polite"],
                },
                {
                    "form": "走らせられる",
                    "roman": "hashiraserareru",
                    "source": "Conjugation",
                    "tags": ["causative", "passive"],
                },
                {
                    "form": "走らされる",
                    "roman": "hashirasareru",
                    "source": "Conjugation",
                    "tags": ["causative", "colloquial", "passive"],
                },
                {
                    "form": "走らせられない",
                    "roman": "hashiraserarenai",
                    "source": "Conjugation",
                    "tags": ["causative", "negative", "passive"],
                },
            ],
        }
        self.assertEqual(expected, ret)
