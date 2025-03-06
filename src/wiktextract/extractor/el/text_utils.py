import re
from unicodedata import normalize

# Find digits at end of string, like "Noun 2".
# This is so commonly used that it needs to stop being a magic regex.
ENDING_NUMBER_RE = re.compile(r"\s*(\d+)$")

# Use with .strip() and checking for empty strings to eliminate stuff like
# ", ".
STRIP_PUNCTUATION = " \t\b,.;:*#-–()[]"


def normalized_int(fancy_digits: str) -> int:
    try:
        return int(fancy_digits)
    except ValueError:
        return int(normalize("NFKC", fancy_digits))
