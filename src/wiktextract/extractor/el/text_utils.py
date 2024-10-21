import re

# Find digits at end of string, like "Noun 2".
# This is so commonly used that it needs to stop being a magic regex.
ENDING_NUMBER_RE = re.compile(r"\s*(\d+)$")

# Use with .strip() and checking for empty strings to eliminate stuff like
# ", ".
STRIP_PUNCTUATION = " \t\b,.;:*#-–()[]"
