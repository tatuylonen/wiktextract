# Replacement functions that override specific templates,
# which should never be run as is because they cause problems.

import re

# This dictionary should be assigned with the WTP.set_template_override()
# setter method; see wiktwords.
template_override_fns = {}

# https://stackoverflow.com/a/63071396
# To use parameters with reg() for the template-name stuff,
# we need to have three (four) levels of functions here.
# We do not technically have a wrapper function because
# we just return func as is. middle() is not a wrapper function,
# it's the actual decorator function itself (called with func)
# and reg() is actually a kind of wrapper around the decorator
# function that takes a parameter that middle() can't take.
# A bit messy conceptually.


def reg(template_name):
    """Decorator that takes its input key and the template it decorates,
    and adds them to the template_override_fns dictionary"""
    def middle(func):
        template_override_fns[template_name] = func
        return func
    return middle


@reg("egy-glyph")
def egy_glyph(args):
    """Intercept {{egy-glyph}}, which causes problems by creating
    tables and inserting agnostic images that can't be easily parsed
    as text data."""
    print(args)
    ret = "EGY-GLYPH-ERROR"
    if "=" not in args[1]:
        ret = args[1]
    for arg in args[1:]:
        if "quad=" in arg:
            ret = arg[5:]
            ret = re.sub("<br>", ":", ret)
    return "«" + ret + "»"

@reg("egy-glyph-img")
def egy_glyph_img(args):
    """Intercept {{egy-glyph-img}}, which is turned into an inline
    image that is generally useless to our parser and replaces it
    with its egyptological code."""
    if "=" not in args[1]:
        return "«" + args[1] + "»"
    return "EGY-GLYPH-IMAGE-ERROR"
