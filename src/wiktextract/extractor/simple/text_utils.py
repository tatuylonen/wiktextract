import re

from .section_titles import POS_DATA

# In Simple English Wiktionary, these level-3 (===) headings also seem to
# start logical sections; -> `preposition`
SECTION_STARTERS = (
    "word parts",
    "pronunciation",
    "description",
    "etymology",
)

# (==) (Heading text) ==
# the `&` is for stuff like "Acronym & Initialism"
HEADING_RE = re.compile(r"(?m)^(=+)\s*((\w+\s(&\s+)?)*\w+)\s*=+$")

# A regex for detecting a heading that starts like a POS: "Noun 1"
POS_STARTS_RE = re.compile(
    r"(?i)("
    + r"|".join(sorted((re.escape(s) for s in POS_DATA.keys()), key=len))
    + r")(\s+\d+)?"
)

# Quick regex to find the template name in text
TEMPLATE_NAME_RE = re.compile(r"{{\s*((w+\s+)*\w+)\s*(\||}})")

# List all the templates registered to POS headings
POS_TEMPLATE_NAMES: dict[str, str] = {}

for pos, templates in POS_DATA.items():
    POS_TEMPLATE_NAMES.update({tn: pos for tn in templates["templates"]})

