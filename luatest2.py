import re
import sys
import html
import json
import os.path
import collections
import lupa
from lupa import LuaRuntime

# List of search paths for Lua libraries.
builtin_lua_search_paths = [
    "mediawiki-extensions-Scribunto/includes/engines/LuaCommon/lualib",
]

page = open("temp-pages/Words/an/animal.txt").read()
print("Len of source page", len(page))

with open("tempXXXspecials.json") as f:
    lst = json.load(f)


# Extract module and template definitions from the collected special pages.
modules = {}
templates = {}
for tag, title, text in lst:
    text = html.unescape(text)
    if tag == "Template":
        templates[title] = text
    if tag != "Scribunto":
        continue
    if title.endswith("/testcases"):
        continue
    if title.startswith("User:"):
        continue
    modules[title] = text

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
