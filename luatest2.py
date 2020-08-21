import re
import sys
import copy
import html
import json
import time
import textwrap
import os.path
import collections
import lupa
from lupa import LuaRuntime

from wiktextract import wikitext
from wiktextract.wikitext import WikiNode, NodeKind

#import pstats
#import cProfile


# List of search paths for Lua libraries.
builtin_lua_search_paths = [
    "mediawiki-extensions-Scribunto/includes/engines/LuaCommon/lualib",
]

MAX_LEN = 75

page = open("tests/animal.txt").read()
#print("Len of source page", len(page))

langs = collections.defaultdict(int)

print("Loading specials (templates & modules)")
with open("tempXXXspecials.json") as f:
    specials = json.load(f)
print("Extracting definitions", len(specials))


def canonicalize_template_name(name):
    assert isinstance(name, str)
    name = re.sub(r"_", " ", name)
    name = re.sub(r"\s+", " ", name)
    name = name.strip()
    name = name[0].lower() + name[1:]
    return name


def template_to_body(title, text):
    tree = wikitext.parse(title, text)
    explicit_body = []

    def recurse_list(lst):
        ret = []
        for x in lst:
            ret1 = recurse(x)
            if isinstance(ret1, list):
                ret.extend(ret1)
            elif ret1 is not None:
                ret.append(ret1)
        return ret

    def recurse(node):
        """This may return str, WikiNode, or list."""
        if isinstance(node, str):
            return node
        assert isinstance(node, WikiNode)
        kind = node.kind
        if kind == NodeKind.HTML:
            tag = node.args
            assert isinstance(tag, str)
            if tag == "onlyinclude":
                explicit_body.extend(recurse_list(node.children))
            elif tag == "includeonly":
                return recurse_list(node.children)
            elif tag == "noinclude":
                return None
        # print("Recursing into {}".format(node.kind))
        new_node = copy.copy(node)
        new_node.children = recurse_list(node.children)
        if isinstance(node.args, (list, tuple)):
            new_node.args = list(recurse_list(x) for x in node.args)
        return new_node

    body = recurse(tree)
    if explicit_body:
        return explicit_body
    # print("{} BODY".format(title))
    # wikitext.print_tree(body)
    return body


# Extract module and template definitions from the collected special pages.
modules = {}
templates = {}
for tag, title, text in specials:
    # XXX should this be enabled? title = html.unescape(title)
    if tag == "Scribunto":
        continue
    if title.endswith("/testcases"):
        continue
    if title.startswith("User:"):
        continue
    if tag != "Template":
        continue

    print(tag, title)
    text = html.unescape(text)
    body = template_to_body(title, text)
    name = canonicalize_template_name(title)
    templates[name] = body

class FmtCtx(object):
    __slots__ = (
        "indent",  # Current indent for text
        "inpara",  # True if inside paragraph
        "nowrap",  # True to suppress line wrap at current position
        "parts",   # Text accumulated here (list of str)
        "pos",     # Character position on current line
        "space",   # True if space should be inserted before next text
        "variables",  # Dictionary mapping template arg name (str) to value
    )
    def __init__(self):
        self.indent = 0
        self.inpara = False
        self.nowrap = False
        self.parts = []
        self.pos = 0
        self.space = False
        self.variables = {}

    def add(self, txt):
        assert isinstance(txt, str)
        for w in re.split(r"(\s+)", txt):
            if not w:
                continue
            if w.isspace():
                self.space = True
                continue
            # We are adding a non-space segment
            w = html.unescape(w)
            if (self.pos > 0 and self.pos + len(w) + 1 > MAX_LEN and
                not self.nowrap and
                (self.space or
                 (not self.parts[-1][-1].isalnum() or
                  not self.parts[-1][-1].isalnum()))):
                self.parts.append("\n")
                self.pos = 0
                self.space = False
                if self.pos == 0 and self.indent > 0:
                    self.parts.append(" " * self.indent)
                    self.pos += self.indent
            if self.space:
                self.space = False
                if (self.pos > 0 and not self.nowrap and self.parts and
                      not self.parts[-1][-1].isspace()):
                    self.parts.append(" ")
                    self.pos += 1
            self.parts.append(w)
            self.pos += len(w)
            self.inpara = True
            self.nowrap = False

    def add_prefix(self, txt):
        assert isinstance(txt, str)
        self.newline()
        if self.pos == 0 and self.indent > 0:
            self.parts.append(" " * self.indent)
            self.pos += self.indent
        self.parts.append(txt)
        self.pos += len(txt)
        self.nowrap = True
        self.inpara = True
        self.space = False

    def newline(self):
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")
            self.pos = 0

    def newpara(self):
        if self.inpara:
            self.newline()
            self.parts.append("\n")
            self.inpara = False
            self.nowrap = False

def list_to_text(ctx, node):
    prefix = node.args
    number = 1
    ctx.newline()
    for child in node.children:
        if not isinstance(child, WikiNode) or child.kind != NodeKind.LIST_ITEM:
            print("Unexpected item under list: {}".format(child.kind))
            continue
        if prefix.endswith("#"):
                p = "{}. ".format(number)
                number += 1
        elif prefix.endswith("*"):
            p = "* "
        elif prefix.endswith(":"):
            p = "    "
        else:
            p = "? "
        ctx.add_prefix(p)
        ctx.indent += len(p)
        to_text_recurse(ctx, child)
        ctx.indent -= len(p)
        ctx.newline()

def link_to_text(ctx, node):
    assert isinstance(node, WikiNode)
    trail = to_text(ctx, node.children).strip()
    page = to_text(ctx, node.args[0]).strip()
    if len(node.args) > 1:
        txt = to_text(ctx, node.args[1]).strip()
    else:
        txt = page
    if not txt:
        # Pipe trick
        txt = page
        idx = txt.find(":")
        if idx >= 0:
            txt = txt[idx + 1:]
        idx = txt.find("(")
        if idx >= 0:
            txt = txt[:idx]
        else:
            idx = txt.find(",")
            if idx >= 0:
                txt = txt[:idx]
        txt = txt.strip()
    # XXX should we do some inflection with trail links?
    ctx.add(txt + trail)


def template_to_text(ctx, node):
    assert isinstance(ctx, FmtCtx)
    assert isinstance(node, WikiNode)

    # Clean up template name to canonical form
    name = to_text(ctx, node.args[0])
    name = canonicalize_template_name(name)

    body = templates.get(name)

    if body is None:
        print("Reference to undefined template {!r}".format(name))
        ctx.add("{{")
        to_text_list(ctx, node.args[0])
        for x in node.args[1:]:
            ctx.add("|")
            to_text_list(ctx, x)
        ctx.add("}}")
        return

    old_vars = ctx.variables
    new_vars = old_vars.copy()
    argnum = 1
    for x in node.args[1]:
        txt = to_text(ctx, x)
        m = re.match(r"(?s)^([^][#<>\{\}\|])=(.*)$", txt)
        if m:
            argname = m.group(1).strip()
            argvalue = m.group(2).strip()
        else:
            argname = str(argnum)
            argnum += 1
            argvalue = txt
        new_vars[argname] = argvalue

    ctx.variables = new_vars
    to_text_list(ctx, body)
    ctx.variables = old_vars


def templatevar_to_text(ctx, node):
    ctx.add("{{{")
    to_text_list(ctx, node.args[0])
    for x in node.args[1:]:
        ctx.add("|")
        to_text_list(ctx, x)
    ctx.add("}}}")

def parserfn_to_text(node):
    ctx.add("{{")
    to_text_list(ctx, node.args[0])
    ctx.add(":")
    if len(node.args) > 1:
        to_text_list(node.args[1])
        for x in node.args[2:]:
            ctx.add("|")
            to_text_list(ctx, x)
    ctx.add("}}")

def title_to_text(ctx, node, underline):
    txt = to_text(ctx, node.args[0]).strip()
    ctx.newpara()
    ctx.add_prefix(txt)
    ctx.newline()
    ctx.add_prefix(underline * len(txt))
    ctx.newpara()
    to_text_list(ctx, node.children)

def to_text_list(ctx, lst):
    assert isinstance(lst, (list, tuple))
    for x in lst:
        to_text_recurse(ctx, x)

def to_text_recurse(ctx, node):
    assert isinstance(node, (str, WikiNode))
    if isinstance(node, str):
        ctx.add(node)
        return
    kind = node.kind
    if kind == NodeKind.LEVEL2:
        title_to_text(ctx, node, "#")
    elif kind == NodeKind.LEVEL3:
        title_to_text(ctx, node, "=")
    elif kind == NodeKind.LEVEL4:
        title_to_text(ctx, node, "-")
    elif kind == NodeKind.LEVEL5:
        title_to_text(ctx, node, "~")
    elif kind == NodeKind.LEVEL6:
        title_to_text(ctx, node, ".")
    elif kind == NodeKind.LIST:
        list_to_text(ctx, node)
    elif kind == NodeKind.HLINE:
        ctx.newpara()
        ctx.add_prefix("-" * (MAX_LEN - ctx.indent))
        ctx.newpara()
    elif kind == NodeKind.PRE:
        ctx.newpara()
        txt = "".join(node.children).strip()
        for line in txt.split("\n"):
            ctx.add_prefix(line)
            ctx.newline()
        ctx.newpara()
    elif kind == NodeKind.LINK:
        link_to_text(ctx, node)
    elif kind == NodeKind.TEMPLATE:
        template_to_text(ctx, node)
    elif kind == NodeKind.TEMPLATEVAR:
        templatevar_to_text(ctx, node)
    elif kind == NodeKind.PARSERFN:
        parserfn_to_text(ctx, node)
    elif kind == NodeKind.URL:
        if len(node.args) > 1:
            to_text_list(ctx, node.args[1])
        else:
            to_text_list(ctx, node.args[0])
    elif kind == NodeKind.TABLE:
        parts.append("<XXX TABLE>")
    elif kind == NodeKind.MAGIC_WORD:
        # Magic word - generate no output
        # XXX check if some should generate output
        pass
    else:
        to_text_list(ctx, node.children)


def to_text(ctx, lst):
    """Converts content from ``lst`` to text (str).  Template variables are
    taken from ``ctx``, but otherwise a new context will be used and ``ctx``
    will not be modified."""
    assert isinstance(ctx, FmtCtx)
    assert isinstance(lst, (list, tuple))
    new_ctx = FmtCtx()
    new_ctx.variables = ctx.variables.copy()
    for x in lst:
        to_text_recurse(new_ctx, x)
    return "".join(new_ctx.parts)


def analyze_node(node):
    if isinstance(node, str):
        return
    assert isinstance(node, WikiNode)
    kind = node.kind
    if kind == NodeKind.LEVEL2:
        ctx = FmtCtx()
        title = to_text(ctx, node.args[0]).strip()
        langs[title] += 1

    for x in node.children:
        analyze_node(x)

tree = wikitext.parse("animal", page)
analyze_node(tree)
#for k, v in sorted(langs.items(), key=lambda x: x[1], reverse=True):
#    print(v, k)

ctx = FmtCtx()
print(to_text(ctx, tree.children).strip())
print("============================")
wikitext.print_tree(tree)

sys.exit(1)

print("Total length of modules:", sum(len(x) for x in modules.values()))
print("Total length of templates:", sum(len(x) for x in templates.values()))

param_re = re.compile(
    r"(?s)\{\{\{\s*([^|{}]+?)\s*"
    r"(\|\s*(([^{}]|\}[^{}]|\}\}[^{}])*?)\s*)?\}\}\}")

template_re = re.compile(
    r"(?s)\{\{([^|{}]+?)"
    r"((\|([^|{}]+?))*?)"
    r"\}\}")

# Recursively substitutes all occurrences of ``regexp`` by the result of
# fn(m) for its match object on original text ``text``.  This keeps repeating
# the substitutions until there are no more changes.  However this imposes
# an arbitrary limit of 100 iterations to ensure termination.
def iter_sub(regexp, fn, text):
    for iter in range(0, 100):
        prev = text
        text = re.sub(regexp, fn, text)
        if text == prev:
            break
    return text

def lua_loader(modname):
    """This function is called from the Lua sandbox to load a Lua module.
    This will load it from either the user-defined modules on special
    pages or from a built-in module in the file system.  This returns None
    if the module could not be loaded."""
    if modname.startswith("Module:"):
        modname = modname[7:]
    if modname in modules:
        return modules[modname]
    path = modname
    path = re.sub(r":", "/", path)
    path = re.sub(r" ", "_", path)
    path = re.sub(r"\.", "/", path)
    path = re.sub(r"//+", "/", path)
    path = re.sub(r"\.\.", ".", path)
    if path.startswith("/"):
        path = path[1:]
    path += ".lua"
    for prefix in builtin_lua_search_paths:
        p = prefix + "/" + path
        if os.path.isfile(p):
            with open(p, "r") as f:
                data = f.read()
            return data
    print("MODULE NOT FOUND:", modname)
    return None

# Load Lua sandbox code.
lua_sandbox = open("lua_sandbox.lua").read()

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
lua.eval("lua_set_loader")(lua_loader)

def invoke_script(name, ht):
    if name not in modules:
        print("UNRECOGNIZED SCRIPT:", name)
        return "<<UNRECOGNIZED SCRIPT: {}>>".format(name)
    if name.find('"') >= 0:
        print("Invalid lua module name:", name)
        return "<<INVALID LUA MODULE NAME: {}>>".format(name)
    fn_name = ht.get("1")
    if not fn_name or fn_name.find('"') >= 0:
        print("Invalid function name in lua call:", fn_name)
        return "<<INVALID FUNCTION NAME: {}>>".format(fn_name)

    fn = lua.eval("lua_invoke")(name, fn_name, ht)
    print("LUA EXPANSION RETURNED:", ret)
    return ret

def expand(text, param_ht):
    def expand_template_param(m):
        name = m.group(1)
        defval = m.group(3) or ""
        print("EXPAND_TEMPLATE", repr(name), repr(defval))
        return param_ht.get(name, defval)

    def invoke_special(name, ht):
        if name.startswith("#invoke:"):
            return invoke_script(name[8:], ht)
        print("UNHANDLED SPECIAL TEMPLATE:", name)
        return "<<UNHANDLED SPECIAL {}>>".format(name)

    def expand_template_body(name, body, ht):
        """Expands template body, processing only included material."""
        # First handle <onlyinclude> by removing everything outside it
        if re.search("(?i)<\s*onlyinclude\s*>", body):
            lst = []
            for m in re.finditer(
                    r"(?si)<\s*onlyinclude\s*>(.*?)<\s*/\s*onlyinclude\s*>"):
                lst.append(m.group(1))
            body = "".join(lst)

        # Remove material inside <noinclude> ... </noinclude>
        body = re.sub(r"(?si)<\s*noinclude\s*>.*?<\s*/\s*noinclude\s*>",
                      "", body)

        # Remove <includeonly> tags
        body = re.sub(r"(?si)<\s*(/\s*)?includeonly\s*>", "", body)

        # XXX should we add parameter for template name?

        return expand(body, ht)

    def invoke_template(name, ht):
        if name.startswith("#"):
            return invoke_special(name, ht)
        if name in templates:
            return expand_template_body(name, templates[name], ht)
        print("UNRECOGNIZED TEMPLATE:", name)
        return "<<<UNRECOGNIZED {}>>>".format(name)

    def expand_template(m):
        template_name = m.group(1).strip()
        params = m.group(2).strip()
        ht = {}
        i = 1
        for param in params.split("|")[1:]:
            param = param.strip()
            mm = re.match(r"(?s)^([^=]+)=(.*)$", param)
            if mm:
                param_name = mm.group(1).strip()
                v = mm.group(2).strip()
            else:
                param_name = str(i)
                i += 1
                v = param
            ht[param_name] = v
        print("{} {}".format(template_name, ht))
        return invoke_template(template_name, ht)

    # Expand parameters
    text = iter_sub(param_re, expand_template_param, text)

    # Expand templates
    text = iter_sub(template_re, expand_template, text)

    return text

def test(orig, param_ht):
    v = expand(orig, param_ht)
    print("{}: {!r} -> {!r}".format(param_ht, orig, v))

test("foo", {})
test("{{{foo", {})
test("{{{foo}}}", {})
test("a{{{foo}}}b", {"foo": "bar"})
templates["foo"] = "FOO{{{1|-noarg}}}"
test("a{{foo}}b", {})
test("a{{foo||}}b", {})
test("a{{foo|11|22}}b", {})
test("a{{foo|x=xx|11|22}}b", {})
test("{{Arachnida Hypernyms}}", {})
sys.exit(1)

all_defs = "".join(modules.values())

cnts = collections.defaultdict(int)

for m in re.finditer(r"""[^a-zA-Z0-9._]([a-zA-Z0-9._]+)""", all_defs):
    t = m.group(1)
    if not t:
        continue
    if t.isdigit():
        continue
    cnts[t] += 1

for k, v in sorted(cnts.items(), key=lambda x: x[1], reverse=True):
    print(v, k)
