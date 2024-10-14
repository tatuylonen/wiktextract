# Ignorable templates that generate panels to the side, like
# Template:Wikipedia, or other meta-info like Template:see.
# XXX Template:BE850 has data whether the word is part of the Swadesh? list,
# so that could probably be captured. It doesn't do anything but tell you
# "this is part of the 850" and the previous and next alphabetically ordered
# entries.
PANEL_TEMPLATES: set[str] = set(
    [
        "-",
        "also",
        "AVL",
        "AWL",
        "BE850",
        "BNC1000HW",
        "BNC1HW",
        "cleanup",
        "commonscat",
        "Commons category",
        "complex",
        "distinguish",
        "element",
        "format",
        "interwiktionary",
        "NGSL",
        "not to be confused with",
        "number box",
        "see",
        "simplify",
        "stub",
        "wik",
        "wikipedia",
        "Wikipedia",
        "wikispecies",
        "wikiquote",
        "Wikiquote",
        "improve",
        "TOCright",
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

ETYMOLOGY_TEMPLATES = set(
    [
        "ety-affix",
        "ety-prefix",
        "ety-suffix",
        "word parts",
        "confix",
        "compound",
        "multiword term",
    ]
)

