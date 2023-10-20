import unittest

from wiktextract.extractor.de.utils import split_senseids


class TestDEUtils(unittest.TestCase):
    maxDiff = None

    def test_split_senseids(self):
        test_cases = [
            ("[1]", ["1"]),
            ("[1,2]", ["1", "2"]),
            ("[1, 2]", ["1", "2"]),
            ("[1, 2 ]", ["1", "2"]),
            ("[1-3]", ["1", "2", "3"]),
            ("[1, 3-5]", ["1", "3", "4", "5"]),
            ("[1, 3-4, 6]", ["1", "3", "4", "6"]),
            ("[1a]", ["1a"]),
            ("[1, 2a]", ["1", "2a"]),
            ("[1, 2a-3]", ["1", "2", "3"]),
        ]

        for test_case in test_cases:
            self.assertEqual(split_senseids(test_case[0]), test_case[1])
