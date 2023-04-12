# Replacement functions that override specific templates,
# which should never be run as is because they cause problems.

import re
# This dictionary should be assigned with the WTP.set_template_override()
# setter method.
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
    def middle(func):
        template_override_fns[template_name] = func
        return func
    return middle


@reg("egy-glyph")
def egy_glyph(args):
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
    if "=" not in args[1]:
        return "«" + args[1] + "»"
    return "EGY-GLYPH-IMAGE-ERROR"
