-- Simplified implementation of mw.title for running WikiMedia Scribunto
-- code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local mw_title_meta = {
}

function mw_title_meta:__index(key)
   local v = rawget(mw_title_meta, key)
   if v ~= nil then return v end
   if key == "basePageTitle" then
      return mw.title.new(self.baseText, self.nsText)
   end
   if key == "rootPageTitle" then
      return mw.title.new(self.rootText, self.nsText)
   end
   if key == "subjectPageTitle" then
      return mw.title.new(self.text, self.subjectNsText)
   end
   if key == "contentModel" then return "wikitext" end
   if key == "talkPageTitle" then
      local talk_ns = mw.site.namespaces[self.namespace].talk
      if talk_ns == nil then return nil end
      return mw.title.new(self.text, talk_ns.name)
   end
   if key == "protectionLevels" then return { nil } end
   if key == "cascadingProtection" then
      return { restrictions = {}, sources = {} }
   end
   if key == "canTalk" then return false end
   if key == "redirectTarget" then
      return mw.title.new(self._redirectTarget)
   end
   return nil
end

function mw_title_meta.__eq(a, b)
   return a.prefixedText == b.prefixedText
end

function mw_title_meta.__lt(a, b)
   return a.prefixedText < b.prefixedText
end

function mw_title_meta:__tostring()
   return self.prefixedText
end

function mw_title_meta:isSubpageOf(titleobj2)
   assert(type(titleobj2) == "table")
   if self.nsText ~= titleobj2.nsText then return false end
   local t1 = titleobj2.text
   local t2 = self.text
   if #t1 >= #t2 then
      return false
   end
   if string.sub(t2, 1, #t1) ~= t1 then
      return false
   end
   if string.sub(t2, #t1 + 1, #t1 + 1) ~= "/" then
      return false
   end
   return true
end

function mw_title_meta:inNamespace(ns)
   assert(type(ns) == "string" or type(ns) == "number")
   local ns1 = mw.site.namespaces[self.namespace]
   local ns2 = mw.site.namespaces[ns]
   assert(ns1 ~= nil and ns2 ~= nil)
   if ns1.name == ns2.name then return true end
   return false
end

function mw_title_meta:inNamespaces(...)
   for i, ns in ipairs({...}) do
      if self:inNamespace(ns) then return true end
   end
   return false
end

function mw_title_meta:hasSubjectNamespace(namespace)
   local ns = mw.site.findNamespace(namespace)
   return ns.name == self.subjectNsText
end

function mw_title_meta:subPageTitle(text)
   return mw.title.makeTitle(self.namespace, self.text .. "/" .. text)
end

function mw_title_meta:partialUrl()
   return mw.uri.encode(self.text, "WIKI")
end

function mw_title_meta:fullUrl(query, proto)
   local uri = mw.uri.fullUrl(self.fullText, query)
   if proto ~= nil and proto ~= "" then uri = proto .. ":" .. uri end
   return uri
end

function mw_title_meta:localUrl(query)
   return mw.uri.localUrl(self.fullText, query)
end

function mw_title_meta:canonicalUrl(query)
   return mw.uri.canonicalUrl(self.fullText, query)
end

function mw_title_meta:getContent()
   return mw.title.python_get_page_content(self.fullText)
end

local mw_title = {
   -- equals
   -- compare
   -- getCurrentTitle
   -- new
   -- makeTitle  (see below)
}

function mw_title.makeTitle(namespace, title, fragment, interwiki)
   if title == nil or title == "" then return nil end
   if title:find("%%[0-9a-fA-F][0-9a-fA-F]") then return nil end
   if title:find("#") then return nil end
   if title:find("<") then return nil end
   if title:find(">") then return nil end
   if title:find("%[") then return nil end
   if title:find("%]") then return nil end
   if title:find("|") then return nil end
   if title:find("{") then return nil end
   if title:find("}") then return nil end
   if title:find("_") then return nil end
   if title:sub(1, 1) == ":" then return nil end
   if title == "." or title == ".." then return nil end
   if title:sub(1, 2) == "./" or title:sub(1, 3) == "../" then return nil end
   if title:find("/%./") or title:find("/%.%./") then return nil end
   if title:sub(-2) == "/." or title:sub(-3) == "/.." then return nil end
   if #title > 255 then return nil end
   if title:sub(1, 1) == " " or title:sub(-1) == " " then return nil end
   if title:find("  ") then return nil end
   if title:find("~~~~") then return nil end
   local prefixes = {"Talk:", "WP:", "WT:", "Project:", "Image:",
                     "Media:", "Special:"}
   -- XXX other disallowed prefixes, see
   -- https://www.mediawiki.org/wiki/Special:Interwiki
   for i, prefix in ipairs(prefixes) do
      if title:sub(1, #prefix) == prefix then return nil end
   end
   -- XXX there are also other disallowed titles, see
   -- https://www.mediawiki.org/wiki/Manual:Page_title
   if not namespace or namespace == "" then namespace = "Main" end
   local ns = mw.site.findNamespace(namespace)
   if not ns then
      return nil
   end
   if interwiki then
      error("XXX unimplemented: mw_title.makeTitle called with interwiki: " ..
            interwiki)
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
   local root = string.gsub(title, "/.*$", "")
   local parent = string.gsub(title, "/[^/]*$", "")
   local subpage = string.gsub(title, "^.*/", "")
   local fullName
   if ns.name == "Main" then
      fullName = title
   else
      fullName = ns.name .. ":" .. title
   end
   local withFrag
   if fragment then
      withFrag = fullName .. "#" .. fragment
   else
      withFrag = fullName
   end

   -- mw_title.python_get_page_info is set in lua_set_fns
   local dt = mw_title.python_get_page_info(ns.name .. ":" .. title)
   local id = dt.id
   local exists = dt.exists
   local redirectTo = dt.redirectTo

   local t = {
      namespace = ns.id,
      id = id,
      interwiki = interwiki or "",
      fragment = fragment,
      nsText = ns.name,    -- ???
      subjectNsText = (ns.subject or ns).name,
      text = title,
      prefixedText = ns.name .. ":" .. title,
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
      isSpecialPage = ns.name == "Special",
      isSubpage = title ~= base,
      isTalkPage = ns.name == "Talk" or string.find(ns.name, "_talk") ~= nil,
      _redirectTarget = redirectTo,
   }
   setmetatable(t, mw_title_meta)
   return t
end

function mw_title.new(text, namespace)
   if type(text) == "number" then
      error("XXX mw.title.new with id not yet implemented")
   end
   assert(type(text) == "string")
   if not namespace then namespace = "Main" end
   local idx = string.find(text, ":")
   if idx ~= nil then
      local ns1 = string.sub(text, 1, idx - 1)
      local nsobj = mw.site.findNamespace(ns1)
      if nsobj ~= nil then
         namespace = ns1
         text = string.sub(text, idx + 1)
      end
   end
   return mw_title.makeTitle(namespace, text)
end

function mw_title.getCurrentTitle()
   local t = mw_title.new(mw._pageTitle)
   if t == nil then
      print("mw.title.getCurrentTitle returns nil:", mw._pageTitle)
   end
   return t
   -- local frame = mw.getCurrentFrame()
   -- local parent = frame:getParent() or frame
   -- local title = parent:getTitle()
   -- local newtitle = mw_title.new(title, "Main")
   -- return newtitle
end

function mw_title.equals(a, b)
   return a.fullText == b.fullText
end

function mw_title.compare(a, b)
   if a.interwiki < b.interwiki then return -1 end
   if a.interwiki > b.interwiki then return 1 end
   if a.nsText < b.nsText then return -1 end
   if a.nsText > b.nsText then return 1 end
   if a.text < b.text then return -1 end
   if a.text > b.text then return 1 end
   return 0
end

return mw_title
