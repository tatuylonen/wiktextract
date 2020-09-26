-- Simplified implementation of mw.uri for running WikiMedia Scribunto code
-- under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local scribunto_mwuri = require("mw.uri")

local DEFAULT_HOST = "wiki.local"

local Uri = {
   protocol = "https",
   -- user
   -- password
   host = DEFAULT_HOST,
   port = 80,
   path = "/w/index.php",
   query = {},
   fragment = ""
   -- userInfo
   -- hostPort
   -- authority
   -- queryString
   -- relativePath
   -- completeUrl (internal)
}

function Uri:new(obj)
   obj = obj or {}
   setmetatable(obj, self)
   self.__index = self
   return obj
end

function Uri:__tostring()
   return self.completeUrl
end

function Uri:update()
   -- internal function for updating userInfo, hostPoret, authority,
   -- queryString, relativePath, completeUrl after computing rest
   local enc = function(s) return mw.uri.encode(s, "QUERY") end
   local url = enc(self.protocol) .. "://"
   if self.user then
      local userinfo = enc(self.user)
      if self.password then
         userinfo = userinfo .. ":" .. enc(self.password)
      end
      self.userInfo = userinfo
   else
      self.userInfo = ""
   end
   local hostport = self.host
   if self.port and self.port ~= 80 then
      hostport = hostport .. ":" .. tostring(self.port)
   end
   self.hostPort = hostport
   if self.userInfo ~= "" then
      self.authority = self.userInfo .. "@" .. self.hostPort
   else
      self.authority = self.hostPort
   end
   url = url .. self.authority
   local relpath = mw.uri.encode(self.path, "WIKI")
   local qs = {}
   local first = true
   for k, v in pairs(self.query) do
      if type(v) ~= "function" then
         if v == false then
            table.insert(qs, k)
         else
            table.insert(qs, enc(tostring(k)) .. "=" .. enc(tostring(v)))
         end
      end
   end
   table.sort(qs)
   self.queryString = table.concat(qs, "&")
   if self.queryString ~= "" then
      relpath = relpath .. "?" .. self.queryString
   end
   if self.fragment and self.fragment ~= "" then
      relpath = relpath .. "#" .. enc(self.fragment)
   end
   self.relativePath = relpath
   url = url .. relpath
   self.completeUrl = url
end

function Uri:parse(s)
   local ofs
   if string.match(s, "[a-z0-9]+:") then
      ofs = string.find(s, ":")
      self.protocol = string.sub(s, 1, ofs - 1)
      s = string.sub(s, ofs + 1)
   end
   if string.sub(s, 1, 2) == "//" then
      s = string.sub(s, 3)
      -- next is optional user@password, followed by mandatory host
      if string.match(s, "[^#?/@]+@.*") then
         ofs = string.find(s, "@")
         local userpass = string.sub(s, 1, ofs - 1)
         s = string.sub(s, ofs + 1)
         ofs = string.find(userpass, ":")
         if ofs then
            local user = string.sub(userpass, 1, ofs - 1)
            local pass = string.sub(userpass, ofs + 1)
            self.user = mw.uri.decode(user, "QUERY")
            self.pass = mw.uri.decode(pass, "QUERY")
         end
      end
      -- next is host
      local host
      ofs = string.find(s, "/")
      if ofs then
         host = string.sub(s, 1, ofs - 1)
         s = string.sub(s, ofs)  -- initial / is part of path
         self.host = mw.uri.decode(host, "QUERY")
      else
         -- there is no path, but there could be fragment or query string
         ofs = string.find(s, "#")
         if ofs then
            host = string.sub(s, 1, ofs - 1)
            s = string.sub(s, ofs - 1)
            self.host = mw.uri.decode(host, "QUERY")
         else
            ofs = string.find(s, "?")
            if ofs then
               host = string.sub(s, 1, ofs - 1)
               s = string.sub(s, ofs - 1)
               self.host = mw.uri.decode(host, "QUERY")
            else
               self.host = mw.uri.decode(host, s)
               s = ""
            end
         end
      end
   end
   -- whatever remains is path, fragment and/or query string
   local qs = ""
   ofs = string.find(s, "?")
   if ofs then
      -- have query string
      local path = string.sub(s, 1, ofs - 1)
      s = string.sub(s, ofs + 1)
      self.path = mw.uri.decode(path, "PATH")
      ofs = string.find(s, "#")
      if ofs then
         -- have both query string and fragment
         qs = string.sub(s, ofs - 1)
         s = string.sub(s, ofs + 1)
      else
         -- no fragment after query string
         qs = s
         s = ""
      end
   else
      -- no query string
      ofs = string.find(s, "#")
      if ofs then
         -- have fragment
         local path = string.sub(s, 1, ofs - 1)
         self.path = mw.uri.decode(path, "PATH")
         s = string.sub(s, ofs + 1)
      else
         -- no fragment
         self.path = mw.uri.decode(s, "PATH")
         s = ""
      end
   end

   -- parse any trailing fragment
   if s ~= "" then
      if string.sub(s, 1, 1) ~= "#" then
         print("Uri:parse unexpected stuff at end:", s)
         s = ""
      else
         local frag = string.sub(s, 2)
         self.fragment = mw.uri.decode(frag, "PATH")
      end
   end

   -- parse query string into a table
   self.query = {}
   if qs ~= "" then
      for x in string.gmatch(qs, "([^&]*)") do
         ofs = string.find(x, "=")
         if ofs then
            k = string.sub(x, 1, ofs - 1)
            v = string.sub(x, 1, ofs + 1)
         else
            k = x
            v = ""
         end
         self.query[k] = v
      end
   end

   -- Compute completeUrl and its components
   self:update()
end

function Uri:clone()
   return mw.clone(self)
end

function Uri:extend(query)
   if query == nil then return end
   for k, v in pairs(query) do
      if type(v) ~= "function" then
         self.query[k] = v
      end
   end
   self:update()
end

local mw_uri = {
   encode = scribunto_mwuri.encode,
   decode = scribunto_mwuri.decode,
   validate = scribunto_mwuri.validate
}

function mw_uri.anchorEncode(s)
   -- XXX how exactly should this work?
   s = s:gsub(" ", "_")
   return s
end

function mw_uri.localUrl(page, query)
   local fragment = page:gmatch("#(.*)$", "")() or ""
   page = page:gsub("#.*$", "")
   local uri = Uri:new{}
   uri:extend({title=page})
   uri:extend(query)
   local ret = uri.relativePath
   if fragment ~= "" then ret = ret .. "#" .. fragment end
   return ret
end

function mw_uri.fullUrl(page, query)
   local fragment = page:gmatch("#(.*)$", "")() or ""
   page = page:gsub("#.*$", "")
   local uri = Uri:new{}
   uri:extend({title=page})
   uri:extend(query)
   local ret = "//" .. uri.hostPort .. uri.relativePath
   if fragment ~= "" then ret = ret .. "#" .. fragment end
   return ret
end

function mw_uri.canonicalUrl(page, query)
   local fragment = page:gmatch("#(.*)$", "")() or ""
   page = page:gsub("#.*$", "")
   local uri = Uri:new{}
   uri:parse("/wiki/" .. mw.uri.encode(page, "WIKI"))
   uri:extend(query)
   local ret = uri.completeUrl
   if fragment ~= "" then ret = ret .. "#" .. fragment end
   return ret
end

function mw_uri.new(s)
   local url = Uri:new{}
   if type(s) == "string" then
      url:parse(s)
   elseif type(s) == "table" then
      url.protocol = s.protocol
      url.user = s.user
      url.password = s.password
      url.host = s.host
      url.port = s.port
      url.path = s.path
      url.query = mw.clone(s.query)
      url.fragment = s.fragment
   end
end

function mw_uri.buildQueryString(args)
   local parts = {}
   for k, v in pairs(args) do
      if type(v) ~= "function" then
         local x = k .. "=" .. mw.uri.encode(tostring(v), "QUERY")
         table.insert(parts, x)
      end
   end
   table.sort(parts)
   return table.concat(parts, "&")
end

function mw_uri.parseQueryString(s, i, j)
   if i == nil then i = 1 end
   if i < 0 then i = #s + i end
   if j == nil then j = #s - i + 1 end
   s = "&" .. string.sub(s, i, j) .. "&"
   args = {}
   for k in string.gmatch(s, "&([^&]+)") do
      local ofs = string.find(k, "=")
      if ofs == nil then
         v = false
      else
         v = string.sub(k, ofs + 1)
         k = string.sub(k, 1, ofs - 1)
         v = mw.uri.decode(v)
      end
      if args[k] ~= nil then
         local lst = args[k]
         if type(lst) ~= "table" then lst = {lst} end
         table.insert(lst, v)
         args[k] = lst
      else
         args[k] = v
      end
   end
   return args
end

return mw_uri
