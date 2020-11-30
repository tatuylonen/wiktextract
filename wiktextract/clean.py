# This file contains code to clean Wiktionary annotations from a string and to
# produce plain text from it, typically for glossary entries but this is also
# called for various other data to produce clean strings.
#
# This file also contains code for cleaning qualifiers for the "tags" field.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import html
from .config import WiktionaryConfig

######################################################################
# Cleaning values into plain text.
######################################################################

def clean_value(config, title, no_strip=False):
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(title, str)
    title = re.sub(r"\{\{[^}]+\}\}", "", title)
    # Remove tables
    title = re.sub(r"(?s)\{\|.*?\|\}", " ", title)
    # Remove references (<ref>...</ref>).
    title = re.sub(r"(?is)<\s*ref\s*[^>]*?>\s*.*?<\s*/\s*ref\s*>\n*", "", title)
    # Replace <br/> by comma space (it is used to express alternatives in some
    # declensions)
    title = re.sub(r"(?si)<\s*br\s*/?>\n*", ", ", title)
    # Change <div> and </div> to newlines
    title = re.sub(r"(?si)<\s*/?\s*div\b[^>]*>", "\n", title)
    # Change <sup> ... </sup> to ^
    title = re.sub(r"(?si)<\s*sup\b[^>]*>(.*?)<\s*/\s*sup\s*>",
                   r"^\1", title)
    # Remove any remaining HTML tags.
    title = re.sub(r"(?s)<\s*[^/][^>]*>\s*", "", title)
    title = re.sub(r"(?s)<\s*/\s*[^>]+>\n*", "", title)
    # Replace links by their text
    title = re.sub(r"(?s)\[\[\s*Category:([^]]+)\]\]", r"", title)
    title = re.sub(r"(?s)\[\[([^]|]+)\|([^]|]+)\]\]", r"\2", title)
    title = re.sub(r"(?s)\[\[([a-zA-z0-9]+:)?([^]|]+)(\s*\([^])|]*\)\s*)?"
                   r"\|\]\]",
                   r"\2", title)
    title = re.sub(r"(?s)\[\[([^]|]+)\]\]", r"\1", title)
    # Replace remaining HTML links by the URL.
    title = re.sub(r"\[https?:[^]\s]+\s+([^]]+?)\s*\]", r"\1", title)
    title = re.sub(r"\[(https?:[^]]+)\]", r"", title)
    # Replace HTML entities
    title = html.unescape(title)
    # Remove italic and bold
    title = re.sub(r"''+", r"", title)
    title = re.sub("\xa0", " ", title)  # nbsp
    # This unicode quote seems to be used instead of apostrophe quite randomly
    # (about 4% of apostrophes in English entries, some in Finnish entries).
    title = re.sub("\u2019", "'", title)  # Note: no r"..." here!
    # Replace strange unicode quotes with normal quotes
    title = re.sub(r"”", '"', title)
    # Replace unicode long dash by normal dash
    title = re.sub(r"–", "-", title)
    # Replace whitespace sequences by a single space.
    title = re.sub(r"\s+", " ", title)
    # Remove whitespace before periods and commas etc
    title = re.sub(r" ([.,;:!?)])", r"\1", title)
    # Strip surrounding whitespace.
    if not no_strip:
        title = title.strip()
    return title
