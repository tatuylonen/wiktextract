# Code for expanding Wikitext templates, arguments, parser functions, and
# Lua macros.
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import os
import re
import sys
import copy
import html
import base64
import os.path
import traceback
import collections
import html.entities
import lupa
from lupa import LuaRuntime

from wiktextract import wikitext
from wiktextract.wikitext import WikiNode, NodeKind
from wiktextract.wikiparserfns import (PARSER_FUNCTIONS, call_parser_function,
                                       tag_fn)
from wiktextract import languages

# List of search paths for Lua libraries.
builtin_lua_search_paths = [
    # [path, ignore_modules]
    ["lua", ["string"]],
    ["lua/mediawiki-extensions-Scribunto/includes/engines/LuaCommon/lualib",
     []],
]

# Set of HTML tags that need an explicit end tag.
PAIRED_HTML_TAGS = set(k for k, v in wikitext.ALLOWED_HTML_TAGS.items()
                       if not v.get("no-end-tag"))

# Set of known language codes.
KNOWN_LANGUAGE_TAGS = set(x["code"] for x in languages.all_languages
                          if x.get("code") and x.get("name"))

# Mapping from language code code to language name.
LANGUAGE_CODE_TO_NAME = { x["code"]: x["name"]
                          for x in languages.all_languages
                          if x.get("code") and x.get("name") }


# Create unique value (128-random value) that is used as a magic cookie for
# special codes used to represent nested structures during encoding/expansion
magic = base64.b64encode(os.urandom(16), altchars=b"#!").decode("utf-8")
magic = re.sub(r"=", "-", magic)


class ExpandCtx(object):
    """Context used for processing wikitext and for expanding templates,
    parser functions and Lua macros.  This structure is used to cache
    Lua modules captured in Phase 1, among other things."""
    __slots__ = (
        "cookies",	 # Mapping from magic cookie -> expansion data
        "cookies_base",  # Cookies for processing template bodies
        "fullpage",	 # The unprocessed text of the current page (or None)
        "lua",		 # Lua runtime or None if not yet initialized
        "modules",	 # Lua code for defined Lua modules
        "need_pre_expand",  # Set of template names to be expanded before parse
        "redirects",	 # Redirects in the wikimedia project
        "rev_ht",	 # Mapping from text to magic cookie
        "rev_ht_base",   # Rev_ht from processing template bodies
        "template_fn",   # None or function to expand template
        "template_name", # name of template currently being expanded
        "templates",     # dict temlate name -> definition
        "title",         # current page title
    )
    def __init__(self):
        self.cookies_base = []
        self.cookies = []
        self.fullpage = None
        self.lua = None
        self.rev_ht_base = {}
        self.rev_ht = {}

    def save_value(self, kind, args):
        """Saves a value of a particular kind and returns a unique magic
        cookie for it."""
        assert kind in ("T", "A", "L")  # Template/parserfn, arg, link
        assert isinstance(args, (list, tuple))
        args = tuple(args)
        v = (kind, args)
        if v in self.rev_ht_base:
            return "!" + magic + kind + str(self.rev_ht[v]) + "!"
        if v in self.rev_ht:
            return "!" + magic + kind + str(self.rev_ht[v]) + "!"
        idx = len(self.cookies)
        self.cookies.append(v)
        self.rev_ht[v] = idx
        ret = "!" + magic + kind + str(idx) + "!"
        return ret

    def encode(self, text):
        """Encode all templates, template arguments, and parser function calls
        in the text, from innermost to outermost."""

        def repl_arg(m):
            """Replacement function for template arguments."""
            orig = m.group(1)
            args = orig.split("|")
            return self.save_value("A", args)

        def repl_templ(m):
            """Replacement function for templates {{...}} and parser
            functions."""
            args = m.group(1).split("|")
            return self.save_value("T", args)

        def repl_link(m):
            """Replacement function for links [[...]]."""
            orig = m.group(1)
            return self.save_value("L", (orig,))

        # Main loop of encoding.  We encode repeatedly, always the innermost
        # template, argument, or parser function call first.  We also encode
        # links as they affect the interpretation of templates.
        while True:
            prev = text
            # Encode links.
            text = re.sub(r"\[\[([^][{}]+)\]\]", repl_link, text)
            # Encode template arguments.  We repeat this until there are
            # no more matches, because otherwise we could encode the two
            # innermost braces as a template transclusion.
            while True:
                prev2 = text
                text = re.sub(r"(?s)\{\{\{(([^{}]|\}[^}]|\}\}[^}])*?)\}\}\}",
                              repl_arg, text)
                if text == prev2:
                    break
            # Encode templates
            text = re.sub(r"(?s)\{\{(([^{}]|\}[^}])+?)\}\}",
                          repl_templ, text)
            # We keep looping until there is no change during the iteration
            if text == prev:
                break
            prev = text
        return text


def canonicalize_template_name(name):
    """Canonicalizes a template name by making its first character uppercase
    and replacing underscores by spaces and sequences of whitespace by a single
    whitespace."""
    assert isinstance(name, str)
    name = re.sub(r"_", " ", name)
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\(", "%28", name)
    name = re.sub(r"\)", "%29", name)
    name = re.sub(r"&", "%26", name)
    name = re.sub(r"\+", "%2B", name)
    name = name.strip()
    if name[:9].lower() == "template:":
        name = name[9:]
    if name:
        name = name[0].upper() + name[1:]
    return name


def canonicalize_parserfn_name(name):
    """Canonicalizes a parser function name by making its first character
    uppercase and replacing underscores by spaces and sequences of
    whitespace by a single whitespace."""
    assert isinstance(name, str)
    name = re.sub(r"_", " ", name)
    name = re.sub(r"\s+", " ", name)
    name = name.strip()
    if name not in PARSER_FUNCTIONS:
        name = name.lower()  # Parser function names are case-insensitive
    return name


def template_to_body(title, text):
    """Extracts the portion to be transcluded from a template body.  This
    returns an str."""
    assert isinstance(title, str)
    assert isinstance(text, str)
    # Preprocess the template, handling, e.g., <nowiki> ... </nowiki> and
    # HTML comments
    text = wikitext.preprocess_text(text)
    # Remove all text inside <noinclude> ... </noinclude>
    text = re.sub(r"(?is)<\s*noinclude\s*>.*?<\s*/\s*noinclude\s*>",
                  "", text)
    text = re.sub(r"(?is)<\s*noinclude\s*/\s*>", "", text)
    # <onlyinclude> tags, if present, include the only text that will be
    # transcluded.  All other text is ignored.
    onlys = list(re.finditer(r"(?is)<\s*onlyinclude\s*>(.*?)"
                             r"<\s*/\s*onlyinclude\s*>|"
                             r"<\s*onlyinclude\s*/\s*>",
                             text))
    if onlys:
        text = "".join(m.group(1) or "" for m in onlys)
    # Remove <includeonly>.  They mark text that is not visible on the page
    # itself but is included in transclusion.  Also text outside these tags
    # is included in transclusion.
    text = re.sub(r"(?is)<\s*(/\s*)?includeonly\s*(/\s*)?>", "", text)
    # Sanity checks for certain unbalanced tags.  However, it appears some
    # templates intentionally produce these and intend them to be displayed.
    # Thus don't warn, and we may even need to arrange for them to be properly
    # parsed as text.
    if False:
       m = re.search(r"(?is)<\s*(/\s*)?noinclude\s*(/\s*)?>", text)
       if m:
           print("{}: unbalanced {}".format(title, m.group(0)))
       m = re.search(r"(?is)<\s*(/\s*)?onlyinclude\s*(/\s*)?>", text)
       if m:
           print("{}: unbalanced {}".format(title, m.group(0)))
    return text


def analyze_template(name, body):
    """Analyzes a template body and returns a set of the canonicalized
    names of all other templates it calls and a boolean that is True
    if it should be pre-expanded before final parsing and False if it
    need not be pre-expanded.  The pre-expanded flag is determined
    based on that body only; the caller should propagate it to
    templates that include the given template.  This does not work for
    template and template function calls where the name is generated by
    other expansions."""
    assert isinstance(body, str)
    included_templates = set()
    pre_expand = False

    # Determine if the template starts with a list item
    contains_list = re.match(r"(?s)^[#*;:]", body) is not None

    # Remove paired tables
    prev = body
    while True:
        unpaired_text = re.sub(
            r"(?s)(^|\n)\{\|([^\n]|\n+[^{|]|\n+\|[^}]|\n+\{[^|])*?\n+\|\}",
            r"", prev)
        if unpaired_text == prev:
            break
        prev = unpaired_text
    #print("unpaired_text {!r}".format(unpaired_text))

    # Determine if the template contains an unpaired table
    contains_unpaired_table = re.search(r"(?s)(^|\n)(\{\||\|\})",
                                        unpaired_text) is not None

    # Determine if the template contains table element tokens outside
    # paired table start/end.  We only try to look for these outside templates,
    # as it is common to write each template argument on its own line starting
    # with a "|".
    outside = unpaired_text
    while True:
        #print("=== OUTSIDE ITER")
        prev = outside
        while True:
            newt = re.sub(r"(?s)\{\{\{([^{}]|\}[^}]|\}\}[^}])*?\}\}\}",
                          "", prev)
            if newt == prev:
                break
            prev = newt
        #print("After arg elim: {!r}".format(newt))
        newt = re.sub(r"(?s)\{\{([^{}]|\}[^}])*?\}\}", "", newt)
        #print("After templ elim: {!r}".format(newt))
        if newt == outside:
            break
        outside = newt
    # For now, we'll ignore !! and ||
    m = re.search(r"(?s)(^|\n)(\|\+|\|-|\||\!)", outside)
    contains_table_element = m is not None
    # if contains_table_element:
    #     print("contains_table_element {!r} at {}"
    #           "".format(m.group(0), m.start()))
    #     print("... {!r} ...".format(outside[m.start() - 10:m.end() + 10]))
    #     print(repr(outside))

    # Check for unpaired HTML tags
    tag_cnts = collections.defaultdict(int)
    for m in re.finditer(r"(?si)<\s*(/\s*)?({})\b\s*[^>]*(/\s*)?>"
                         r"".format("|".join(PAIRED_HTML_TAGS)), outside):
        start_slash = m.group(1)
        tagname = m.group(2)
        end_slash = m.group(3)
        if start_slash:
            tag_cnts[tagname] -= 1
        elif not end_slash:
            tag_cnts[tagname] += 1
    contains_unbalanced_html = any(v != 0 for v in tag_cnts.values())
    # if contains_unbalanced_html:
    #     print(name, "UNBALANCED HTML")
    #     for k, v in tag_cnts.items():
    #         if v != 0:
    #             print("  {} {}".format(v, k))

    # Determine whether this template should be pre-expanded
    pre_expand = (contains_list or contains_unpaired_table or
                  contains_table_element or contains_unbalanced_html)

    # if pre_expand:
    #     print(name,
    #           {"list": contains_list,
    #            "unpaired_table": contains_unpaired_table,
    #            "table_element": contains_table_element,
    #            "unbalanced_html": contains_unbalanced_html,
    #            "pre_expand": pre_expand,
    #     })

    # Determine which other templates are called from unpaired text.
    # None of the flags we currently gather propagate outside a paired
    # table start/end.
    for m in re.finditer(r"(?s)(^|[^{])(\{\{)?\{\{([^{]*?)(\||\}\})",
                         unpaired_text):
        name = m.group(3)
        name = re.sub(r"(?si)<\s*nowiki\s*/\s*>", "", name)
        name = canonicalize_template_name(name)
        if not name:
            continue
        included_templates.add(name)

    return included_templates, pre_expand


def phase1_to_ctx(phase1_data):
    """Extract module and template definitions from the special pages and
    other data collected in phase1.  We also determine which templates
    need to be pre-expanded to allow parsing the resulting structure.
    (This determination is somewhat heuristic and is not guaranteed to
    always produce optimal results.  However, it significantly improves
    the parseability of the resulting structure of a page.)"""
    assert isinstance(phase1_data, (list, tuple))
    ctx = ExpandCtx()
    ctx.modules = {}
    ctx.templates = {}
    # Some predefined templates
    ctx.templates["!"] = "&vert;"
    ctx.templates["%28%28"] = "&lbrace;&lbrace;"  # {{((}}
    ctx.templates["%29%29"] = "&rbrace;&rbrace;"  # {{))}}
    ctx.need_pre_expand = set()
    ctx.redirects = {}
    included_map = collections.defaultdict(set)
    expand_q = []
    for tag, title, text in phase1_data:
        title = html.unescape(title)
        text = html.unescape(text)
        if tag == "#redirect":
            ctx.redirects[title] = text
            continue
        if tag == "Scribunto":
            ctx.modules[title] = text
            continue
        if title.endswith("/testcases"):
            continue
        if title.startswith("User:"):
            continue
        if tag != "Template":
            continue

        # print(tag, title)
        name = canonicalize_template_name(title)
        body = template_to_body(title, text)
        assert isinstance(body, str)
        included_templates, pre_expand = analyze_template(name, body)
        for x in included_templates:
            included_map[x].add(name)
        if pre_expand:
            ctx.need_pre_expand.add(name)
            expand_q.append(name)
        ctx.templates[name] = body

    # Propagate pre_expand from lower-level templates to all templates that
    # refer to them
    while expand_q:
        name = expand_q.pop()
        if name not in included_map:
            continue
        for inc in included_map[name]:
            if inc in ctx.need_pre_expand:
                continue
            #print("propagating EXP {} -> {}".format(name, inc))
            ctx.need_pre_expand.add(inc)
            expand_q.append(name)

    # Copy template definitions to redirects to them
    for k, v in ctx.redirects.items():
        if not k.startswith("Template:"):
            # print("Unhandled redirect src", k)
            continue
        k = k[9:]
        if not v.startswith("Template:"):
            # print("Unhandled redirect dst", v)
            continue
        v = v[9:]
        k = canonicalize_template_name(k)
        v = canonicalize_template_name(v)
        if v not in ctx.templates:
            # print("{} redirects to non-existent template {}".format(k, v))
            continue
        if k in ctx.templates:
            # print("{} -> {} is redirect but already in templates"
            #       "".format(k, v))
            continue
        ctx.templates[k] = ctx.templates[v]
        if v in ctx.need_pre_expand:
            ctx.need_pre_expand.add(k)

    return ctx


def lua_loader(ctx, modname):
    """This function is called from the Lua sandbox to load a Lua module.
    This will load it from either the user-defined modules on special
    pages or from a built-in module in the file system.  This returns None
    if the module could not be loaded."""
    # print("Loading", modname)
    if modname.startswith("Module:"):
        modname = modname[7:]
    if modname in ctx.modules:
        return ctx.modules[modname]
    path = modname
    path = re.sub(r":", "/", path)
    path = re.sub(r" ", "_", path)
    # path = re.sub(r"\.", "/", path)
    path = re.sub(r"//+", "/", path)
    path = re.sub(r"\.\.", ".", path)
    if path.startswith("/"):
        path = path[1:]
    path += ".lua"
    for prefix, exceptions in builtin_lua_search_paths:
        if modname in exceptions:
            continue
        p = prefix + "/" + path
        if os.path.isfile(p):
            with open(p, "r") as f:
                data = f.read()
            return data
    return None


def mw_text_decode(text, decodeNamedEntities=False):
    """Implements the mw.text.decode function for Lua code."""
    if decodeNamedEntities:
        return html.unescape(text)

    # Otherwise decode only selected entities
    parts = []
    pos = 0
    for m in re.finditer(r"&(lt|gt|amp|quot|nbsp);", text):
        if pos < m.start():
            parts.append(text[pos:m.start()])
        pos = m.end()
        tag = m.group(1)
        if tag == "lt":
            parts.append("<")
        elif tag == "gt":
            parts.append(">")
        elif tag == "amp":
            parts.append("&")
        elif tag == "quot":
            parts.append('"')
        elif tag == "nbsp":
            parts.append("\xa0")
        else:
            assert False
    parts.append(text[pos:])
    return "".join(parts)

def mw_text_encode(text, charset='<>&\xa0"'):
    """Implements the mw.text.encode function for Lua code."""
    parts = []
    for ch in str(text):
        if ch in charset:
            chn = ord(ch)
            if chn in html.entities.codepoint2name:
                parts.append("&" + html.entities.codepoint2name.get(chn) + ";")
            else:
                parts.append(ch)
        else:
            parts.append(ch)
    return "".join(parts)


def get_page_info(ctx, title):
    """Retrieves information about a page identified by its table (with
    namespace prefix.  This returns a lua table with fields "id", "exists",
    and "redirectTo".  This is used for retrieving information about page
    titles."""
    assert isinstance(title, str)

    # XXX actually look at information collected in phase 1 to determine
    page_id = 0  # XXX collect required info in phase 1
    page_exists = False  # XXX collect required info in Phase 1
    redirect_to = ctx.redirects.get(title, None)

    # whether the page exists and what its id might be
    dt = {
        "id": page_id,
        "exists": page_exists,
        "redirectTo": redirect_to,
    }
    return ctx.lua.table_from(dt)


def get_page_content(ctx, title):
    """Retrieves the full content of the page identified by the title.
    Currently this will only return content for the current page.
    This returns None if the page is other than the current page, and
    False if the page does not exist (currently not implemented)."""
    assert isinstance(title, str)
    if title == ctx.title:
        return ctx.fullpage
    return None


def fetch_language_name(code):
    """This function is called from Lua code as part of the mw.language
    inmplementation.  This maps a language code to its name."""
    if code in LANGUAGE_CODE_TO_NAME:
        return LANGUAGE_CODE_TO_NAME[code]
    return None


def fetch_language_names(ctx, include):
    """This function is called from Lua code as part of the mw.language
    implementation.  This returns a list of known language names."""
    include = str(include)
    if include == "all":
        ret = LANGUAGE_CODE_TO_NAME
    else:
        ret = {"en": "English"}
    return ctx.lua.table_from(dt)


def initialize_lua(ctx):
    assert isinstance(ctx, ExpandCtx)
    assert ctx.lua is None
    # Load Lua sandbox code.
    lua_sandbox = open("lua/sandbox.lua").read()

    def filter_attribute_access(obj, attr_name, is_setting):
        print("FILTER:", attr_name, is_setting)
        if isinstance(attr_name, unicode):
            if not attr_name.startswith("_"):
                return attr_name
        raise AttributeError("access denied")

    lua = LuaRuntime(unpack_returned_tuples=True,
                     register_eval=False,
                     attribute_filter=filter_attribute_access)
    lua.execute(lua_sandbox)
    lua.eval("lua_set_loader")(lambda x: lua_loader(ctx, x),
                               mw_text_decode,
                               mw_text_encode,
                               lambda x: get_page_info(ctx, x),
                               lambda x: get_page_content(ctx, x),
                               fetch_language_name,
                               lambda x: fetch_language_names(ctx, x))
    ctx.lua = lua


def expand_wikitext(ctx, title, text, templates_to_expand=None,
                    template_fn=None, fullpage=None):
    """Expands templates and parser functions (and optionally Lua macros)
    from ``text`` (which is from page with title ``title``).
    ``templates_to_expand`` should be a set (or dictionary) containing
    those canonicalized template names that should be expanded (None
    expands all).  ``template_fn``, if given, will be used to expand
    templates; if it is not defined or returns None, the default
    expansion will be used (it can also be used to capture template
    arguments).  If ``fullpage`` is specified, it should be the
    original content of the given page (with any preprocesing); this
    may be used by Lua code (title:getContent()).  This returns the
    text with the given templates expanded."""
    assert isinstance(ctx, ExpandCtx)
    assert isinstance(title, str)
    assert isinstance(text, str)
    assert isinstance(templates_to_expand, (set, dict, type(None)))
    assert template_fn is None or callable(template_fn)
    assert isinstance(fullpage, (str, type(None)))
    ctx.title = title
    ctx.template_fn = template_fn
    ctx.cookies = []
    ctx.fullpage = fullpage
    ctx.rev_ht = {}

    # If templates_to_expand is None, then expand all known templates
    if templates_to_expand is None:
        templates_to_expand = ctx.templates

    def unexpanded_template(args):
        """Formats an unexpanded template (whose arguments may have been
        partially or fully expanded)."""
        return "{{" + "|".join(args) + "}}"

    def invoke_fn(invoke_args, expander, stack, parent):
        """This is called to expand a #invoke parser function."""
        assert isinstance(invoke_args, (list, tuple))
        assert callable(expander)
        assert isinstance(stack, list)
        assert isinstance(parent, (tuple, type(None)))
        # print("invoke_fn", invoke_args)
        # sys.stdout.flush()
        if len(invoke_args) < 2:
            print("#invoke {}: too few arguments at {}"
                  "".format(invoke_args, stack))
            return ("{{" + invoke_args[0] + ":" +
                    "|".join(invoke_args[1:]) + "}}")

        # Initialize the Lua sandbox if not already initialized
        if ctx.lua is None:
            initialize_lua(ctx)
        lua = ctx.lua

        # Get module and function name
        modname = invoke_args[0].strip()
        modfn = invoke_args[1].strip()

        def value_with_expand(frame, fexpander, x):
            assert isinstance(frame, dict)
            assert isinstance(fexpander, str)
            assert isinstance(x, str)
            obj = {"expand": lambda obj: frame[fexpander](x)}
            return lua.table_from(obj)

        def make_frame(pframe, title, args):
            assert isinstance(title, str)
            assert isinstance(args, (list, tuple, dict))
            # Convert args to a dictionary with default value None
            if isinstance(args, dict):
                frame_args = args
            else:
                assert isinstance(args, (list, tuple))
                frame_args = {}
                num = 1
                for arg in args:
                    m = re.match(r"""^\s*([^<>="']+?)\s*=\s*(.*?)\s*$""", arg)
                    if m:
                        # Have argument name
                        k, arg = m.groups()
                        if k.isdigit():
                            k = int(k)
                            if k < 1 or k > 1000:
                                k = 1000
                            if num <= k:
                                num = k + 1
                    else:
                        # No argument name
                        k = num
                        num += 1
                    frame_args[k] = arg
            frame_args = lua.table_from(frame_args)

            def extensionTag(frame, *args):
                if len(args) < 1:
                    print("extensionTag: missing arguments at {}".format(stack))
                    return ""
                dt = args[0]
                if not isinstance(dt, (str, int, float, type(None))):
                    name = str(dt["name"] or "")
                    content = str(dt["content"] or "")
                    attrs = dt["args"] or {}
                elif len(args) == 1:
                    name = str(args[0])
                    content = ""
                    attrs = {}
                elif len(args) == 2:
                    name = str(args[0] or "")
                    content = str(args[1] or "")
                    attrs = {}
                else:
                    name = str(args[0] or "")
                    content = str(args[1] or "")
                    attrs = args[2] or {}
                if not isinstance(attrs, str):
                    attrs = list(v if isinstance(k, int) else
                                 '{}="{}"'
                                 .format(k, html.escape(v, quote=True))
                                 for k, v in sorted(attrs.items(),
                                                    key=lambda x: str(x[0])))
                elif not attrs:
                    attrs = []
                else:
                    attrs = [attrs]

                stack.append("extensionTag()")
                ret = tag_fn(title, "#tag", [name, content] + attrs,
                             lambda x: x,  # Already expanded
                             stack)
                stack.pop()
                return ret

            def callParserFunction(frame, *args):
                if len(args) < 1:
                    print("callParserFunction: missing name at {}"
                          .format(stack))
                    return ""
                name = args[0]
                if not isinstance(name, str):
                    new_args = list(name["args"].values())
                    name = name["name"] or ""
                else:
                    new_args = []
                name = str(name)
                for arg in args[1:]:
                    if isinstance(arg, (int, float, str)):
                        new_args.append(str(arg))
                    else:
                        for k, v in sorted(arg.items(),
                                           key=lambda x: str(x[0])):
                            new_args.append(str(v))
                name = canonicalize_parserfn_name(name)
                if name not in PARSER_FUNCTIONS:
                    print("frame:callParserFunction(): undefined function "
                          "{!r} at {}".format(name, stack))
                    return ""
                return call_parser_function(name, new_args, lambda x: x,
                                            ctx.title, stack)

            def expand_all_templates(encoded):
                # Expand all templates here, even if otherwise only
                # expanding some of them.  We stay quiet about undefined
                # templates here, because Wiktionary Module:ugly hacks
                # generates them all the time.
                ret = expand(encoded, stack, parent, ctx.templates,
                             quiet=True)
                return ret

            def preprocess(frame, *args):
                if len(args) < 1:
                    print("preprocess: missing arg at {}".format(stack))
                    return ""
                v = args[0]
                if not isinstance(v, str):
                    v = str(v["text"] or "")
                # Expand all templates, in case the Lua code actually inspects
                # the output.
                v = ctx.encode(v)
                stack.append("frame:preprocess()")
                ret = expand_all_templates(v)
                stack.pop()
                return ret

            def expandTemplate(frame, *args):
                if len(args) < 1:
                    print("expandTemplate: missing arguments at {}"
                          "".format(stack))
                    return ""
                dt = args[0]
                if isinstance(dt, (int, float, str, type(None))):
                    print("expandTemplate: arguments should be named at {}"
                          "".format(stack))
                    return ""
                title = dt["title"] or ""
                args = dt["args"] or {}
                new_args = [title]
                for k, v in sorted(args.items(), key=lambda x: str(x[0])):
                    new_args.append("{}={}".format(k, v))
                sys.stdout.flush()
                encoded = ctx.save_value("T", new_args)
                stack.append("frame:expandTemplate()")
                ret = expand_all_templates(encoded)
                stack.pop()
                return ret

            # Create frame object as dictionary with default value None
            frame = {}
            frame["args"] = frame_args
            # argumentPairs is set in sandbox.lua
            frame["callParserFunction"] = callParserFunction
            frame["extensionTag"] = extensionTag
            frame["expandTemplate"] = expandTemplate
            # getArgument is set in sandbox.lua
            frame["getParent"] = lambda self: pframe
            frame["getTitle"] = lambda self: title
            frame["preprocess"] = preprocess
            # XXX still untested:
            frame["newParserValue"] = \
                lambda self, x: value_with_expand(self, "preprocess", x)
            frame["newTemplateParserValue"] = \
                lambda self, x: value_with_expand(self, "expand", x)
            frame["newChild"] = lambda title="", args="": \
                make_frame(self, title, args)
            return lua.table_from(frame)

        # Create parent frame (for page being processed) and current frame
        # (for module being called)
        if parent is not None:
            parent_title, page_args = parent
            expanded_key_args = {}
            for k, v in page_args.items():
                if isinstance(k, str):
                    expanded_key_args[expander(k)] = v
                else:
                    expanded_key_args[k] = v
            pframe = make_frame(None, parent_title, expanded_key_args)
        else:
            pframe = None
        frame = make_frame(pframe, modname, invoke_args[2:])

        # Call the Lua function in the given module
        sys.stdout.flush()
        stack.append("Lua:{}:{}()".format(modname, modfn))
        ret = lua.eval("lua_invoke")(modname, modfn, frame, ctx.title)
        if not isinstance(ret, (list, tuple)):
            ok, text = ret, ""
        elif len(ret) == 1:
            ok, text = ret[0], ""
        else:
            ok, text = ret[0], ret[1]
        stack.pop()
        if ok:
            if text is None:
                text = "nil"
            return str(text)
        print("LUA ERROR IN #invoke {} at {}".format(invoke_args, stack))
        if isinstance(text, Exception):
            parts = [str(text)]
            lst = traceback.format_exception(etype=type(text),
                                             value=text,
                                             tb=text.__traceback__)
            for x in lst:
                parts.append("\t" + x.strip())
            text = "\n".join(parts)
        elif not isinstance(text, str):
            text = str(text)
        parts = []
        in_traceback = 0
        for line in text.split("\n"):
            s = line.strip()
            if s == "[C]: in function 'xpcall'":
                break
            parts.append(line)
        print("\n".join(parts))
        return ""

    def expand(coded, stack, parent, templates_to_expand, quiet=False):
        """This function does most of the work for expanding encoded templates,
        arguments, and parser functions."""
        assert isinstance(coded, str)
        assert isinstance(stack, list)
        assert isinstance(parent, (tuple, type(None)))
        assert isinstance(templates_to_expand, (set, dict))
        assert quiet in (False, True)

        def expand_args(coded, argmap):
            assert isinstance(coded, str)
            assert isinstance(argmap, dict)
            parts = []
            pos = 0
            for m in re.finditer(r"!{}(.)(\d+)!".format(magic), coded):
                new_pos = m.start()
                if new_pos > pos:
                    parts.append(coded[pos:new_pos])
                pos = m.end()
                kind = m.group(1)
                idx = int(m.group(2))
                kind = m.group(1)
                kind2, args = ctx.cookies[idx]
                assert isinstance(args, tuple)
                assert kind == kind2
                if kind == "T":
                    # Template transclusion - map arguments in its arguments
                    new_args = tuple(map(lambda x: expand_args(x, argmap),
                                         args))
                    parts.append(ctx.save_value(kind, new_args))
                    continue
                if kind == "A":
                    # Template argument reference
                    if len(args) > 2:
                        print("{}: too many args ({}) in argument reference "
                              "{!r}".format(title, len(args), args))
                    stack.append("ARG-NAME")
                    k = expand(expand_args(args[0], argmap),
                               stack, parent, ctx.templates).strip()
                    stack.pop()
                    if k.isdigit():
                        k = int(k)
                    v = argmap.get(k, None)
                    if v is not None:
                        parts.append(v)
                        continue
                    if len(args) >= 2:
                        stack.append("ARG-DEFVAL")
                        ret = expand_args(args[1], argmap)
                        stack.pop()
                        parts.append(ret)
                        continue
                    # The argument is not defined (or name is empty)
                    arg = "{{{" + str(k) + "}}}"
                    parts.append(arg)
                    continue
                if kind == "L":
                    # Link to another page
                    content = args[0]
                    content = expand_args(content, argmap)
                    parts.append("[[" + content + "]]")
                    continue
                print("{}: expand_arg: unsupported cookie kind {!r} in {}"
                      "".format(title, kind, m.group(0)))
                parts.append(m.group(0))
            parts.append(coded[pos:])
            return "".join(parts)

        def expand_parserfn(fn_name, args):
            # Call parser function
            stack.append(fn_name)
            expander = lambda arg: expand(arg, stack, parent, ctx.templates)
            if fn_name == "#invoke":
                ret = invoke_fn(args, expander, stack, parent)
            else:
                ret = call_parser_function(fn_name, args, expander,
                                           title, stack)
            stack.pop()  # fn_name
            # XXX if lua code calls frame:preprocess(), then we should
            # apparently encode and expand the return value, similarly to
            # template bodies (without argument expansion)
            # XXX current implementation of preprocess() does not match!!!
            return ret

        # Main code of expand()
        parts = []
        pos = 0
        for m in re.finditer(r"!{}(.)(\d+)!".format(magic), coded):
            new_pos = m.start()
            if new_pos > pos:
                parts.append(coded[pos:new_pos])
            pos = m.end()
            kind = m.group(1)
            idx = int(m.group(2))
            kind2, args = ctx.cookies[idx]
            assert isinstance(args, tuple)
            assert kind == kind2
            if kind == "T":
                # Template transclusion or parser function call
                # Limit recursion depth
                if len(stack) >= 100:
                    print("{}: too deep expansion of templates via {}"
                          "".format(title, stack))
                    parts.append(unexpanded_template(args))
                    continue

                # Expand template/parserfn name
                stack.append("TEMPLATE_NAME")
                tname = expand(args[0], stack, parent, templates_to_expand)
                stack.pop()

                # Strip safesubst: and subst: prefixes
                tname = tname.strip()
                if tname[:10].lower() == "safesubst:":
                    tname = tname[10:]
                elif tname[:6].lower() == "subst:":
                    tname = tname[6:]

                # Check if it is a parser function call
                ofs = tname.find(":")
                if ofs > 0:
                    # It might be a parser function call
                    fn_name = canonicalize_parserfn_name(tname[:ofs])
                    # Check if it is a recognized parser function name
                    if fn_name in PARSER_FUNCTIONS or fn_name.startswith("#"):
                        ret = expand_parserfn(fn_name,
                                              (tname[ofs + 1:].lstrip(),) +
                                              args[1:])
                        parts.append(ret)
                        continue

                # As a compatibility feature, recognize parser functions
                # also as the first argument of a template (withoout colon),
                # whether there are more arguments or not.  This is used
                # for magic words and some parser functions have an implicit
                # compatibility template that essentially does this.
                fn_name = canonicalize_parserfn_name(tname)
                if fn_name in PARSER_FUNCTIONS or fn_name.startswith("#"):
                    ret = expand_parserfn(fn_name, args[1:])
                    parts.append(ret)
                    continue

                # Otherwise it must be a template expansion
                name = canonicalize_template_name(tname)
                if name.startswith("Template:"):
                    name = name[9:]

                # Check for undefined templates
                if name not in ctx.templates:
                    if not quiet:
                        print("{}: undefined template {!r} at {}"
                              "".format(title, tname, stack))
                    parts.append(unexpanded_template(args))
                    continue

                # If this template is not one of those we want to expand,
                # return it unexpanded (but with arguments possibly expanded)
                if name not in templates_to_expand:
                    parts.append(unexpanded_template(args))
                    continue

                # Construct and expand template arguments
                stack.append(name)
                ht = {}
                num = 1
                for i in range(1, len(args)):
                    arg = str(args[i])
                    m = re.match(r"""^\s*([^<>="']+?)\s*=\s*(.*?)\s*$""", arg)
                    if m:
                        # Note: Whitespace is stripped by the regexp
                        # around named parameter names and values per
                        # https://en.wikipedia.org/wiki/Help:Template
                        # (but not around unnamed parameters)
                        k, arg = m.groups()
                        if k.isdigit():
                            k = int(k)
                            if k < 1 or k > 1000:
                                print("{}: invalid argument number {}"
                                      "".format(title, k))
                                k = 1000
                            if num <= k:
                                num = k + 1
                        else:
                            stack.append("ARGNAME")
                            k = expand(k, stack, parent, ctx.templates)
                            stack.pop()
                    else:
                        k = num
                        num += 1
                    # Expand arguments in the context of the frame where
                    # they are defined.  This makes a difference for
                    # calls to #invoke within a template argument (the
                    # parent frame would be different).
                    stack.append("ARGVAL-{}".format(k))
                    arg = expand(arg, stack, parent, ctx.templates)
                    stack.pop()
                    ht[k] = arg

                # Expand the body, either using ``template_fn`` or using
                # normal template expansion
                t = None
                if ctx.template_fn is not None:
                    t = template_fn(name, ht)
                if t is None:
                    body = ctx.templates[name]
                    # XXX optimize by pre-encoding bodies during preprocessing
                    # (Each template is typically used many times)
                    # Determine if the template starts with a list item
                    contains_list = re.match(r"(?s)^[#*;:]", body) is not None
                    if contains_list:
                        body = "\n" + body
                    encoded_body = ctx.encode(body)
                    # Expand template arguments recursively.  The arguments
                    # are already expanded.
                    encoded_body = expand_args(encoded_body, ht)
                    # Expand the body using the calling template/page as
                    # the parent frame for any parserfn calls
                    new_title = tname.strip()
                    for prefix in ("Media", "Special", "Main", "Talk", "User",
                                   "User_talk", "Project", "Project_talk",
                                   "File", "Image", "File_talk",
                                   "MediaWiki", "MediaWiki_talk",
                                   "Template", "Template_talk",
                                   "Help", "Help_talk", "Category",
                                   "Category_talk", "Module", "Module_talk"):
                        if tname.startswith(prefix + ":"):
                            break
                    else:
                        new_title = "Template:" + new_title
                    new_parent = (new_title, ht)
                    # XXX no real need to expand here, it will expanded on
                    # next iteration anyway (assuming parent unchanged)
                    # Otherwise expand the body
                    t = expand(encoded_body, stack, new_parent,
                               templates_to_expand)

                assert isinstance(t, str)
                stack.pop()  # template name
                parts.append(t)
            elif kind == "A":
                # The argument is outside transcluded template body
                arg = "{{{" + "|".join(args) + "}}}"
                parts.append(arg)
            elif kind == "L":
                # Link to another page
                content = args[0]
                stack.append("[[link]]")
                content = expand(content, stack, parent, templates_to_expand)
                stack.pop()
                parts.append("[[" + content + "]]")
            else:
                print("{}: expand: unsupported cookie kind {!r} in {}"
                      "".format(title, kind, m.group(0)))
                parts.append(m.group(0))
        parts.append(coded[pos:])
        return "".join(parts)

    # Encode all template calls, template arguments, and parser function
    # calls on the page.  This is an inside-out operation.
    # print("Encoding")
    encoded = ctx.encode(text)

    # Recursively expand the selected templates.  This is an outside-in
    # operation.
    # print("Expanding")
    expanded = expand(encoded, [title], None, templates_to_expand)

    return expanded
