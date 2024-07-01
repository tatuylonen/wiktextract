# Extracting the category tree from Wiktionary
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

from typing import (
    Optional,
    TypedDict,
)

from wikitextprocessor.core import NamespaceDataEntry

from wiktextract.wxr_context import WiktextractContext

from .page import clean_node

LUA_CODE = r"""
local export = {}

topic_data = require("Module:category tree/topic cat/data")
poscat_data = require("Module:category tree/poscatboiler/data")
top_data = require("Module:category tree/data")

local function extract_tree(data, parts)
  for k, v in pairs(data.LABELS) do
    desc = v.description or ""
    if type(desc) == "function" then
        -- Module:category tree/poscatboiler/data/non-lemma forms
        -- Turns out category tree can return a function where we
        -- expect a string, and the function is called with a `data`-
        -- table containing some kind of context data when appropriate,
        -- in a similar way to how all the {{{langname}}} calls are
        -- filled in when appropriate. However, we are just getting
        -- the "templates" here, so we don't have a context to call
        -- the function with: so instead just give it an empty table
        -- and hope the function has a sensible condition structure
        -- that first checks whether it should output a default:
        -- the gerund template in the above url does this.
        print("Function returned in description of category tree template `"..
              k.."`: "..tostring(v.description))
        desc = desc({})
    end
    print( k..": "..desc )
    desc = string.gsub(desc, "\n", "\\n")
    table.insert(parts, k .. "@@" .. desc)
    for kk, vv in pairs(v.parents) do
      local name
      local sort = ""
      if type(vv) == "table" then
        name = vv.name
        sort = vv.sort or ""
      else
        name = vv
      end
      if name then
        table.insert(parts, "@@" .. name .. "@@" .. sort)
      end
    end
    table.insert(parts, "\n")
  end
end

function export.main()
  local parts = {}
  extract_tree(topic_data, parts)
  extract_tree(poscat_data, parts)
  for k, v in pairs(top_data) do
    table.insert(parts, k .. "@@@@Fundamental@@\n")
  end
  local ret = table.concat(parts, "")
  return ret
end

return export
"""

CategoryEntry = TypedDict(
    "CategoryEntry",
    {
        "name": str,
        "desc": str,
        "clean_desc": str,
        "children": list[str],
        "sort": list[str],
    },
    total=False,
)

CategoryReturn = TypedDict(
    "CategoryReturn",
    {
        "roots": list[str],
        "nodes": dict[str, CategoryEntry],
    },
    total=False,
)

def extract_categories(wxr: WiktextractContext) -> CategoryReturn:
    """Extracts the category tree from Wiktionary."""
    module_ns: Optional[NamespaceDataEntry] = wxr.wtp.NAMESPACE_DATA.get(
                                                            "Module", None)
    assert module_ns is not None
    module_ns_local_name = module_ns.get("name")
    module_ns_id = module_ns.get("id")
    wxr.wtp.add_page(f"{module_ns_local_name}:wiktextract cat tree",
                 module_ns_id, LUA_CODE, model="Scribunto")
    wxr.wtp.start_page("Wiktextract category tree extraction")
    rawdata = wxr.wtp.expand("{{#invoke:wiktextract cat tree|main}}")
    ht: dict[str, CategoryEntry] = {}
    for line in rawdata.split("\n"):
        if not line:
            continue
        parts = line.split("@@")
        name = parts[0]
        desc = parts[1]
        name = name.removeprefix("Category:")
        name_lc = name.lower()
        clean_desc = clean_node(wxr, None, desc)
        if name_lc not in ht:
            ht[name_lc] = {"name": name}
        dt = ht[name_lc]
        if desc and not dt.get("desc"):
            dt["desc"] = desc
        if clean_desc and not dt.get("clean_desc"):
            dt["clean_desc"] = clean_desc
        for i in range(2, len(parts), 2):
            parent_name = parts[i]
            parent_name = parent_name.removeprefix("Category:")
            parent_name_lc = parent_name.lower()
            parent_sort = parts[i + 1]
            if parent_name_lc not in ht:
                p: CategoryEntry  = {"name": parent_name}
                ht[parent_name_lc] = p
            else:
                p = ht[parent_name_lc]
            if "children" not in p:
                p["children"] = []
            p["children"].append(name)
            if parent_sort and parent_sort.strip():
                if "sort" not in p:
                    p["sort"] = []
                p["sort"].append(parent_sort)

    seen: set[str] = set()
    is_child: set[str] = set()

    def recurse(name: str) -> None:
        if name in seen:
            return
        seen.add(name)
        for child in ht[name].get("children", ()):
            recurse(child.lower())

    recurse("fundamental")

    for k, v in ht.items():
        for child in v.get("children", ()):
            is_child.add(child.lower())

    notseen_set = set(x.lower() for x in ht.keys()) - seen - is_child
    notseen = list(ht[x]["name"] for x in sorted(notseen_set))
    #if notseen:
    #    print("NOT SEEN:", "; ".join(notseen))

    # Sort lists of children
    for v in ht.values():
        if "children" in v:
            v["children"] = list(sorted(v["children"]))

    roots = ["Fundamental"]
    roots.extend(notseen)
    ret: CategoryReturn = {"roots": roots, "nodes": ht}
    # import json
    # print(json.dumps(ret, sort_keys=True, indent=2))
    return ret
