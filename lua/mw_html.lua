-- Implementation of mw.html for running WikiMedia Scribunto code under
-- Python.
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

mw_html = {
}

local Html = {
   -- node
   -- wikitext
   -- newline
   -- tag
   -- attr
   -- getAttr
   -- addClass
   -- css
   -- cssText
   -- done
   -- allDone
}

function mw_html.create(tagName, args)
   local selfClosing = args and args.selfClosing
   if tagName == "hr" or tagName == "br" then selfClosing = true end
   local obj = Html:new()
   obj._parent = nil
   obj._tagName = tagName -- can be nil
   obj._attrs = {}
   obj._css = {}
   obj._children = {}
   obj._selfClosing = selfClosing
   return obj
end

function Html:new(obj)
   obj = obj or {}
   setmetatable(obj, self)
   self.__index = self
   return obj
end

function Html:_push_css()
   local parts = {}
   for k, v in pairs(self._css) do
      if type(v) ~= "function" then
         table.insert(parts, "" .. k .. ":" .. v .. ";")
      end
   end
   if #parts == 0 then return "" end
   table.sort(parts)
   local css = table.concat(parts, "")
   self._css = {}
   self:cssText(css)
end

function Html:_attrs_to_string()
   self:_push_css()
   local parts = {}
   for k, v in pairs(self._attrs) do
      if type(v) ~= "function" then
         local encoded = mw.text.encode(v)
         table.insert(parts, " " .. k .. '="' .. encoded .. '"')
      end
   end
   if #parts == 0 then return "" end
   table.sort(parts)
   return table.concat(parts, "")
end

function Html:_start()
   if self._tagName == nil then return "" end
   local parts = {"<", self._tagName, self:_attrs_to_string()}
   if self._selfClosing then table.insert(parts, " /") end
   table.insert(parts, ">")
   return table.concat(parts, "")
end

function Html:_end()
   if self._tagName == nil then return "" end
   if self._selfClosing then return "" end
   return "</" .. self._tagName .. ">"
end

function Html:__tostring()
   local parts = {}
   local start_tag = self:_start()
   if start_tag then table.insert(parts, start_tag) end
   for k, v in ipairs(self._children) do
      table.insert(parts, tostring(v))
   end
   local end_tag = self:_end()
   if end_tag then table.insert(parts, end_tag) end
   return table.concat(parts, "")
end

function Html:node(builder)
   if builder then
      table.insert(self._children, builder)
   end
end

function Html:wikitext1(v)
   if v == nil then return end
   -- I am not quite sure how this should work.  This now just inserts the text
   -- into the node, assuming that wikitext processing will be done later on
   -- the text returned by Lua.  Is this the normal case, or should we call
   -- Python here to expand the wikitext to HTML here?
   table.insert(self._children, v)
end

function Html:wikitext(...)
   for k, v in ipairs({...}) do
      self:wikitext1(v)
   end
end

function Html:newline()
   table.insert(self._children, "\n")
end

function Html:tag(tagName, args)
   local child = mw_html.create(tagName, args)
   child._parent = self
   table.insert(self._children, child)
   return child
end

function Html:attr(name, value)
   if type(name) == "table" then
      for k, v in pairs(name) do
         if type(v) ~= "function" then
            self:attr(k, v)
         end
      end
   end
   self._attrs[name] = value
end

function Html:getAttr(name)
   return self._attrs[name]
end

function Html:addClass(new_class)
   if new_class == nil then return end
   local classes = self:getAttr("class") or ""
   local new_classes = {}
   for cl in string.gmatch(classes, "([^%s]+)") do
      if cl == new_class then return end
   end
   if classes == "" then
      classes = new_class
   else
      classes = classes .. " " .. new_class
   end
   self:attr("class", classes)
end

function Html:css(name, value)
   if type(name) == "table" then
      for k, v in pairs(name) do
         if type(v) ~= "function" then
            self:css(k, v)
         end
      end
      return
   end

   self._css[name] = value
end

function Html:cssText(new_css)
   if new_css == nil or new_css == "" then return end
   if string.sub(new_css, -1) ~= ";" then new_css = new_css .. ";" end
      local css = self:getAttr("style") or ""
   if css == "" then
      css = new_css
   else
      css = css .. new_css
   end
   self:attr("style", css)
end

function Html:done()
   if self._parent then return self._parent end
   return self
end

function Html:allDone()
   local node = self
   while node._parent do node = node._parent end
   return node
end

return mw_html
