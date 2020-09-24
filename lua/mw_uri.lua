-- Simplified implementation of mw.uri for running WikiMedia Scribunto code
-- under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local scribunto_mwuri = require("mw.uri")

local DEFAULT_HOST = "dummy.host"

local Uri = {
   protocol = "https",
   -- user
   -- password
   host = DEFAULT_HOST,
   port = 80,
   path = "/",
   query = {},
   fragment = ""
   -- userInfo
   -- hostPort
   -- authority
   -- queryString
   -- relativePath
   -- fullUrl (internal)
}

function Uri:new(obj)
   obj = obj or {}
   setmetatable(obj, self)
   self.__index = self
   return obj
end

function Uri:__tostring()
   return self.fullUrl
end

function Uri:update()
   -- internal function for updating userInfo, hostPoret, authority,
   -- queryString, relativePath, fullUrl after computing rest
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
   local relpath = mw.uri.encode(self.path, "PATH")
   if #self.query > 0 then
      local qs = ""
      local first = true
      for k, v in pairs(self.query) do
         local p = enc(tostring(k)) .. "=" .. enc(tostring(v))
         if first then
            qs = qs .. p
            first = false
         else
            qs = qs .. "&" .. p
         end
      end
      self.queryString = qs
      relpath = relpath .. "?" .. qs
   else
      self.queryString = ""
   end
   if self.fragment then
      relpath = relpath .. "#" .. enc(self.fragment)
   end
   self.relativePath = relpath
   url = url .. relpath
   self.fullUrl = url
end

function Uri:parse(s)
   local ofs
   if string.match(s, "[a-z0-9]+:") then
      ofs = string.find(s, ":")
      self.protocol = string.sub(s, 1, ofs - 1)
      s = string.sub(s, ofs + 1)
   else
      self.protocol = "http"
   end
   if string.sub(s, 1, 2) == "//" then
      s = string.sub(s, 3)
   end
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
      else
         self.user = nil
         self.password = nil
      end
   end
   -- next is mandatory host
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
   -- whatever remains is fragment and/or query string
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

   -- Compute fullUrl and its components
   self:update()
end

function Uri:clone()
   return mw.clone(self)
end

function Uri:extend(parameters)
   for k, v in pairs(parameters) do
      self.query[k] = v
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
   return mw.uri.canonicalUrl(page, query)
end

function mw_uri.fullUrl(page, query)
   return mw.uri.canonicalUrl(page, query)
end

function mw_uri.canonicalUrl(page, query)
   local uri = Uri:new{}
   uri:parse(page)
   uri:extend(query)
   -- might want to set protocol, host
   return uri
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
