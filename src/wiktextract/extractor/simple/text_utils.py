import re

from .section_titles import POS_DATA

# A regex for detecting a heading that starts like a POS: "Noun 1"
POS_STARTS_RE = re.compile(
    r"(?i)("
    + r"|".join(sorted((re.escape(s) for s in POS_DATA.keys()), key=len))
    + r")(\s+\d+)?"
)

# List all the templates registered to POS headings
POS_TEMPLATE_NAMES: dict[str, str] = {}

for pos, templates in POS_DATA.items():
    POS_TEMPLATE_NAMES.update({tn: pos for tn in templates["templates"]})

