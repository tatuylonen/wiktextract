# Tests for datautils.py
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.datautils import split_slashes
from wiktextract.extractor.share import create_audio_url_dict
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_slashes1(self):
        ret = split_slashes(self.wxr, "foo ")
        self.assertEqual(ret, ["foo"])

    def test_slashes2(self):
        ret = split_slashes(self.wxr, "foo bar /  zap")
        self.assertEqual(ret, ["foo bar", "zap"])

    def test_slashes3(self):
        ret = split_slashes(self.wxr, "foo/bar/zap ")
        self.assertEqual(ret, ["foo", "bar", "zap"])

    def test_slashes4(self):
        ret = split_slashes(self.wxr, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes5(self):
        ret = split_slashes(self.wxr, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes6(self):
        ret = split_slashes(self.wxr, "foo/bar zap a/b")
        # print("ret:", ret)
        self.assertEqual(
            ret, ["bar zap a", "bar zap b", "foo zap a", "foo zap b"]
        )

    def test_slashes7(self):
        self.wxr.wtp.add_page("foo", 0, "x")
        self.assertTrue(self.wxr.wtp.page_exists("foo"))
        ret = split_slashes(self.wxr, "foo/bar zap a/b")
        # XXX this response is still perhaps not what we want with the page
        # existing
        self.assertEqual(
            ret, ["bar zap a", "bar zap b", "foo zap a", "foo zap b"]
        )

    def test_audio_transcode_url(self):
        sound_data = create_audio_url_dict(
            "LL-Q150 (fra)-DenisdeShawi-bonjour.wav \u200e"
        )
        self.assertEqual(
            sound_data,
            {
                "audio": "LL-Q150 (fra)-DenisdeShawi-bonjour.wav",
                "wav_url": "https://commons.wikimedia.org/wiki/Special:FilePath/LL-Q150 (fra)-DenisdeShawi-bonjour.wav",
                "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/e/e1/LL-Q150_(fra)-DenisdeShawi-bonjour.wav/LL-Q150_(fra)-DenisdeShawi-bonjour.wav.mp3",
                "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/e/e1/LL-Q150_(fra)-DenisdeShawi-bonjour.wav/LL-Q150_(fra)-DenisdeShawi-bonjour.wav.ogg",
            },
        )

        sound_data = create_audio_url_dict("File:Fr-BonjourF.oga")
        self.assertEqual(
            sound_data,
            {
                "audio": "Fr-BonjourF.oga",
                "oga_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fr-BonjourF.oga",
                "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/b9/Fr-BonjourF.oga/Fr-BonjourF.oga.mp3",
            },
        )

        sound_data = create_audio_url_dict("Qc-Vancouver.ogv")
        self.assertEqual(sound_data["audio"], "Qc-Vancouver.oga")

        sound_data = create_audio_url_dict("De-Fisch.OGG")
        self.assertEqual(
            sound_data,
            {
                "audio": "De-Fisch.OGG",
                "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/De-Fisch.OGG",
                "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/0/0f/De-Fisch.OGG/De-Fisch.OGG.mp3",
            },
        )
