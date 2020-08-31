# Definitions for various parser functions supported in WikiText
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import html
import datetime
import urllib.parse
import dateparser
from .wikihtml import ALLOWED_HTML_TAGS


# Name of the WikiMedia for which we are generating content
PROJECT_NAME = "Wiktionary"


def if_fn(title, fn_name, args, stack):
    """Implements #if parser function."""
    if len(args) > 3:
        print("{}: too many arguments for {} ({}) at {}"
              "".format(title, fn_name, len(args), stack))
    else:
        while len(args) < 3:
            args.append("")
    v = args[0].strip()
    if v:
        return args[1].strip()
    return args[2].strip()


def ifeq_fn(title, fn_name, args, stack):
    """Implements #ifeq parser function."""
    if len(args) > 4:
        print("{}: too many arguments for {} ({}) at {}"
              "".format(title, fn_name, len(args), stack))
    else:
        while len(args) < 4:
            args.append("")
    if args[0].strip() == args[1].strip():
        return args[2].strip()
    return args[3].strip()


def ifexist_fn(title, fn_name, args, stack):
    """Implements #ifexist parser function."""
    if len(args) > 3:
        print("{}: too many arguments for {} ({}) at {}"
              "".format(title, fn_name, len(args), stack))
    else:
        while len(args) < 3:
            args.append("")
    # XXX how will we check if the page exists?  Should probably pass a context
    # to all parser function implementations and use the context to evaluate
    # this.
    exists = False  # XXX needs to be implemented
    if exists:
        return args[1].strip()
    return args[2].strip()


def switch_fn(title, fn_name, args, stack):
    """Implements #switch parser function."""
    if len(args) < 3:
        print("{}: too few arguments for #switch ({}) at {}"
              "".format(title, len(args), stack))
        while len(args) < 3:
            args.append("")
    val = args[0].strip()
    match_next = False
    defval = None
    last = None
    for i in range(1, len(args)):
        arg = args[i].strip()
        m = re.match(r"(?s)^([^=]+)=(.*)$", arg)
        if not m:
            last = arg
            if arg == val:
                match_next = True
            continue
        k, v = m.groups()
        k = k.strip()
        v = v.strip()
        if k == val or match_next:
            return v
        if k == "#default":
            defval = v
        last = v
    if defval is not None:
        return defval
    return last or ""


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


def fullpagename_fn(title, fn_name, args, stack):
    """Implements the FULLPAGENAME magic word/parser function."""
    t = args[0] if args else title
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs == 0:
        t = t[1:].capitalize()
    elif ofs > 0:
        ns = t[:ofs].capitalize()
        t = t[ofs + 1:].capitalize()
        if ns == "Project":
            ns = PROJECT_NAME
        t = ns + ":" + t
    else:
        t = t.capitalize()
    return t


def pagename_fn(title, fn_name, args, stack):
    """Implements the PAGENAME magic word/parser function."""
    t = args[0] if args else title
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs == 0:
        t = t[1:].capitalize()
    elif ofs > 0:
        t = t[ofs + 1:].capitalize()
    else:
        t = t.capitalize()
    return t


def namespace_fn(title, fn_name, args, stack):
    """Implements the NAMESPACE magic word/parser function."""
    t = args[0] if args else title
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs == 0:
        ns = PROJECT_NAME
    elif ofs > 0:
        ns = t[:ofs].capitalize()
        if ns == "Project":
            ns = PROJECT_NAME
    else:
        ns = PROJECT_NAME
    return ns


def lc_fn(title, fn_name, args, stack):
    """Implements the lc parser function (lowercase)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return args[0].strip().upper()


def lcfirst_fn(title, fn_name, args, stack):
    """Implements the lcfirst parser function (lowercase first character)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    t = args[0].strip()
    return t[0].lower() + t[1:]


def uc_fn(title, fn_name, args, stack):
    """Implements the uc parser function (uppercase)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return args[0].strip().upper()


def ucfirst_fn(title, fn_name, args, stack):
    """Implements the ucfirst parser function (capitalize first character)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return args[0].strip().capitalize()


def dateformat_fn(title, fn_name, args, stack):
    """Implements the #dateformat (= #formatdate) parser function."""
    if len(args) < 1 or len(args) > 2:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    dt = dateparser.parse(args[0])
    if not dt:
        print("{}: invalid date format in {}: {!r}"
              "".format(title, fn_name, args[0]))
        dt = datetime.datetime.utcnow()
    fmt = args[1] if len(args) > 1 else "ISO 8601"
    # This is supposed to format according to user preferences by default.
    if fmt in ("ISO 8601", "ISO8601") and dt.year == 0:
        fmt = "mdy"
    date_only = dt.hour == 0 and dt.minute == 0 and dt.second == 0
    if fmt == "mdy":
        if date_only:
            if dt.year == 0:
                return dt.strftime("%B %d")
            return dt.strftime("%B %d, %Y")
        return dt.strftime("%B %d, %Y %H:%M:%S")
    elif fmt == "dmy":
        if date_only:
            if dt.year == 0:
                return dt.strftime("%d %B")
            return dt.strftime("%d %B %Y")
        return dt.strftime("%d %B %Y %H:%M:%S")
    elif fmt == "ymd":
        if date_only:
            if dt.year == 0:
                return dt.strftime("%B %d")
            return dt.date().isoformat()
        return dt.isoformat(sep=" ")
    # Otherwise format into ISO format
    if date_only:
        return dt.date().isoformat()
    return dt.isoformat()


def urlencode_fn(title, fn_name, args, stack):
    """Implements the urlencode parser function."""
    if len(args) < 1 or len(args) > 2:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    fmt = args[1] if len(args) > 1 else "QUERY"
    url = args[0].strip()
    if fmt == "PATH":
        return urllib.parse.quote(url)
    elif fmt == "QUERY":
        return urllib.parse.quote_plus(url)
    # All else in WIKI encoding
    url = re.sub(r"\s+", "_", url)
    return urllib.parse.quote(url)


def anchorencode_fn(title, fn_name, args, stack):
    """Implements the urlencode parser function."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    anchor = args[0].strip()
    anchor = re.sub(r"\s+", "_", anchor)
    # I am not sure how MediaWiki encodes these but HTML5 at least allows
    # any character except any type of space character.  However, we also
    # replace quotes and "<>", just in case these are used inside attributes.
    # XXX should really check from MediaWiki source code
    def repl_anchor(m):
        v = urllib.parse.quote(m.group(0))
        return re.sub(r"%", ".", v)

    anchor = re.sub(r"""['"<>]""", repl_anchor, anchor)
    return anchor


def ns_fn(title, fn_name, args, stack):
    """Implements the ns parser function."""
    print("{}: ns {}".format(title, args))
    return "XXX"


def padleft_fn(title, fn_name, args, stack):
    """Implements the ns parser function."""
    if len(args) < 2:
        print("{}: too few arguments for {}"
              "".format(title, fn_name))
    v = args[0] if len(args) >= 1 else ""
    cnt = args[1].strip() if len(args) >= 2 else "0"
    pad = args[2] if len(args) >= 3 and args[2] else "0"
    if not cnt.isdigit():
        print("{}: pad length is not integer: {!r}".format(title, cnt))
        cnt = 0
    else:
        cnt = int(cnt)
    if cnt - len(v) > len(pad):
        v = (pad * ((cnt - len(v)) // len(pad)))
    if len(v) < cnt:
        v = pad[:cnt - len(v)] + v
    return v


def padright_fn(title, fn_name, args, stack):
    """Implements the ns parser function."""
    if len(args) < 2:
        print("{}: too few arguments for {}"
              "".format(title, fn_name))
    v = args[0] if len(args) >= 1 else ""
    cnt = args[1].strip() if len(args) >= 2 else "0"
    pad = args[2] if len(args) >= 3 and args[2] else "0"
    if not cnt.isdigit():
        print("{}: pad length is not integer: {!r}".format(title, cnt))
        cnt = 0
    else:
        cnt = int(cnt)
    if cnt - len(v) > len(pad):
        v = (pad * ((cnt - len(v)) // len(pad)))
    if len(v) < cnt:
        v = pad[:cnt - len(v)] + v
    return v


def unimplemented_fn(title, fn_name, args, stack):
    print("{}: unimplemented parserfn {} at {}".format(title, fn_name, stack))
    return "{{" + fn_name + ":" + "|".join(args) + "}}"


# This list should include names of predefined parser functions and
# predefined variables (some of which can take arguments using the same
# syntax as parser functions and we treat them as parser functions).
# See https://en.wikipedia.org/wiki/Help:Magic_words#Parser_functions
PARSER_FUNCTIONS = {
    "FULLPAGENAME": fullpagename_fn,
    "PAGENAME": pagename_fn,
    "BASEPAGENAME": unimplemented_fn,
    "ROOTPAGENAME": unimplemented_fn,
    "SUBPAGENAME": unimplemented_fn,
    "ARTICLEPAGENAME": unimplemented_fn,
    "SUBJECTPAGENAME": unimplemented_fn,
    "TALKPAGENAME": unimplemented_fn,
    "NAMESPACENUMBER": unimplemented_fn,
    "NAMESPACE": namespace_fn,
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
    "lc": lc_fn,
    "lcfirst": lcfirst_fn,
    "uc": uc_fn,
    "ucfirst": ucfirst_fn,
    "formatnum": unimplemented_fn,
    "#dateformat": dateformat_fn,
    "#formatdate": dateformat_fn,
    "padleft": padleft_fn,
    "padright": padright_fn,
    "plural": unimplemented_fn,
    "#time": unimplemented_fn,
    "#timel": unimplemented_fn,
    "gender": unimplemented_fn,
    "#tag": tag_fn,
    "localurl": unimplemented_fn,
    "fullurl": unimplemented_fn,
    "canonicalurl": unimplemented_fn,
    "filepath": unimplemented_fn,
    "urlencode": urlencode_fn,
    "anchorencode": anchorencode_fn,
    "ns": ns_fn,
    "nse": unimplemented_fn,
    "#rel2abs": unimplemented_fn,
    "#titleparts": unimplemented_fn,
    "#expr": unimplemented_fn,
    "#if": if_fn,
    "#ifeq": ifeq_fn,
    "#iferror": unimplemented_fn,
    "#ifexpr": unimplemented_fn,
    "#ifexist": ifexist_fn,
    "#switch": switch_fn,
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


def call_parser_function(fn_name, args, pagetitle, stack):
    """Calls the given parser function with the given arguments."""
    assert isinstance(fn_name, str)
    assert isinstance(args, (list, tuple))
    assert isinstance(pagetitle, str)
    assert isinstance(stack, list)
    fn = PARSER_FUNCTIONS[fn_name]
    return fn(pagetitle, fn_name, args, stack)
