import re
import unicodedata
from typing import Generator, TypeAlias

from wikitextprocessor import WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Form, WordEntry
from .section_titles import (
    POS_HEADINGS,
    POS_HEADINGS_RE,
    SUBSECTION_HEADINGS,
    SUBSECTIONS_RE,
    Heading,
    POSName,
    Tags,
)
from .text_utils import normalized_int

# Ignorable templates that generate panels to the side, like
# Template:Wikipedia, or other meta-info like Template:see.
# Called 'panel templates' because they often generate panels.
PANEL_TEMPLATES: set[str] = set(
    [
        "interwiktionary",
        "stub",
        "wik",
        "wikipedia",
        "Wikipedia",
        "wikispecies",
        "wikiquote",
        "Wikiquote",
        "improve",
    ]
)

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
# PANEL_PREFIXES: set[str] = set()

# Additional templates to be expanded in the pre-expand phase
# XXX nothing here yet, add as needed if some template turns out to be
# problematic when unexpanded.
ADDITIONAL_EXPAND_TEMPLATES: set[str] = set()

# Names of templates used in etymology sections whose parameters we want
# to store in `etymology_templates`.
ETYMOLOGY_TEMPLATES: set[str] = set()

GREEK_LANGCODES = set(
    (
        "el",
        "grc",
        "el2",
        "el-crt",
        "el-cyp",
        "gkm",
        "gkm-cyp",
        "gkm-crt",
        "gmy",
        "gmy2",
        "grc-dor",
        "grc-ion",
        "grc-koi",
        "grk",
        "grk-ita",
        "grk-pro",
        "kath",
        "pnt",
        "pregrc",
        "tsd",
        "xme-old",
        "xmk",
    )
)


Title: TypeAlias = str

POSReturns: TypeAlias = list[
    tuple[POSName, Title, Tags, int, WikiNode, WordEntry]
]


def find_sections(
    wxr: WiktextractContext,
    nodes: list[WikiNode],
) -> Generator[tuple[Heading, POSName, Title, Tags, int, WikiNode], None, None]:
    for node in nodes:
        heading_title = clean_node(wxr, None, node.largs[0]).lower().strip()

        type, pos, heading_name, tags, num, ok = parse_lower_heading(
            wxr, heading_title
        )

        if num > 0:
            wxr.wtp.warning(
                f"Sub-sub-section is numbered: {heading_name}, {num=}",
                sortid="page/find_pos_sections_1",
            )
        yield type, pos, heading_name, tags, num, node


def parse_lower_heading(
    wxr: WiktextractContext, heading: str
) -> tuple[Heading, str, str, Tags, int, bool]:
    """Determine if a heading is for a part of speech or other subsection.
    Returns heading type enum, POS name or string data, list of tags and a
    success bool."""
    if m := POS_HEADINGS_RE.match(heading):
        pos, tags, num, ok = parse_pos_heading(wxr, heading, m)
        if ok:
            return Heading.POS, pos, heading, tags, num, True

    if m := SUBSECTIONS_RE.match(heading):
        section, section_name, tags, num, ok = parse_section_heading(
            wxr, heading, m
        )
        if ok:
            return section, section_name, heading, tags, num, True

    return Heading.Err, "", heading, [], -1, False


def parse_pos_heading(
    wxr: WiktextractContext, heading: str, m: re.Match[str]
) -> tuple[POSName, Tags, int, bool]:
    pos_str = m.group(1)
    rest = m.group(2)
    post_number = -1
    if rest:
        # logger.info(f"POS REST: '{rest}'")
        if rest.strip().isdigit():
            post_number = normalized_int(rest.strip())
            # logger.info(f"POST_NUMBER {post_number}")
    pos_data = POS_HEADINGS[pos_str]
    return pos_data["pos"], pos_data.get("tags", []), post_number, True


def parse_section_heading(
    wxr: WiktextractContext, heading: str, m: re.Match[str]
) -> tuple[Heading, str, Tags, int, bool]:
    subsection_str = m.group(1)
    rest = m.group(2)
    post_number = -1
    if rest:
        # logger.info(f"SUBSECTION REST: '{rest}'")
        if rest.strip().isdigit():
            post_number = normalized_int(rest.strip())
            # logger.info(f"POST_NUMBER {post_number}")
    section_data = SUBSECTION_HEADINGS[subsection_str]
    return (
        section_data["type"],
        subsection_str,
        section_data.get("tags", []),
        post_number,
        True,
    )


# https://stackoverflow.com/a/518232
def strip_accents(accented: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", accented)
        if unicodedata.category(c) != "Mn"
    )


def remove_duplicate_forms(
    wxr: WiktextractContext, forms: list[Form]
) -> list[Form]:
    """Check for identical `forms` and remove duplicates."""
    if not forms:
        return []
    new_forms = []
    for i, form in enumerate(forms):
        for comp in forms[i + 1 :]:
            if (
                form.form == comp.form
                and form.tags == comp.tags
                and form.raw_tags == comp.raw_tags
            ):
                break
                # basically "continue" for the outer for block in this case,
                # but this will not trigger the following else-block
        else:
            # No duplicates found in for loop (exited without breaking)
            new_forms.append(form)
    if len(forms) > len(new_forms):
        # wxr.wtp.debug("Found duplicate forms", sortid="simple/pos/32")
        return new_forms
    return forms
