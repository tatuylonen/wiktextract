import re

TEXT_BOX_RE = re.compile(r"(?m)\n?{{text box start[^\n$]+{{text box end}}\n?")

def preprocess_text(text: str, page_title="") -> str:
    """Use simple text processing to rearrange the hierarchy of the page so that
    sections like `Word part` and `Pronunciation` will start a new main section.
    We do this by introducing LEVEL 1 headings, with a dummy title."""

    text = TEXT_BOX_RE.sub("", text)

    return text
