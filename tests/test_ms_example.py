from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_italic(self):
        page_data = parse_page(
            self.wxr,
            "makan",
            """==Bahasa Melayu==
=== Takrifan ===
# memasukkan sesuatu ke dalam mulut
#: ''Jemputlah '''makan''' kuih ini.''
#:: ''.جمڤوتله '''ماکن''' کو<sup>ء</sup>يه اين''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "examples": [
                        {
                            "text": "Jemputlah makan kuih ini.",
                            "bold_text_offsets": [(10, 15)],
                            "translation": ".جمڤوتله ماکن کو^ءيه اين",
                            "bold_translation_offsets": [(9, 13)],
                        }
                    ],
                    "glosses": ["memasukkan sesuatu ke dalam mulut"],
                }
            ],
        )

    def test_cp(self):
        self.wxr.wtp.add_page(
            "Templat:ko-usex",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko"><span style="background&#45;color:#FEF8EA"><b>젓가락</b></span>으로 먹다</i>&nbsp;<dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn">'''jeotgarak'''euro meokda</i></dd><dd><span class="e-translation">makan menggunakan '''penyepit'''</span></dd></dl></div>[[Kategori:Kata bahasa Korea dengan contoh penggunaan|젓가락]]""",
        )
        page_data = parse_page(
            self.wxr,
            "젓가락",
            """==Bahasa Korea==
==== Kata nama ====
# [[penyepit]]
#* {{ko-usex|'''젓가락'''으로 먹다|makan menggunakan '''penyepit'''}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Kata bahasa Korea dengan contoh penggunaan"
                    ],
                    "examples": [
                        {
                            "text": "젓가락으로 먹다",
                            "bold_text_offsets": [(0, 3)],
                            "roman": "jeotgarakeuro meokda",
                            "bold_roman_offsets": [(0, 9)],
                            "translation": "makan menggunakan penyepit",
                            "bold_translation_offsets": [(18, 26)],
                        }
                    ],
                    "glosses": ["penyepit"],
                }
            ],
        )

    def test_lit(self):
        self.wxr.wtp.add_page(
            "Templat:uxi",
            10,
            """<span class="h-usage-example"><i class="Latn mention e-example" lang="de">die sterblichen '''Überreste'''</i> ― <span class="e-translation">'''jasad'''</span> (literally, “<span class="e-literally">badan orang mati</span>”)</span>[[Kategori:Kata bahasa Jerman dengan contoh penggunaan|HA]]""",
        )
        page_data = parse_page(
            self.wxr,
            "Überrest",
            """==Bahasa Jerman==
==== Kata nama ====
# [[mayat]]
#: {{uxi|de|die sterblichen '''Überreste'''|'''jasad'''|lit=badan orang mati}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Kata bahasa Jerman dengan contoh penggunaan"
                    ],
                    "examples": [
                        {
                            "text": "die sterblichen Überreste",
                            "bold_text_offsets": [(16, 25)],
                            "translation": "jasad",
                            "bold_translation_offsets": [(0, 5)],
                            "literal_meaning": "badan orang mati",
                        }
                    ],
                    "glosses": ["mayat"],
                }
            ],
        )

    def test_quote(self):
        self.wxr.wtp.add_page(
            "Templat:quote",
            10,
            """<div class="h-quotation"><span class="Latn e-quotation" lang="de">Nun steht fest&#x3A; Bei dem Skelett handelt es sich mit "an Sicherheit grenzender Wahrscheinlichkeit" um die '''Überreste''' der aus England stammenden Prinzessin, die mit dem damaligen König Otto dem Großen verheiratet war.</span><dl><dd><span class="e-translation">Sekarang sudah jelas: kerangka itu hampir pasti sebahagian daripada '''jenazah''' puteri dari England yang telah berkahwin dengan raja pada waktu itu, Otto the Great.</span></dd></dl></div>[[Kategori:Kata bahasa Jerman dengan petikan|UBERREST]]""",
        )
        page_data = parse_page(
            self.wxr,
            "Überrest",
            """==Bahasa Jerman==
==== Kata nama ====
# [[mayat]]
#* '''2010''' Jun 16, "Überreste von Königin Editha identifiziert", ''der Spiegel''.
#*: {{quote|de|Nun steht fest: Bei dem Skelett handelt es sich mit "an Sicherheit grenzender Wahrscheinlichkeit" um die '''Überreste''' der aus England stammenden Prinzessin, die mit dem damaligen König Otto dem Großen verheiratet war.|Sekarang sudah jelas: kerangka itu hampir pasti sebahagian daripada '''jenazah''' puteri dari England yang telah berkahwin dengan raja pada waktu itu, Otto the Great.}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["Kata bahasa Jerman dengan petikan"],
                    "examples": [
                        {
                            "text": 'Nun steht fest: Bei dem Skelett handelt es sich mit "an Sicherheit grenzender Wahrscheinlichkeit" um die Überreste der aus England stammenden Prinzessin, die mit dem damaligen König Otto dem Großen verheiratet war.',
                            "bold_text_offsets": [(105, 114)],
                            "translation": "Sekarang sudah jelas: kerangka itu hampir pasti sebahagian daripada jenazah puteri dari England yang telah berkahwin dengan raja pada waktu itu, Otto the Great.",
                            "bold_translation_offsets": [(68, 75)],
                            "ref": '2010 Jun 16, "Überreste von Königin Editha identifiziert", der Spiegel.',
                        }
                    ],
                    "glosses": ["mayat"],
                }
            ],
        )

    def test_quote_book(self):
        self.wxr.wtp.add_page(
            "Templat:quote-book",
            10,
            """<div class="citation-whole"><span class="cited-source"><span class="None" lang="und">'''2014'''</span>, Jonas Grethlein, “Das homerische Epos als Quelle, Überrest und Monument”, dalam <cite>Medien der Geschichte - Antikes Griechenland und Rom</cite>&lrm;<sup>[http://archiv.ub.uni-heidelberg.de/volltextserver/20459/1/Das%20homerische%20Epos.pdf]</sup>, <small><span class="neverexpand">[https://doi.org/10.11588%2Fheidok.00020459 →DOI]</span></small>:</span><dl><dd><div class="h-quotation"><span class="Latn e-quotation cited-passage" lang="de">Als ‚Quellen’ bezeichnet Droysen die „schriftlichen und mündlichen Nachrichten für die Erinnerungen“, als ‚'''Überreste'''’ solche Materialien, die nicht um der Überlieferung willen in die Welt gesetzt wurden, aber von uns als Zeugnisse ihrer Zeit interpretiert werden können.</span><dl><dd><span class="e-translation">Droysen menggunakan istilah ‘sumber’ untuk "mesej yang ditulis dan dituturkan demi kepentingan peringatan" dan ‘'''jasad'''’ untuk bahan yang tidak dicipta dengan niat tradisi tetapi masih boleh ditafsirkan sebagai saksi masa mereka.</span></dd></dl></div>[[Kategori:Kata bahasa Jerman dengan petikan|UBERREST]]</dd></dl></div>""",
        )
        page_data = parse_page(
            self.wxr,
            "Überrest",
            """==Bahasa Jerman==
==== Kata nama ====
# [[mayat]]
#* {{quote-book
|de
|year=2014
|doi=10.11588/heidok.00020459
|author=Jonas Grethlein
|title=Medien der Geschichte - Antikes Griechenland und Rom
|chapter=Das homerische Epos als Quelle, Überrest und Monument
|url=http://archiv.ub.uni-heidelberg.de/volltextserver/20459/1/Das%20homerische%20Epos.pdf
|passage= Als ‚Quellen’ bezeichnet Droysen die „schriftlichen und mündlichen Nachrichten für die Erinnerungen“, als ‚'''Überreste'''’ solche Materialien, die nicht um der Überlieferung willen in die Welt gesetzt wurden, aber von uns als Zeugnisse ihrer Zeit interpretiert werden können.
|translation=Droysen menggunakan istilah ‘sumber’ untuk "mesej yang ditulis dan dituturkan demi kepentingan peringatan" dan ‘'''jasad'''’ untuk bahan yang tidak dicipta dengan niat tradisi tetapi masih boleh ditafsirkan sebagai saksi masa mereka.}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["Kata bahasa Jerman dengan petikan"],
                    "examples": [
                        {
                            "text": "Als ‚Quellen’ bezeichnet Droysen die „schriftlichen und mündlichen Nachrichten für die Erinnerungen“, als ‚Überreste’ solche Materialien, die nicht um der Überlieferung willen in die Welt gesetzt wurden, aber von uns als Zeugnisse ihrer Zeit interpretiert werden können.",
                            "bold_text_offsets": [(107, 116)],
                            "translation": 'Droysen menggunakan istilah ‘sumber’ untuk "mesej yang ditulis dan dituturkan demi kepentingan peringatan" dan ‘jasad’ untuk bahan yang tidak dicipta dengan niat tradisi tetapi masih boleh ditafsirkan sebagai saksi masa mereka.',
                            "bold_translation_offsets": [(112, 117)],
                            "ref": "2014, Jonas Grethlein, “Das homerische Epos als Quelle, Überrest und Monument”, dalam Medien der Geschichte - Antikes Griechenland und Rom, →DOI:",
                        }
                    ],
                    "glosses": ["mayat"],
                }
            ],
        )
