-- Simplified implementation of mw.text for running WikiMedia Scribunto code
-- under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

-- Use the original WikiMedia Scribunto code for some things
scribunto_mwtext = require("mw.text")

local mw_text = {
   -- decode (set from Python)
   -- encode (set from Python)
   -- jsonDecode
   -- jsonEncode
   -- killMarkers
   -- listToText
   -- nowiki  (see below)
   split = scribunto_mwtext.split,
   gsplit = scribunto_mwtext.gsplit,
   -- tag
   trim = scribunto_mwtext.trim
   -- truncate
   -- unstripNoWiki
   -- unstrip
}

function mw_text.nowiki(s)
   s = s:gsub("&", "&amp;")
   s = s:gsub('"', "&quot;")
   s = s:gsub("'", "&apos;")
   s = s:gsub("<", "&lt;")
   s = s:gsub(">", "&gt;")
   s = s:gsub("=", "&#61;")
   s = s:gsub("%[", "&lsqb;")
   s = s:gsub("%]", "&rsqb;")
   s = s:gsub("{", "&lbrace;")
   s = s:gsub("}", "&rbrace;")
   s = s:gsub("|", "&vert;")
   s = s:gsub("^#", "&num;")
   s = s:gsub("\n#", "\n&num;")
   s = s:gsub("^:", "&colon;")
   s = s:gsub("\n:", "\n&colon;")
   s = s:gsub("^;", "&semi;")
   s = s:gsub("\n;", "\n&semi;")
   s = s:gsub("^ ", "&nbsp;")
   s = s:gsub("\n ", "\n&nbsp;")
   s = s:gsub("^\t", "&Tab;")
   s = s:gsub("\n\t", "\n&Tab;")
   s = s:gsub("\n\n", "\n&NewLine;")
   s = s:gsub("^%-%-%-%-", "&minus;---")
   s = s:gsub("\n%-%-%-%-", "\n&minus;---")
   s = s:gsub("^__", "&#95;_")
   s = s:gsub("\n__", "\n&#95;_")
   s = s:gsub("://", "&colon;//")
   s = s:gsub("ISBN ", "ISBN&nbsp;")
   s = s:gsub("ISBN\t", "ISBN&Tab;")
   s = s:gsub("ISBN\n", "ISBN&NewLine;")
   s = s:gsub("RFC ", "ISBN&nbsp;")
   s = s:gsub("RFC\t", "ISBN&Tab;")
   s = s:gsub("RFC\n", "ISBN&NewLine;")
   s = s:gsub("PMID ", "ISBN&nbsp;")
   s = s:gsub("PMID\t", "ISBN&Tab;")
   s = s:gsub("PMID\n", "ISBN&NewLine;")
   return s
end

return mw_text
