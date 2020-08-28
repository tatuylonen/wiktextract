# Definitions for various parser functions supported in WikiText
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org


from .wikihtml import ALLOWED_HTML_TAGS


def if_fn(title, fn_name, args, stack):
    """Implements #if parser function."""
    if len(args) > 3:
        print("{}: too many arguments for #if ({}) at {}"
              "".format(title, len(args), stack))
    else:
        while len(args) < 3:
            args.append("")
    if args[0].isspace():
        return args[2].strip()
    return args[1].strip()


def ifeq_fn(title, fn_name, args, stack):
    """Implements #ifeq parser function."""
    if len(args) > 4:
        print("{}: too many arguments for #ifeq ({}) at {}"
              "".format(title, len(args), stack))
    else:
        while len(args) < 4:
            args.append("")
    if args[0].strip() == args[1].strip():
        return args[2].strip()
    return args[3].strip()


def tag_fn(title, fn_name, args, stack):
    """Implements #tag parser function."""
    while len(args) < 2:
        args.append("")
    tag = args[0].lower()
    if tag not in ALLOWED_HTML_TAGS:
        print("{}: #tag creating non-allowed tag <{}> - omitted at {}"
              "".format(title, tag, stack))
        return "{{" + fn_name + ":" + "|".join(args) + "}}"
    content = args[1]
    attrs = []
    for x in args[2:]:
        m = re.match(r"""(?s)^([^=<>'"]+)=(.*)$""", x)
        if not m:
            print("{}: invalid attribute format {!r} missing name at {}"
                  "".format(title, x, stack))
            continue
        name, value = m.groups()
        attrs.append("{}={}".format(name, html.escape(value)))
    if attrs:
        attrs = " " + " ".join(attrs)
    else:
        attrs = ""
    if not content:
        return "<{}{} />".format(tag, attrs)
    content = html.escape(content, quote=False)
    return "<{}{}>{}</{}>".format(tag, attrs, content, tag)


def unimplemented_fn(title, fn_name, args, stack):
    print("{}: unimplemented parserfn {} at {}".format(title, fn_name, stack))
    return "{{" + fn_name + ":" + "|".join(args) + "}}"


# This list should include names of predefined parser functions and
# predefined variables (some of which can take arguments using the same
# syntax as parser functions and we treat them as parser functions).
# See https://en.wikipedia.org/wiki/Help:Magic_words#Parser_functions
PARSER_FUNCTIONS = {
    "FULLPAGENAME": unimplemented_fn,
    "PAGENAME": unimplemented_fn,
    "BASEPAGENAME": unimplemented_fn,
    "ROOTPAGENAME": unimplemented_fn,
    "SUBPAGENAME": unimplemented_fn,
    "ARTICLEPAGENAME": unimplemented_fn,
    "SUBJECTPAGENAME": unimplemented_fn,
    "TALKPAGENAME": unimplemented_fn,
    "NAMESPACENUMBER": unimplemented_fn,
    "NAMESPACE": unimplemented_fn,
    "ARTICLESPACE": unimplemented_fn,
    "SUBJECTSPACE": unimplemented_fn,
    "TALKSPACE": unimplemented_fn,
    "FULLPAGENAMEE": unimplemented_fn,
    "PAGENAMEE": unimplemented_fn,
    "BASEPAGENAMEE": unimplemented_fn,
    "ROOTPAGENAMEE": unimplemented_fn,
    "SUBPAGENAMEE": unimplemented_fn,
    "ARTICLEPAGENAMEE": unimplemented_fn,
    "SUBJECTPAGENAMEE": unimplemented_fn,
    "TALKPAGENAMEE": unimplemented_fn,
    "NAMESPACENUMBERE": unimplemented_fn,
    "NAMESPACEE": unimplemented_fn,
    "ARTICLESPACEE": unimplemented_fn,
    "SUBJECTSPACEE": unimplemented_fn,
    "TALKSPACEE": unimplemented_fn,
    "SHORTDESC": unimplemented_fn,
    "SITENAME": unimplemented_fn,
    "SERVER": unimplemented_fn,
    "SERVERNAME": unimplemented_fn,
    "SCRIPTPATH": unimplemented_fn,
    "CURRENTVERSION": unimplemented_fn,
    "CURRENTYEAR": unimplemented_fn,
    "CURRENTMONTH": unimplemented_fn,
    "CURRENTMONTHNAME": unimplemented_fn,
    "CURRENTMONTHABBREV": unimplemented_fn,
    "CURRENTDAY": unimplemented_fn,
    "CURRENTDAY2": unimplemented_fn,
    "CUEEWNTDOW": unimplemented_fn,
    "CURRENTDAYNAME": unimplemented_fn,
    "CURRENTTIME": unimplemented_fn,
    "CURRENTHOUR": unimplemented_fn,
    "CURRENTWEEK": unimplemented_fn,
    "CURRENTTIMESTAMP": unimplemented_fn,
    "LOCALYEAR": unimplemented_fn,
    "LOCALMONTH": unimplemented_fn,
    "LOCALMONTHNAME": unimplemented_fn,
    "LOCALMONTHABBREV": unimplemented_fn,
    "LOCALDAY": unimplemented_fn,
    "LOCALDAY2": unimplemented_fn,
    "LOCALDOW": unimplemented_fn,
    "LOCALDAYNAME": unimplemented_fn,
    "LOCALTIME": unimplemented_fn,
    "LOCALHOUR": unimplemented_fn,
    "LOCALWEEK": unimplemented_fn,
    "LOCALTIMESTAMP": unimplemented_fn,
    "REVISIONDAY": unimplemented_fn,
    "REVISIONDAY2": unimplemented_fn,
    "REVISIONMONTH": unimplemented_fn,
    "REVISIONYEAR": unimplemented_fn,
    "REVISIONTIMESTAMP": unimplemented_fn,
    "REVISIONUSER": unimplemented_fn,
    "NUMBEROFPAGES": unimplemented_fn,
    "NUMBEROFARTICLES": unimplemented_fn,
    "NUMBEROFFILES": unimplemented_fn,
    "NUMBEROFEDITS": unimplemented_fn,
    "NUMBEROFUSERS": unimplemented_fn,
    "NUMBEROFADMINS": unimplemented_fn,
    "NUMBEROFACTIVEUSERS": unimplemented_fn,
    "PAGEID": unimplemented_fn,
    "PAGESIZE": unimplemented_fn,
    "PROTECTIONLEVEL": unimplemented_fn,
    "PROTECTIONEXPIRY": unimplemented_fn,
    "PENDINGCHANGELEVEL": unimplemented_fn,
    "PAGESINCATEGORY": unimplemented_fn,
    "NUMBERINGROUP": unimplemented_fn,
    "lc": unimplemented_fn,
    "lcfirst": unimplemented_fn,
    "uc": unimplemented_fn,
    "ucfirst": unimplemented_fn,
    "formatnum": unimplemented_fn,
    "#dateformat": unimplemented_fn,
    "formatdate": unimplemented_fn,
    "padleft": unimplemented_fn,
    "padright": unimplemented_fn,
    "plural": unimplemented_fn,
    "#time": unimplemented_fn,
    "#timel": unimplemented_fn,
    "gender": unimplemented_fn,
    "#tag": tag_fn,
    "localurl": unimplemented_fn,
    "fullurl": unimplemented_fn,
    "canonicalurl": unimplemented_fn,
    "filepath": unimplemented_fn,
    "urlencode": unimplemented_fn,
    "anchorencode": unimplemented_fn,
    "ns": unimplemented_fn,
    "nse": unimplemented_fn,
    "#rel2abs": unimplemented_fn,
    "#titleparts": unimplemented_fn,
    "#expr": unimplemented_fn,
    "#if": if_fn,
    "#ifeq": ifeq_fn,
    "#iferror": unimplemented_fn,
    "#ifexpr": unimplemented_fn,
    "#ifexist": unimplemented_fn,
    "#switch": unimplemented_fn,
    "#babel": unimplemented_fn,
    "#categorytree": unimplemented_fn,
    "#coordinates": unimplemented_fn,
    "#invoke": unimplemented_fn,
    "#language": unimplemented_fn,
    "#lst": unimplemented_fn,
    "#lsth": unimplemented_fn,
    "#lstx": unimplemented_fn,
    "#property": unimplemented_fn,
    "#related": unimplemented_fn,
    "#section": unimplemented_fn,
    "#section-h": unimplemented_fn,
    "#section-x": unimplemented_fn,
    "#statements": unimplemented_fn,
    "#target": unimplemented_fn,
}
