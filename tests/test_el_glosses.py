from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


class TestElGlosses(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="el"),
            WiktionaryConfig(
                dump_file_lang_code="el",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_el_glosses1(self) -> None:
        self.wxr.wtp.start_page("brain")
        data = WordEntry(lang="English", lang_code="en", word="brain")
        root = self.wxr.wtp.parse(
            """==={{ουσιαστικό|en}}===
'''φώσφορος'''
# foo
#: ''An operation was done to remove a tumor from the patient’s '''brain'''.''
#:: Έγινε επέμβαση για αφαίρεση όγκου από τον '''εγκέφαλο''' του ασθενή.
# (''πληθυντικός'') τα [[μυαλό|μυαλά]], το μυαλό ζώων που χρησιμοποιείται από τους ανθρώπους ως τροφή
#: ''lamb '''brains''''' - αρνίσια '''μυαλά'''
# το [[μυαλό]], η ικανότητα να μαθαίνω γρήγορα και να σκέφτομαι τα πράγματα με λογικό και έξυπνο τρόπο
#: ''Use your '''brain'''!''
#:: Βάλε το '''μυαλό''' σου να δουλέψει!
#: ''If you had any '''brains''', you wouldn’t be in this mess.''
#:: Αν είχες '''μυαλά''' δε θα βρισκόσουν σ΄ αυτά τα χάλια.
# ανεπίσημο το [[μυαλό]], έξυπνος άνθρωπος
#: ''He’s a big '''brain'''.''
#:: Είναι κάποιος μεγάλο '''μυαλό'''.
# ('''''the brains''', ενικός'') ο [[εγκέφαλος]], το [[μυαλό]], το πιο έξυπνο άτομο σε μια συγκεκριμένη ομάδα· το άτομο που είναι υπεύθυνο να σκεφτεί και να οργανώσει κάτι
#: ''He is '''the brains''' of the company.''
#:: Είναι '''ο εγκέφαλος''' της εταιρείας.
#: ''He was '''the brains''' behind the plot.''
#:: Ήταν '''το μυαλό''' της συνωμοσίας.
"""
        )
        pos_node = root.children[0]
        process_pos(
            self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[]
        )
        # print(f"{data.model_dump(exclude_defaults=True)}")
        test = {
            "word": "brain",
            "forms": [{"form": "φώσφορος"}],
            "lang_code": "en",
            "lang": "English",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["foo"],
                    "examples": [
                        {
                            "text": "An operation was done to remove a tumor from the patient’s brain.",
                            "translation": "Έγινε επέμβαση για αφαίρεση όγκου από τον εγκέφαλο του ασθενή.",
                        }
                    ],
                },
                {
                    "glosses": [
                        "τα μυαλά, το μυαλό ζώων που χρησιμοποιείται από τους ανθρώπους ως τροφή"
                    ],
                    "raw_tags": ["πληθυντικός"],
                    "examples": [{"text": "lamb brains - αρνίσια μυαλά"}],
                },
                {
                    "glosses": [
                        "το μυαλό, η ικανότητα να μαθαίνω γρήγορα και να σκέφτομαι τα πράγματα με λογικό και έξυπνο τρόπο"
                    ],
                    "examples": [
                        {
                            "text": "Use your brain!",
                            "translation": "Βάλε το μυαλό σου να δουλέψει!",
                        },
                        {
                            "text": "If you had any brains, you wouldn’t be in this mess.",
                            "translation": "Αν είχες μυαλά δε θα βρισκόσουν σ΄ αυτά τα χάλια.",
                        },
                    ],
                },
                {
                    "glosses": ["ανεπίσημο το μυαλό, έξυπνος άνθρωπος"],
                    "examples": [
                        {
                            "text": "He’s a big brain.",
                            "translation": "Είναι κάποιος μεγάλο μυαλό.",
                        }
                    ],
                },
                {
                    "glosses": [
                        "ο εγκέφαλος, το μυαλό, το πιο έξυπνο άτομο σε μια συγκεκριμένη ομάδα· το άτομο που είναι υπεύθυνο να σκεφτεί και να οργανώσει κάτι"
                    ],
                    "raw_tags": ["ενικός"],
                    "examples": [
                        {
                            "text": "He is the brains of the company.",
                            "translation": "Είναι ο εγκέφαλος της εταιρείας.",
                        },
                        {
                            "text": "He was the brains behind the plot.",
                            "translation": "Ήταν το μυαλό της συνωμοσίας.",
                        },
                    ],
                    "related": [{"word": "the brains"}],
                },
            ],
        }
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped, test)
