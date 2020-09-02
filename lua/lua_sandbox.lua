local env = _ENV

unpack = table.unpack

python_loader = {}
data_cache = {}

-- This function loads new a new module, whether built-in or defined in the
-- data file.
function new_loader(modname)
  local content = nil
  if python_loader.call ~= nil then
    content = python_loader.call(modname)
  else
     error("PYTHON LOADER NOT SET - call lua_set_loader() first")
  end
  if content == nil then
     error("MODULE NOT FOUND: " .. modname)
  end

  -- Wikimedia uses an older version of Lua.  Make certain substitutions
  -- to make existing code run on more modern versions of Lua.
  content = string.gsub(content, "%%\\%[", "%%[")

  -- Load the content into the Lua interpreter.
  ret = assert(load(content, modname, "bt", env))
  return ret
end

-- Register the new loader as the only package searcher in Lua.
package.searchers = {}
package.searchers[0] = nil
package.searchers[1] = new_loader

-- mw.loadData function - loads a data file.  This implements caching
-- for performance.
function mw_loadData(module)
  v = data_cache[module]
  if v ~= nil then
     return v
  end
  fn = new_loader(module)
  v = fn()
  data_cache[module] = v
  return v
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
local new_os = {
   clock = os.clock,
   date = os.date,
   difftime = os.difftime,
   time = os.time,
}
local mw_hash = {
  hashValue = mw_hash_hashValue,
  listAlgorithms = mw_hash_listAlgorithms,
}

local title_obj = {
   -- XXX many other fields too
  namespace = 0,
  text = "TESTWORDT",
  fullPagename = "TESTWORDT",
  nsText = "",
  subpageText = "TESTWORDT",
}

local mw_title = {
   -- equals
   -- compare
   -- getCurrentTitle below
   -- new
   -- makeTitle
}
function mw_title.getCurrentTitle()
  return title_obj
end

mw_text = {
   -- decode (set from Python)
   -- encode (set from Python)
   -- jsonDecode
   -- jsonEncode
   -- killMarkers
   -- listToText
   -- nowiki
   -- split (see below)
   -- gsplit (see below)
   -- tag
   -- trim (see below)
   -- truncate
   -- unstripNoWiki
   -- unstrip
}

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

mw_language = {
   -- fetchLanguageName(code, inLanguage)
   -- fetchLanguageNames(inLanguage=None, include=None)
   -- getContentLanguage()
   -- getFallbacksFor(code)
   -- isKnownLanguageTag(code)  -- assigned in lua_set_fns
   -- isSupportedLanguage(code)
   -- isValidBuiltInCode(code)
   -- isValidCode(code)
   -- new(code)
   -- :getCode()
   -- :getFallbackLanguages()
   -- :isRTL()
   -- :lc(s)
   -- :lcfirst(s)
   -- :uc(s)
   -- :ucfirst(s)
   -- :caseFold(s)
   -- :formatNum(n, options=None)
   -- :formatdate(format, timestamp, local)
   -- :formatDuration(seconds, allowedIntervals=None)
   -- :parseFormattedNumber(s)
   -- :convertPlural(n, forms)
   -- :plural(n, forms)
   -- :convertGrammar(word, case)
   -- :grammar(case, word)
   -- :gender(what, masculine, feminine, neutral) / :gender(what, {masculine, feminine, neutral})
   -- :getArrow(direction)
   -- :getDir()
   -- :getDirMark(opposite)
   -- :getDirMarkEntity(opposite)
   -- :getDurationIntervals(seconds, allowedIntervals)
}

function mw_dumpObject(obj)
  print("MW_DUMPOBJECT")
end

mw = {
   -- addWarning
   -- allToString
   -- clone
  dumpObject = mw_dumpObject,
  getCurrentFrame = function() return frame end,
  hash = mw_hash,
  -- html.*
  -- incrementExpensiveFunctionCount
  -- isSubsting
  language = mw_language,
  loadData = mw_loadData,
  log = mw_log,
  logObject = mw_logObject,
  -- message.*
  -- site.*
  text = mw_text,
  title = mw_title,
  -- uri.*
  -- ustring = ustring,  -- assigned in lua-set-loader
}

function page_getTitle(self)
  print("page_getTitle called")
  return "TESTWORD"
end

-- This should be called immediately after loading the sandbox to set the
-- Python function that will be used for loading Lua modules.
function lua_set_loader(loader)
  python_loader.call = loader
  ustring = require("ustring:ustring")
  mw.ustring = ustring
end

function lua_set_fns(mw_text_decode, mw_text_encode,
                     mw_language_is_known_language_tag)
  mw.text.decode = mw_text_decode
  mw.text.encode = mw_text_encode
  mw.language.isKnownLanguageTag = mw_language_is_known_language_tag
end

-- This function implements the {{#invoke:...}} parser function.
-- XXX need better handling of parent frame and frame
-- This returns (true, value) if successful, (false, error) if exception.
function lua_invoke(mod_name, fn_name, frame)
  mod = require(mod_name)
  fn = mod[fn_name]
  frame.argumentPairs = function () return pairs(frame.args) end
  pframe = frame:getParent()
  if pframe ~= nil then
     pframe.argumentPairs = function () return pairs(pframe.args) end
  end
  mw.getCurrentFrame = function() return frame end
  if fn == nil then
     return {false, "\tNo function '" .. fn_name .. "' in module " .. mod_name}
  else
     return xpcall(function() return fn(frame) end, debug.traceback)
  end
end

env = {}
env["_G"] = env
env["_VERSION"] = _VERSION
env["assert"] = assert
env["debug"] = new_debug
env["error"] = error
env["frame"] = frame
env["getmetatable"] = getmetatable  -- MODIFY
env["ipairs"] = ipairs
env["lua_invoke"] = lua_invoke
env["lua_set_loader"] = lua_set_loader
env["math"] = math
env["mw"] = mw
env["next"] = next
env["os"] = new_os
env["pairs"] = pairs
env["pcall"] = pcall
env["print"] = print
env["rawequal"] = rawequal
env["rawget"] = rawget
env["rawset"] = rawset
env["require"] = require
env["select"] = select
env["setmetatable"] = setmetatable
env["string"] = string
env["table"] = table
env["tonumber"] = tonumber
env["tostring"] = tostring
env["type"] = type
env["unpack"] = table.unpack
env["xpcall"] = xpcall   -- MODIFY

local _ENV = env

-- built-in modules:
    -- bit32
    -- libraryUtil
    -- luabit


-- frame.args uses lazy evaluation apparently - only expand args when they
-- are actually used
