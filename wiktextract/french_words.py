# Vocabulary of known French words.
#
# The vocabulary is mostly based on the 1M News Corpus from Wortschatz Leipzig (https://wortschatz.uni-leipzig.de/en/download/French), but we add some words
# and exclude some words.  These will likely need to be tweaked semi-frequently
# to add support for unrecognized sense descriptions.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import os


leipzig_words = []

my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "./data/fr/french_words.txt")
print(path)
with open(path, 'r') as f:
    for line in f:
        word = line.strip().split('\t')[1]
        leipzig_words.append(word)

additional_words = set([
    "'",
    "ʹ",
    ".",
    ";",
    ":",
    "!",
    "‘",
    "’",
    '"',
    '“',
    '”',
    '"',
    ',',
    "…",
    '...',
    '“.”',
    '—',
    '€',
])

# These words will never be treated as French words (overriding other
# considerations, not just membership in the set)
not_french_words = set([
    # This is a blacklist - these will not be treated as French words
    # even though they are in leipzig_words.  Adding a word on this list
    # generally makes it likely to be treated as a romanization.
])

# Construct a set of (most) French words.  Multi-word expressions where we
# do not want to include the components can also be put here space-separated.
french_words = (set(leipzig_words) |
                 # XXX the second words of species names add too much garbage
                 # now that we accept "french" more loosely.
                 # set(x for name in known_species for x in name.split())
                 additional_words) - not_french_words
