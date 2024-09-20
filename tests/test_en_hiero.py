import unittest

from wiktextract.extractor.en.hieroglyphs import convert_hiero


class TagTests(unittest.TestCase):
    def test_phoneme(self):
        r = convert_hiero("x")
        self.assertEqual(r, '𓐍')

    def test_glyph(self):
        r = convert_hiero("T9")
        self.assertEqual(r, '𓌒')

    def test_bang1(self):
        r = convert_hiero("x!T9")
        self.assertEqual(r, '𓐍\n𓌒')

    def test_bang2(self):
        r = convert_hiero("x ! T9")
        self.assertEqual(r, '𓐍\n𓌒')

    def test_H_SPACE(self):
        r = convert_hiero("x H_SPACE y")
        self.assertEqual(r, '𓐍\xa0𓏭')

    def test_dot1(self):
        r = convert_hiero("x.y")
        self.assertEqual(r, '𓐍 𓏭')

    def test_dot2(self):
        r = convert_hiero("x . y")
        self.assertEqual(r, '𓐍 𓏭')

    def test_dot3(self):
        r = convert_hiero("x..y")
        self.assertEqual(r, '𓐍  𓏭')

    def test_doubledot(self):
        r = convert_hiero("x:y")
        self.assertEqual(r, '𓐍\U00013430𓏭')

    def test_asterisk(self):
        r = convert_hiero("x*y")
        self.assertEqual(r, '𓐍\U00013431𓏭')

    def test_asterisk_doubledot(self):
        r = convert_hiero("x*y:z")
        self.assertEqual(r, '\U00013437𓐍\U00013431𓏭\U00013438\U00013430𓊃')
