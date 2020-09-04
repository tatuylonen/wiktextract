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
   -- nowiki
   split = scribunto_mwtext.split,
   gsplit = scribunto_mwtext.gsplit,
   -- tag
   trim = scribunto_mwtext.trim
   -- truncate
   -- unstripNoWiki
   -- unstrip
}

return mw_text
