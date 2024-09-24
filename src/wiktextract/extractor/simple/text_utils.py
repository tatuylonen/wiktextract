import re

from .section_titles import POS_HEADINGS

# List all the templates registered to POS headings
POS_TEMPLATE_NAMES: dict[str, str] = {}

for pos, templates in POS_HEADINGS.items():
    POS_TEMPLATE_NAMES.update({tn: pos for tn in templates["templates"]})

# This is so commonly used that it needs to stop being a magic regex
POS_ENDING_NUMBER_RE = re.compile(r"\s+(\d+)$")
