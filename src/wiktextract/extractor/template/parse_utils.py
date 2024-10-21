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
ETYMOLOGY_TEMPLATES: set[str] = set(
)

