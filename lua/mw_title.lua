-- Simplified implementation of mw.title for running WikiMedia Scribunto
-- code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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
   local ns = mw.site.findNamespace(namespace)
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
      if mw.site.matchNamespaceName(v, namespace) then
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

   -- mw_title.python_get_page_info is set in lua_set_fns
   local dt = mw_title.python_get_page_info(fullName)
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

return mw_title
