local env = _ENV

unpack = table.unpack

python_get_page_info = nil
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

local mw_title_meta = {
   contentModel = "wikitext",
   talkPageTitle = nil,
   protectionLevels = { nil },
   cascadingProtection = { restrictions = {}, sources = {} },
   canTalk = false
}
function mw_title_meta.__eq(a, b)
   return a.prefixedText == b.prefixedText
end

function mw_title_meta.__lt(a, b)
   return a.prefixedText < b.prefixedText
end

function mw_title_meta.__tostring(a)
   return a.prefixedText
end

function mw_title_meta.isSubpageOf(titleobj, titleobj2)
   assert(type(titleobj2) == "table")
   local t1 = titleobj.text
   local t2 = titleobj2.text
   if len(t1) >= len(t2) then
      return false
   end
   if string.sub(t2, 1, len(t1)) ~= t1 then
      return false
   end
   if string.sub(t2, len(t1), len(t1)) ~= "/" then
      return false
   end
   return true
end

function mw_title_meta.inNamespace(titleobj, ns)
   assert(type(ns) == "string")
   v = mw.site.namespaces[titleobj.namespace]
   if ns == v.name then return true end
   if ns == v.canonicalName then return true end
   for i, alias in ipairs(v.aliases) do
      if ns == alias then return true end
   end
   return false
end

function mw_title_meta.inNamespaces(titleobj, ...)
   for i, ns in ipairs(...) do
      if titleobj.inNamespace(ns) then return true end
   end
   return false
end

function mw_title_meta.hasSubjectNamespace(titleobj, ns)
   error("XXX hasSubjectNamespace not yet implemented")
end

function mw_title_meta.subPageTitle(titleobj, text)
   error("XXX subPageTitle not yet implemented")
end

function mw_title_meta.partialUrl(titleobj)
   error("XXX partialUrl not yet implemented")
end

function mw_title_meta.fullUrl(titleobj, query, proto)
   error("XXX fullUrl not yet implemented")
end

function mw_title_meta.localUrl(titleobj, query)
   error("XXX localUrl not yet implemented")
end

function mw_title_meta.canonicalUrl(titleobj, query)
   error("XXX canonicalUrl not yet implemented")
end

function mw_title_meta.getContent(titleobj)
   error("XXX getContent not yet implemented")
end

function mw_title_meta.__index(titleobj, key)
   if v == "basePageTitle" then
      error("XXX basePageTitle not yet implemented")
   end
   if v == "rootPageTitle" then
      error("XXX rootPageTitle not yet implemented")
   end
   if v == "subjectPageTitle" then
      error("XXX subjectPageTitle not yet implemented")
   end
   return nil
end

local mw_title = {
   -- equals
   -- compare
   -- getCurrentTitle
   -- new
   -- makeTitle  (see below)
}

function mw_title.makeTitle(namespace, title, fragment, interwiki)
   assert(title)
   if not namespace then namespace = "Main" end
   local ns = findNamespace(namespace)
   if not ns then
      print("mw.title.makeTitle: could not find namespace",
            namespace, title, fragment, interwiki)
      assert(ns)
   end
   if interwiki then
      print("mw_title.makeTitle called with interwiki", interwiki)
   end
   -- XXX how should interwiki be handled?
   -- w: (wikipedia)
   -- m: (or meta:) for Meta-Wiki
   -- mw: (MediaWiki)
   -- wikt: (Wiktionary)
   -- en: (English)
   -- fr: (French language)
   -- de: (German language)
   -- and other language prefixes
   -- :en: links to English wikipedia etc
   -- interwiki prefixes are case-insensitive
   local isContent = false
   for i, v in pairs(mw.site.contentNamespaces) do
      if matchNamespaceName(v, namespace) then
         isContent = true
         break
      end
   end
   local root = string.gsub(title, "/.*", "")
   local parent = string.gsub(title, "/[^/]*", "")
   local subpage = string.gsub(title, ".*/", "")
   local fullName
   if namespace == "Main" then
      fullName = title
   else
      fullName = namespace + ":" + title
   end
   local withFrag
   if fragment then
      withFrag = fullName + "#" + fragment
   else
      withFrag = fullName
   end

   local dt = python_get_page_info(fullName)
   local id = dt.id
   local exists = dt.exists
   local redirectTo = dt.redirectTo

   local t = {
      __index = mw_title_meta,
      namespace = ns,
      id = id,
      interwiki = interwiki,
      fragment = fragment,
      nsText = namespace,    -- ???
      subjectNsText = namespace,  -- ???
      text = title,
      prefixedText = fullName,
      fullText = withFrag,
      rootText = root,
      baseText = parent,
      subpageText = subpage,
      exists = exists,
      -- XXX file: see https://www.mediawiki.org/wiki/Extension:Scribunto/Lua_reference_manual
      file = nil,
      isContentPage = isContent,
      isExternal = interwiki ~= nil,  -- ???
      isLocal = interwiki == nil,   -- ???
      isRedirect = redirectTo ~= nil,
      isSpecialPage = namespace == "Special",
      isSubpage = title ~= base,
      redirectTarget = redirectTo,
   }
   setmetatable(t, mw_title_meta)
   return t
end

function mw_title.new(text, namespace)
   assert(type(text) == "string")
   if not namespace then namespace = "Main" end
   local idx = string.find(text, ":")
   if idx ~= nil then
      namespace = string.sub(text, 1, idx - 1)
      text = string.sub(text, idx + 1)
   end
   assert(namespace)
   return mw_title.makeTitle(namespace, text)
end

function mw_title.getCurrentTitle()
   local frame = mw.getCurrentFrame()
   local parent = frame:getParent()
   local title = parent:getTitle()
   local newtitle = mw_title.new(title, "Main")
   return newtitle
end

function mw_title.equals(a, b)
   return a.fullName == b.fullName
end

function mw_title.compare(a, b)
   if a.interwiki < b.interwiki then return -1 end
   if a.interwiki > b.interwiki then return 1 end
   if a.namespace < b.namespace then return -1 end
   if a.namespace > b.namespace then return 1 end
   if a.text < b.text then return -1 end
   if a.text > b.text then return 1 end
   return 0
end

local mw_text = {
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

local Language = {
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

local mw_language = {
   -- fetchLanguageName(code, inLanguage)
   -- fetchLanguageNames(inLanguage=None, include=None)
   -- getContentLanguage()
   -- getFallbacksFor(code)
   -- isKnownLanguageTag(code)  -- assigned in lua_set_fns
   -- isSupportedLanguage(code)
   -- isValidBuiltInCode(code)
   -- isValidCode(code)
   -- new(code)
}

function matchNamespaceName(v, name)
   -- namespace prefixes are case-insensitive
   assert(type(name) == "string")
   name = string.upper(name)
   if name == string.upper(v.name) then return true end
   if name == string.upper(v.canonicalName) then return true end
   for i, alias in ipairs(v.aliases) do
      if name == string.upper(alias) then return true end
   end
   return false
end

function findNamespace(name)
   assert(type(name) == "string")
   for k, v in pairs(mw.site.namespaces) do
      if matchNamespaceName(v, name) then return true end
   end
   return nil
end

local Namespace = {
   hasGenderDistinction = true,
   isCapitalized = false,
   isMovable = false,
   defaultContentModel = "wikitext",
   aliases = {},
   associated = nil,  -- ???
}

function Namespace:new(obj)
   obj = obj or {}
   setmetatable(obj, self)
   self.__index = self
   obj.canonicalName = obj.name
   obj.displayName = obj.name
   obj.hasSubpages = obj.name == "Main" or obj.name == "Module"
   return obj
end

local media_ns = Namespace:new{id=-2, name="Media", isSubject=true}
local special_ns = Namespace:new{id=-1, name="Special", isSubject=true}
local main_ns = Namespace:new{id=0, name="Main", isContent=true, isSubject=true}
local talk_ns = Namespace:new{id=1, name="Talk", isTalk=true, subject=main_ns}
local user_ns = Namespace:new{id=2, name="User", isSubject=true}
local user_talk_ns = Namespace:new{id=3, name="User_talk", isTalk=true,
                                   subject=user_ns}
local project_ns = Namespace:new{id=4, name="Project", isSubject=true}
local project_talk_ns = Namespace:new{id=5, name="Project_talk", isTalk=true,
                                      subject=project_ns}
local image_ns = Namespace:new{id=6, name="Image", isSubject=true}
local image_talk_ns = Namespace:new{id=7, name="Image_talk", isTalk=true,
                                    subject=image_ns}
local mediawiki_ns = Namespace:new{id=8, name="MediaWiki", isSubject=true}
local mediawiki_talk_ns = Namespace:new{id=9, name="MediaWiki_talk",
                                        isTalk=true, subject=mediawiki_ns}
local template_ns = Namespace:new{id=10, name="Template", isSubject=true}
local template_talk_ns = Namespace:new{id=11, name="Template_talk", isTalk=true,
                                       subject=template_ns}
local help_ns = Namespace:new{id=12, name="Help", isSubject=true}
local help_talk_ns = Namespace:new{id=13, name="Help_talk", isTalk=true,
                                   subject=help_ns}
local category_ns = Namespace:new{id=14, name="Category", isSubject=true}
local category_talk_ns = Namespace:new{id=15, name="Category_talk", isTalk=true,
                                       subject=category_ns}
local module_ns = Namespace:new{id=828, name="Module", isIncludable=true,
                                isSubject=true}
local module_talk_ns = Namespace:new{id=829, name="Module_talk", isTalk=true,
                                     subject=module_ns}
main_ns.talk = talk_ns
user_ns.talk = user_talk_ns
project_ns.talk = project_talk_ns
mediawiki_ns.talk = mediawiki_talk_ns
template_ns.talk = template_talk_ns
help_ns.talk = help_talk_ns
category_ns.talk = category_talk_ns
module_ns.talk = module_talk_ns

function add_ns(t, ns)
   t[ns.id] = ns
end

local mw_site_namespaces = {}
add_ns(mw_site_namespaces, media_ns)
add_ns(mw_site_namespaces, special_ns)
add_ns(mw_site_namespaces, main_ns)
add_ns(mw_site_namespaces, talk_ns)
add_ns(mw_site_namespaces, user_ns)
add_ns(mw_site_namespaces, user_talk_ns)
add_ns(mw_site_namespaces, project_ns)
add_ns(mw_site_namespaces, project_talk_ns)
add_ns(mw_site_namespaces, image_ns)
add_ns(mw_site_namespaces, image_talk_ns)
add_ns(mw_site_namespaces, mediawiki_ns)
add_ns(mw_site_namespaces, mediawiki_talk_ns)
add_ns(mw_site_namespaces, template_ns)
add_ns(mw_site_namespaces, template_talk_ns)
add_ns(mw_site_namespaces, help_ns)
add_ns(mw_site_namespaces, help_talk_ns)
add_ns(mw_site_namespaces, category_ns)
add_ns(mw_site_namespaces, category_talk_ns)
add_ns(mw_site_namespaces, module_ns)
add_ns(mw_site_namespaces, module_talk_ns)

local mw_site_contentNamespaces = {}
add_ns(mw_site_contentNamespaces, main_ns)

local mw_site_subjectNamespaces = {}
add_ns(mw_site_subjectNamespaces, media_ns)
add_ns(mw_site_subjectNamespaces, special_ns)
add_ns(mw_site_subjectNamespaces, main_ns)
add_ns(mw_site_subjectNamespaces, user_ns)
add_ns(mw_site_subjectNamespaces, project_ns)
add_ns(mw_site_subjectNamespaces, image_ns)
add_ns(mw_site_subjectNamespaces, mediawiki_ns)
add_ns(mw_site_subjectNamespaces, template_ns)
add_ns(mw_site_subjectNamespaces, help_ns)
add_ns(mw_site_subjectNamespaces, category_ns)
add_ns(mw_site_subjectNamespaces, module_ns)

local mw_site_talkNamespaces = {}
add_ns(mw_site_talkNamespaces, talk_ns)
add_ns(mw_site_talkNamespaces, user_talk_ns)
add_ns(mw_site_talkNamespaces, project_talk_ns)
add_ns(mw_site_talkNamespaces, image_talk_ns)
add_ns(mw_site_talkNamespaces, mediawiki_talk_ns)
add_ns(mw_site_talkNamespaces, template_talk_ns)
add_ns(mw_site_talkNamespaces, help_talk_ns)
add_ns(mw_site_talkNamespaces, category_talk_ns)
add_ns(mw_site_talkNamespaces, module_talk_ns)

function mw_site_index(x, ns)
   return findNamespace(ns)
end

local mw_site = {
   __index = mw_site_index,
   server = "server.dummy",
   siteName = "Dummy Site",
   namespaces = mw_site_namespaces,
   contentNamespaces = mw_site_contentNamespaces,
   subjectNamespaces = mw_site_subjectNamespaces,
   talkNamespaces = mw_site_talkNamespaces,
   stats = {
      pages = 0,
      articles = 0,
      files = 0,
      users = 0,
      activeUsers = 0,
      admins = 0
   }
}

function mw_site.stats.pagesInCategory(category, which)
   if which == "*" or which == nil then
      return {
         all = 0,
         subcats = 0,
         files = 0,
         pages = 0
      }
   end
   return 0
end

function mw_site.stats.pagesInNamespace(ns)
   return 0
end

function mw_site.stats.usersInGroup(filter)
   return 0
end

function mw_site.interwikiMap(filter)
   print("mw.site.interwikiMap called", filter)
   return {}
end

mw = {
   -- addWarning  (see below)
   -- allToString  (see below)
   -- clone  (see below)
   -- dumpObject  (see below)
   -- getCurrentFrame -- assigned in lua_invoke for each call
  hash = mw_hash,
  -- XXX html.*
  -- incrementExpensiveFunctionCount (see below)
  -- isSubsting  (see below)
  language = mw_language,
  -- loadData  (see below)
  log = mw_log,
  -- logObject  (see below)
  -- XXX message.*
  site = mw_site,
  text = mw_text,
  title = mw_title,
  -- XXX uri.*
  -- ustring = ustring,  -- assigned in lua_set_loader
}

function mw.addWarning(text)
   print("mw.addWarning", text)
end

function mw.allToString(...)
   local ret = ""
   for k, v in pairs(...) do
      ret = ret .. tostring(v)
   end
   return ret
end

function deepcopy(obj, visited)
   -- non-table objects can be returned as-is
   if type(obj) ~= "table" then return obj end
   -- handle cyclic data structures
   if visited[obj] ~= nil then return visited[obj] end
   -- copy the table
   local new_table = {}
   for k, v in pairs(obj) do
      new_table[deepcopy(k, visited)] = deepcopy(v, visited)
   end
   -- copy metatable pointer
   setmetatable(new_table, getmetatable(obj))
   -- track that we have visited this node and save the copy
   visited[obj] = new_table
   return new_table
end

function mw.clone(v)
   return deepcopy(v, {})
end

function mw.dumpObject(obj)
  print("mw.dumpObject", obj)
end

function mw.incrementExpensiveFunctionCount()
   print("mw.incrementExpensiveFunctionCount")
end

function mw.isSubsting()
   return false
end

-- mw.loadData function - loads a data file.  This implements caching
-- for performance.
function mw.loadData(module)
  local v = data_cache[module]
  if v ~= nil then
     return v
  end
  local fn = new_loader(module)
  v = fn()
  data_cache[module] = v
  return v
end

function mw.log(...)
  print("mw.log", ...)
end

function mw.logObject(obj)
  print("mw.logObject", obj)
end

-- This should be called immediately after loading the sandbox to set the
-- Python function that will be used for loading Lua modules.
function lua_set_loader(loader)
  python_loader.call = loader
  ustring = require("ustring:ustring")
  mw.ustring = ustring
end

function lua_set_fns(mw_text_decode, mw_text_encode,
                     mw_language_is_known_language_tag,
                     get_page_info)
  mw.text.decode = mw_text_decode
  mw.text.encode = mw_text_encode
  mw.language.isKnownLanguageTag = mw_language_is_known_language_tag
  python_get_page_info = get_page_info
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

-- math.log10 seems to be sometimes missing???
function math.log10(x)
   return math.log(x, 10)
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
