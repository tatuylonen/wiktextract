import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.form_line import (
    extract_form_line,
    process_zh_mot_template,
)
from wiktextract.wxr_context import WiktextractContext


class TestFormLine(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    @patch(
        "wiktextract.extractor.fr.pronunciation.clean_node",
        return_value="/lə nɔ̃/",
    )
    def test_ipa(self, mock_clean_node):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("'''le nom''' {{pron|lə nɔ̃|fr}}")
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(page_data, [{"sounds": [{"ipa": "/lə nɔ̃/"}]}])

    @patch(
        "wiktextract.extractor.fr.form_line.clean_node", return_value="masculin"
    )
    def test_gender(self, mock_clean_node):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("'''le nom''' {{m}}")
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(page_data, [{"tags": ["masculin"]}])

    def test_equiv_pour(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "{{équiv-pour|une femme|autrice|auteure|auteuse|lang=fr}}"
        )
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(
            page_data,
            [
                {
                    "forms": [
                        {
                            "form": "autrice",
                            "tags": ["pour une femme"],
                            "source": "form line template 'équiv-pour'",
                        },
                        {
                            "form": "auteure",
                            "tags": ["pour une femme"],
                            "source": "form line template 'équiv-pour'",
                        },
                        {
                            "form": "auteuse",
                            "tags": ["pour une femme"],
                            "source": "form line template 'équiv-pour'",
                        },
                    ]
                }
            ],
        )

    def test_zh_mot(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:zh-mot", 10, body="{{lang}} {{pron}}")
        self.wxr.wtp.add_page("Modèle:lang", 10, body="mǎ")
        self.wxr.wtp.add_page("Modèle:pron", 10, body="\\ma̠˨˩˦\\")
        root = self.wxr.wtp.parse("{{zh-mot|马|mǎ}}")
        page_data = [defaultdict(list)]
        process_zh_mot_template(self.wxr, root.children[0], page_data)
        self.assertEqual(
            page_data,
            [
                {
                    "sounds": [
                        {"tags": ["Pinyin"], "zh-pron": "mǎ"},
                        {"ipa": "\\ma̠˨˩˦\\"},
                    ]
                }
            ],
        )

    def test_ipa_location_tag(self):
        # https://fr.wiktionary.org/wiki/basket-ball
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:pron", 10, body="{{{1}}}")
        self.wxr.wtp.add_page("Modèle:FR", 10, body="(France)")
        self.wxr.wtp.add_page("Modèle:CA", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:m", 10, body="masculin")
        root = self.wxr.wtp.parse(
            "{{pron|bas.kɛt.bol|fr}} {{FR|nocat=1}} ''ou'' {{pron|bas.kɛt.bɔl|fr}} {{FR|nocat=1}} ''ou'' {{pron|bas.kɛt.bɑl|fr}} {{CA|nocat=1}} {{m}}"
        )
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(
            page_data,
            [
                {
                    "tags": ["masculin"],
                    "sounds": [
                        {"ipa": "bas.kɛt.bol", "tags": ["France"]},
                        {"ipa": "bas.kɛt.bɔl", "tags": ["France"]},
                        {"ipa": "bas.kɛt.bɑl", "tags": ["Canada"]},
                    ],
                }
            ],
        )

    def test_template_in_pron_argument(self):
        # https://fr.wiktionary.org/wiki/minéral argileux
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:pron", 10, body="{{{1}}}")
        self.wxr.wtp.add_page("Modèle:liaison", 10, body="‿")
        root = self.wxr.wtp.parse(
            "'''minéral argileux''' {{pron|mi.ne.ʁa.l{{liaison|fr}}aʁ.ʒi.lø|fr}}"
        )
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(
            page_data,
            [{"sounds": [{"ipa": "mi.ne.ʁa.l‿aʁ.ʒi.lø"}]}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="''(pour un homme, on dit'' : <bdi lang=\"fr\" xml:lang=\"fr\" class=\"lang-fr\">[[auteur#fr|auteur]]</bdi> ; ''pour une personne non-binaire, on peut dire'' : <bdi lang=\"fr\" xml:lang=\"fr\" class=\"lang-fr\">[[autaire#fr|autaire]]</bdi>, <bdi lang=\"fr\" xml:lang=\"fr\" class=\"lang-fr\">[[auteurice#fr|auteurice]]</bdi>, <bdi lang=\"fr\" xml:lang=\"fr\" class=\"lang-fr\">[[auteur·ice#fr|auteur·ice]]</bdi>'')''"
    )
    def test_complex_equiv_pour_template(self, mock_node_to_wikitext):
        self.maxDiff = None
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse(
            "{{équiv-pour|un homme|auteur|2egenre=une personne non-binaire|2egenre1=autaire|2egenre2=auteurice|2egenre3=auteur·ice|lang=fr}}"
        )
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(
            page_data,
            [
                {
                    "forms": [
                        {
                            "form": "auteur",
                            "tags": ["pour un homme, on dit"],
                            "source": "form line template 'équiv-pour'",
                        },
                        {
                            "form": "autaire",
                            "tags": [
                                "pour une personne non-binaire, on peut dire"
                            ],
                            "source": "form line template 'équiv-pour'",
                        },
                        {
                            "form": "auteurice",
                            "tags": [
                                "pour une personne non-binaire, on peut dire"
                            ],
                            "source": "form line template 'équiv-pour'",
                        },
                        {
                            "form": "auteur·ice",
                            "tags": [
                                "pour une personne non-binaire, on peut dire"
                            ],
                            "source": "form line template 'équiv-pour'",
                        },
                    ]
                }
            ],
        )
