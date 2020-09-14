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


def if_fn(title, fn_name, args, expander, stack):
    """Implements #if parser function."""
    if len(args) > 3:
        print("{}: too many arguments for {} ({}) at {}"
              "".format(title, fn_name, len(args), stack))
    else:
        while len(args) < 3:
            args.append("")
    v = expander(args[0]).strip()
    print("if_fn cond:", repr(v))
    if v:
        return expander(args[1]).strip()
    return expander(args[2]).strip()


def ifeq_fn(title, fn_name, args, expander, stack):
    """Implements #ifeq parser function."""
    if len(args) > 4:
        print("{}: too many arguments for {} ({}) at {}"
              "".format(title, fn_name, len(args), stack))
    else:
        while len(args) < 4:
            args.append("")
    arg0 = expander(args[0])
    arg1 = expander(args[1])
    if arg0.strip() == arg1.strip():
        return expander(args[2]).strip()
    return expander(args[3]).strip()


def ifexist_fn(title, fn_name, args, expander, stack):
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
        return expander(args[1]).strip()
    return expander(args[2]).strip()


def switch_fn(title, fn_name, args, expander, stack):
    """Implements #switch parser function."""
    if len(args) < 3:
        print("{}: too few arguments for #switch ({}) at {}"
              "".format(title, len(args), stack))
        while len(args) < 3:
            args.append("")
    val = expander(args[0]).strip()
    match_next = False
    defval = None
    last = None
    for i in range(1, len(args)):
        arg = expander(args[i]).strip()
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
        last = None
    if defval is not None:
        return defval
    return last or ""


def tag_fn(title, fn_name, args, expander, stack):
    """Implements #tag parser function."""
    while len(args) < 2:
        args.append("")
    tag = expander(args[0]).lower()
    if tag not in ALLOWED_HTML_TAGS:
        print("{}: #tag creating non-allowed tag <{}> - omitted at {}"
              "".format(title, tag, stack))
        return "{{" + fn_name + ":" + "|".join(args) + "}}"
    content = expander(args[1])
    attrs = []
    for x in args[2:]:
        x = expander(x)
        m = re.match(r"""(?s)^([^=<>'"]+)=(.*)$""", x)
        if not m:
            print("{}: invalid attribute format {!r} missing name at {}"
                  "".format(title, x, stack))
            continue
        name, value = m.groups()
        attrs.append('{}="{}"'.format(name, html.escape(value)))
    if attrs:
        attrs = " " + " ".join(attrs)
    else:
        attrs = ""
    if not content:
        return "<{}{} />".format(tag, attrs)
    content = html.escape(content, quote=False)
    return "<{}{}>{}</{}>".format(tag, attrs, content, tag)


def fullpagename_fn(title, fn_name, args, expander, stack):
    """Implements the FULLPAGENAME magic word/parser function."""
    t = expander(args[0]) if args else title
    print("fullpagename t={} args={} title={}"
          "".format(t, args, title))
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs == 0:
        t = t[1:].capitalize()
    elif ofs > 0:
        ns = t[:ofs].capitalize()
        t = t[ofs + 1:].capitalize()
        t = ns + ":" + t
    else:
        t = t.capitalize()
    return t


def pagename_fn(title, fn_name, args, expander, stack):
    """Implements the PAGENAME magic word/parser function."""
    t = expander(args[0]) if args else title
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs >= 0:
        t = t[ofs + 1:].capitalize()
    else:
        t = t.capitalize()
    return t


def namespace_fn(title, fn_name, args, expander, stack):
    """Implements the NAMESPACE magic word/parser function."""
    # XXX check what this should return when no namespace given
    t = expander(args[0]) if args else title
    t = re.sub(r"\s+", " ", t)
    t = t.strip()
    ofs = t.find(":")
    if ofs >= 0:
        ns = t[:ofs].capitalize()
        if ns == "Project":
            return PROJECT_NAME
        return ns
    return ""


def lc_fn(title, fn_name, args, expander, stack):
    """Implements the lc parser function (lowercase)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return expander(args[0]).strip().lower()


def lcfirst_fn(title, fn_name, args, expander, stack):
    """Implements the lcfirst parser function (lowercase first character)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    t = expander(args[0]).strip()
    return t[0].lower() + t[1:]


def uc_fn(title, fn_name, args, expander, stack):
    """Implements the uc parser function (uppercase)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return expander(args[0]).strip().upper()


def ucfirst_fn(title, fn_name, args, expander, stack):
    """Implements the ucfirst parser function (capitalize first character)."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    return expander(args[0]).strip().capitalize()


def dateformat_fn(title, fn_name, args, expander, stack):
    """Implements the #dateformat (= #formatdate) parser function."""
    if len(args) < 1 or len(args) > 2:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    arg0 = expander(args[0])
    if not re.search(r"\d\d\d", arg0):
        arg0 += " 3333"
    dt = dateparser.parse(arg0)
    if not dt:
        print("{}: invalid date format in {}: {!r}"
              "".format(title, fn_name, arg0))
        dt = datetime.datetime.utcnow()
    fmt = expander(args[1]) if len(args) > 1 else "ISO 8601"
    # This is supposed to format according to user preferences by default.
    if fmt in ("ISO 8601", "ISO8601") and dt.year == 0:
        fmt = "mdy"
    date_only = dt.hour == 0 and dt.minute == 0 and dt.second == 0
    if fmt == "mdy":
        if date_only:
            if dt.year == 3333:
                return dt.strftime("%b %d")
            return dt.strftime("%b %d, %Y")
        return dt.strftime("%b %d, %Y %H:%M:%S")
    elif fmt == "dmy":
        if date_only:
            if dt.year == 3333:
                return dt.strftime("%d %b")
            return dt.strftime("%d %b %Y")
        return dt.strftime("%d %b %Y %H:%M:%S")
    elif fmt == "ymd":
        if date_only:
            if dt.year == 3333:
                return dt.strftime("%b %d")
            return dt.strftime("%Y %b %d")
        return dt.strftime("%Y %b %d %H:%M:%S")
    # Otherwise format into ISO format
    if date_only:
        return dt.date().isoformat()
    return dt.isoformat()


def urlencode_fn(title, fn_name, args, expander, stack):
    """Implements the urlencode parser function."""
    if len(args) < 1 or len(args) > 2:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    arg0 = expander(args[0])
    fmt = expander(args[1]) if len(args) > 1 else "QUERY"
    url = arg0.strip()
    if fmt == "PATH":
        return urllib.parse.quote(url, safe="")
    elif fmt == "QUERY":
        return urllib.parse.quote_plus(url)
    # All else in WIKI encoding
    url = re.sub(r"\s+", "_", url)
    return urllib.parse.quote(url, safe="/:")


def anchorencode_fn(title, fn_name, args, expander, stack):
    """Implements the urlencode parser function."""
    if len(args) != 1:
        print("{}: wrong number of arguments for {} ({})"
              "".format(title, fn_name, len(args)))
        args.append("")
    anchor = expander(args[0]).strip()
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


class Namespace(object):
    __slots__ = (
        "aliases",
        "canonicalName",
        "defaultContentModel",
        "hasGenderDistinction",
        "id",
        "isCapitalized",
        "isContent",
        "isIncludable",
        "isMovable",
        "isSubject",
        "isTalk",
        "name",
        "subject",
        "talk",
    )

    def __init__(self, aliases=[], canonicalName="",
                 defaultContentModel="wikitext", hasGenderDistinction=True,
                 id=None, isCapitalized=False, isContent=False,
                 isIncludable=False,
                 isMovable=False, isSubject=False, isTalk=False,
                 name="", subject=None, talk=None):
        assert name
        assert id is not None
        self.aliases = aliases
        self.canonicalName = canonicalName
        self.defaultContentModel = defaultContentModel
        self.hasGenderDistinction = hasGenderDistinction
        self.id = id
        self.isCapitalized = isCapitalized
        self.isContent = isContent
        self.isIncludable = isIncludable
        self.isMovable = isMovable
        self.isSubject = isSubject
        self.isTalk = isTalk
        self.name = name
        self.subject = subject
        self.talk = talk

# These duplicate definitions in lua/mw_site.lua
media_ns = Namespace(id=-2, name="Media", isSubject=True)
special_ns = Namespace(id=-1, name="Special", isSubject=True)
main_ns = Namespace(id=0, name="Main", isContent=True, isSubject=True)
talk_ns = Namespace(id=1, name="Talk", isTalk=True, subject=main_ns)
user_ns = Namespace(id=2, name="User", isSubject=True)
user_talk_ns = Namespace(id=3, name="User_talk", isTalk=True,
                         subject=user_ns)
project_ns = Namespace(id=4, name="Project", isSubject=True)
project_talk_ns = Namespace(id=5, name="Project_talk", isTalk=True,
                            subject=project_ns)
image_ns = Namespace(id=6, name="File", aliases=["Image"],
                     isSubject=True)
image_talk_ns = Namespace(id=7, name="File_talk",
                          aliases=["Image_talk"],
                          isTalk=True, subject=image_ns)
mediawiki_ns = Namespace(id=8, name="MediaWiki", isSubject=True)
mediawiki_talk_ns = Namespace(id=9, name="MediaWiki_talk",
                              isTalk=True, subject=mediawiki_ns)
template_ns = Namespace(id=10, name="Template", isSubject=True)
template_talk_ns = Namespace(id=11, name="Template_talk", isTalk=True,
                             subject=template_ns)
help_ns = Namespace(id=12, name="Help", isSubject=True)
help_talk_ns = Namespace(id=13, name="Help_talk", isTalk=True,
                         subject=help_ns)
category_ns = Namespace(id=14, name="Category", isSubject=True)
category_talk_ns = Namespace(id=15, name="Category_talk", isTalk=True,
                             subject=category_ns)
module_ns = Namespace(id=828, name="Module", isIncludable=True,
                      isSubject=True)
module_talk_ns = Namespace(id=829, name="Module_talk", isTalk=True,
                           subject=module_ns)
main_ns.talk = talk_ns
user_ns.talk = user_talk_ns
project_ns.talk = project_talk_ns
mediawiki_ns.talk = mediawiki_talk_ns
template_ns.talk = template_talk_ns
help_ns.talk = help_talk_ns
category_ns.talk = category_talk_ns
module_ns.talk = module_talk_ns

namespaces = {}

def add_ns(t, ns):
   t[ns.id] = ns

add_ns(namespaces, media_ns)
add_ns(namespaces, special_ns)
add_ns(namespaces, main_ns)
add_ns(namespaces, talk_ns)
add_ns(namespaces, user_ns)
add_ns(namespaces, user_talk_ns)
add_ns(namespaces, project_ns)
add_ns(namespaces, project_talk_ns)
add_ns(namespaces, image_ns)
add_ns(namespaces, image_talk_ns)
add_ns(namespaces, mediawiki_ns)
add_ns(namespaces, mediawiki_talk_ns)
add_ns(namespaces, template_ns)
add_ns(namespaces, template_talk_ns)
add_ns(namespaces, help_ns)
add_ns(namespaces, help_talk_ns)
add_ns(namespaces, category_ns)
add_ns(namespaces, category_talk_ns)
add_ns(namespaces, module_ns)
add_ns(namespaces, module_talk_ns)


def ns_fn(title, fn_name, args, expander, stack):
    """Implements the ns parser function."""
    t = expander(args[0]).strip().upper()
    print("ns_fn", t)
    if t and t.isdigit():
        t = int(t)
        ns = namespaces.get(t)
    else:
        for ns in namespaces.values():
            print("checking", ns.name)
            if ns.name and t == ns.name.upper():
                break
            if ns.canonicalName and t == ns.canonicalName.upper():
                break
            for a in ns.aliases:
                if t == a.upper():
                    break
            else:
                continue
            break
        else:
            ns = None
    print("ns=", ns)
    if ns is None:
        return ""
    return ns.name


def padleft_fn(title, fn_name, args, expander, stack):
    """Implements the padleft parser function."""
    if len(args) < 2:
        print("{}: too few arguments for {}"
              "".format(title, fn_name))
    v = expander(args[0]) if len(args) >= 1 else ""
    cnt = expander(args[1]).strip() if len(args) >= 2 else "0"
    pad = expander(args[2]) if len(args) >= 3 and args[2] else "0"
    if not cnt.isdigit():
        print("{}: pad length is not integer: {!r}".format(title, cnt))
        cnt = 0
    else:
        cnt = int(cnt)
    if cnt - len(v) > len(pad):
        pad = (pad * ((cnt - len(v)) // len(pad)))
    if len(v) < cnt:
        v = pad[:cnt - len(v)] + v
    return v


def padright_fn(title, fn_name, args, expander, stack):
    """Implements the padright parser function."""
    if len(args) < 2:
        print("{}: too few arguments for {}"
              "".format(title, fn_name))
    v = expander(args[0]) if len(args) >= 1 else ""
    cnt = expander(args[1]).strip() if len(args) >= 2 else "0"
    arg2 = expander(args[2]) if len(args) >= 3 and args[2] else "0"
    pad = arg2 if len(args) >= 3 and arg2 else "0"
    if not cnt.isdigit():
        print("{}: pad length is not integer: {!r}".format(title, cnt))
        cnt = 0
    else:
        cnt = int(cnt)
    if cnt - len(v) > len(pad):
        pad = (pad * ((cnt - len(v)) // len(pad)))
    if len(v) < cnt:
        v = v + pad[:cnt - len(v)]
    return v


def len_fn(title, fn_name, args, expander, stack):
    """Implements the #len parser function."""
    v = expander(args[0]).strip()
    return str(len(v))


def pos_fn(title, fn_name, args, expander, stack):
    """Implements the #pos parser function."""
    if len(args) < 2:
        return ""
    while len(args) < 3:
        args.append("")
    arg0 = expander(args[0])
    arg1 = expander(args[1])
    offset = expander(args[2]).strip()
    if not offset or not offset.isdigit():
        offset = "0"
    offset = int(offset)
    idx = arg0.find(arg1, offset)
    if idx >= 0:
        return str(idx)
    return ""


def rpos_fn(title, fn_name, args, expander, stack):
    """Implements the #rpos parser function."""
    if len(args) < 2:
        return ""
    while len(args) < 3:
        args.append("")
    arg0 = expander(args[0])
    arg1 = expander(args[1])
    offset = expander(args[2]).strip()
    if not offset or not offset.isdigit():
        offset = "0"
    offset = int(offset)
    idx = arg0.rfind(arg1, offset)
    if idx >= 0:
        return str(idx)
    return ""


def sub_fn(title, fn_name, args, expander, stack):
    """Implements the #sub parser function."""
    if len(args) < 2:
        print("{}: too few arguments".format(title))
    while len(args) < 3:
        args.append("")
    arg0 = expander(args[0])
    start = expander(args[1]).strip()
    length = expander(args[2]).strip()
    try:
        start = int(start)
    except ValueError:
        start = 0
    if start < 0:
        start = max(0, len(arg0) + start)
    start = min(start, len(arg0))
    try:
        length = int(length)
    except ValueError:
        length = 0
    if length == 0:
        length = max(0, len(arg0) - start)
    elif length < 0:
        length = max(0, len(arg0) - start + length)
    return arg0[start : start + length]


def pad_fn(title, fn_name, args, expander, stack):
    """Implements the pad parser function."""
    if len(args) < 2:
        print("{}: too few arguments for {}"
              "".format(title, fn_name))
    v = expander(args[0]) if len(args) >= 1 else ""
    cnt = expander(args[1]).strip() if len(args) >= 2 else "0"
    pad = expander(args[2]) if len(args) >= 3 and args[2] else "0"
    direction = expander(args[3]) if len(args) >= 4 else ""
    if not cnt.isdigit():
        print("{}: pad length is not integer: {!r}".format(title, cnt))
        cnt = 0
    else:
        cnt = int(cnt)
    if cnt - len(v) > len(pad):
        pad = (pad * ((cnt - len(v)) // len(pad) + 1))
    if len(v) < cnt:
        padlen = cnt - len(v)
        if direction == "right":
            v = v + pad[:padlen]
        elif direction == "center":
            v = pad[:padlen // 2] + v + pad[:padlen - padlen // 2]
        else:  # left
            v = pad[:padlen] + v
    return v


def replace_fn(title, fn_name, args, expander, stack):
    """Implements the #replace parser function."""
    if len(args) < 3:
        print("{}: too few arguments".format(title))
    while len(args) < 3:
        args.append("")
    arg0 = expander(args[0])
    arg1 = expander(args[1]) or " "
    arg2 = expander(args[2])
    return arg0.replace(arg1, arg2)


def explode_fn(title, fn_name, args, expander, stack):
    """Implements the #explode parser function."""
    if len(args) < 3:
        print("{}: too few arguments".format(title))
    while len(args) < 4:
        args.append("")
    arg0 = expander(args[0])
    delim = expander(args[1]) or " "
    position = expander(args[2]).strip()
    limit = expander(args[3]).strip()
    try:
        position = int(position)
    except ValueError:
        position = 0
    try:
        limit = int(limit)
    except ValueError:
        limit = 0
    parts = arg0.split(delim)
    if limit > 0 and len(parts) > limit:
        parts = parts[:limit - 1] + [delim.join(parts[limit - 1:])]
    print("parts", parts)
    if position < 0:
        position = len(parts) + position
    if position < 0 or position >= len(parts):
        return ""
    return parts[position]


def urldecode_fn(title, fn_name, args, expander, stack):
    """Implements the #urldecode parser function."""
    arg0 = expander(args[0]).strip()
    ret = urllib.parse.unquote_plus(args[0])
    return ret


def unimplemented_fn(title, fn_name, args, expander, stack):
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
    "nse": ns_fn,  # We don't have spaces in ns names
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
    # From Help:Extension:ParserFunctions
    "#len": len_fn,
    "#pos": pos_fn,
    "#rpos": rpos_fn,
    "#sub": sub_fn,
    "#pad": pad_fn,
    "#replace": replace_fn,
    "#explode": explode_fn,
    "#urldecode": urldecode_fn,
    "#urlencode": urlencode_fn,
}


def call_parser_function(fn_name, args, expander, pagetitle, stack):
    """Calls the given parser function with the given arguments."""
    assert isinstance(fn_name, str)
    assert isinstance(args, (list, tuple))
    assert callable(expander)
    assert isinstance(pagetitle, str)
    assert isinstance(stack, list)
    fn = PARSER_FUNCTIONS[fn_name]
    return fn(pagetitle, fn_name, args, expander, stack)
