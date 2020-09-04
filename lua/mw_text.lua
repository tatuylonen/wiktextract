-- Simplified implementation of mw.text for running WikiMedia Scribunto code
-- under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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

-- XXX this function was copied, from where and what license?
function mw_text.trim(val)
   return (val:gsub("^%s*(.-)%s*$", "%1"))
end

-- XXX this function was copied, from where and what license?
function mw_text.split(text, pattern, plain)
  local ret = {}
  for m in mw_text.gsplit(text, pattern, plain) do
    ret[#ret + 1] = m
  end
  return ret
end

-- XXX this function was copied, from where and what license?
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

return mw_text
