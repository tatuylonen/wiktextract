import re
import sys
import lupa
from lupa import LuaRuntime

def filter_attribute_access(obj, attr_name, is_setting):
    print("FILTER:", attr_name, is_setting)
    if isinstance(attr_name, unicode):
        if not attr_name.startswith("_"):
            return attr_name
    raise AttributeError("access denied")

lua = LuaRuntime(unpack_returned_tuples=True,
                 register_eval=False,
                 attribute_filter=filter_attribute_access)

# XXX frame
# XXX mw.html
# XXX mw.language
# XXX mw.message
# XXX mw.site
# XXX mw.text
# XXX mw.title
# XXX mw.uri
# XXX mw.ustring
# XXX loadable: bit32
# XXX loadable: libraryUtil
# XXX loadable: luabit
# XXX mw.wikibase
# XXX mw.wikibase.lexeme
# XXX mw.wikibase.mediainfo
# XXX mw.bcmath
# XXX mw.smw
# XXX mw.ext.data
# XXX mw.ext.cargo
# XXX mw.ext.cattools
# XXX mw.ext.FlaggedRevs
# XXX mw.ext.TitleBlackList
# XXX mw.ext.articlePlaceholder

sandbox = r"""
local env = _ENV

unpack = table.unpack

function new_loader(modname)
  modname = string.gsub(modname, ":", "/")
  modname = string.gsub(modname, " ", "_")
  modname = string.gsub(modname, "%.", "/")
  path = package.searchpath(modname, "./mediawiki-extensions-Scribunto/includes/engines/LuaCommon/lualib/?.lua;./pages/?.txt") or error("MODULE NOT FOUND: " .. modname)
  print("FOUND", modname, "->", path)
  local file = io.open(path, "rb")
  local content = file:read("*a")
  content = string.gsub(content, "%%\\%[", "%%[")
  file:close()
  ret = assert(load(content, path, "bt", env))
  return ret
end

package.searchers = {}
package.searchers[0] = nil
package.searchers[1] = new_loader

ustring = require("ustring.ustring")

function mw_loadData(module)
  fn = new_loader(module)
  return fn()
end

function mw_dumpObject(obj)
  print("MW_DUMPOBJECT")
end

function mw_log(...)
  print("MW_LOG")
end

function mw_logObject(obj)
  print("MW_LOGOBJECT")
end

function mw_hash_hashValue(algo, value)
  print("MW_HASH_HASHVALUE")
end

function mw_hash_listAlgorithms()
  print("MW_HASH_LISTALGORITHMS")
  return {}
end

local new_debug = { traceback = debug.traceback }
local new_os = { clock = os.clock, date = os.date, difftime = os.difftime,
           time = os.time }
local mw_hash = {
  hashValue = mw_hash_hashValue,
  listAlgorithms = mw_hash_listAlgorithms,
}

local title_obj = {
  namespace = 0,
  text = "TESTWORDT",
  fullPagename = "TESTWORDT",
  nsText = "",
  subpageText = "TESTWORDT",
}

local title = {
}
function title.getCurrentTitle()
  return title_obj
end

mw_text = {}

function mw_text.trim(val)
   return (val:gsub("^%s*(.-)%s*$", "%1"))
end

function mw_text.split(text, pattern, plain)
  local ret = {}
  for m in mw_text.gsplit(text, pattern, plain) do
    ret[#ret + 1] = m
  end
  return ret
end

function mw_text.gsplit(text, pattern, plain)
  local s, l = 1, ustring.len(text)
  return function ()
    if s then
      local e, n = ustring.find(text, pattern, s, plain)
      local ret
      if not e then
        ret = ustring.sub(text, s)
        s = nil
      elseif n < e then
        ret = ustring.sub(text, s, e)
        if e < l then
          s = e + 1
        else
          s = nil
        end
      else
        ret = e > s and ustring.sub(text, s, e - 1) or ''
        s = n + 1
      end
      return ret
    end
  end, nil, nil
end

mw = {
  loadData = mw_loadData,
  dumpObject = mw_dumpObject,
  log = mw_log,
  logObject = mw_logObject,
  hash = mw_hash,
  title = title,
  text = mw_text,
  ustring = ustring,
  getCurrentFrame = function() return frame end,
}

function page_getTitle(self)
  print("page_getTitle called")
  return "TESTWORD"
end

page_frame = {
  getTitle = page_getTitle,
  args = {"talossa"},
}

function frame_getTitle(self)
  print("frame_getTitle called")
  return "Module:IPA"
end

function frame_getParent(self)
  print("frame_getParent called")
  return page_frame
end

frame = {
  args = { "nouns" },
  getTitle = frame_getTitle,
  getParent = frame_getParent,
}

print("ARGS[0]", frame.args[0])
print("ARGS[1]", frame.args[1])

env = {}
env["math"] = math
env["string"] = string
env["table"] = table
env["print"] = print
env["require"] = require
env["_VERSION"] = _VERSION
env["assert"] = assert
env["unpack"] = table.unpack
env["error"] = error
env["getmetatable"] = getmetatable
env["next"] = next
env["pairs"] = pairs
env["ipairs"] = ipairs
env["pcall"] = pcall
env["rawequal"] = rawequal
env["rawget"] = rawget
env["rawset"] = rawset
env["select"] = select
env["setmetatable"] = setmetatable
env["tonumber"] = tonumber
env["tostring"] = tostring
env["type"] = type
env["xpcall"] = xpcall
env["debug"] = new_debug
env["os"] = new_os
env["mw"] = mw
env["frame"] = frame
env["_G"] = env

local _ENV = env
"""

code = """
m = require("Module:fi-IPA")
print("LOADED", m)
if m == nil then
  return nil
end

local v = m.IPA(frame)
print("RESULT:", v)
return v
"""

#m = require("Module:et-IPA")
#print("LOADED", m)
#ipa = m.IPA(frame)
#print("IPA", ipa)


#
#sandbox.math = lua.globals().math
#sandbox.string = lua.globals().string
# etc

#setfenv(0, sandbox)

ret = lua.execute(sandbox + code)
print("RET", ret)
ret = re.sub(r"<.*?>", "", ret)
ret = re.sub(r"&#32;", "", ret)
ret = re.sub(r"\[\[(Wiktionary|Category|Appendix):[^]]*\]\]", "", ret)
ret = re.sub(r"\(\):", "", ret)
print("CLEAN", ret)
