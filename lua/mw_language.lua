-- Simplified implementation of mw.language for running WikiMedia Scribunto
-- code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local ustring = require("ustring:ustring")

-- The fallback data is based on
-- https://upload.wikimedia.org/wikipedia/commons/2/26/MediaWiki_fallback_chains.svg
local fallbacks = {
   qug = {"es", "qu"},
   qu = {"qug", "es"},
   gn = {"es"},
   ast = {"es"},
   ext = {"es"},
   arn = {"es"},
   lad = {"es"},
   ["cbk-zam"] = {"es"},
   nah = {"es"},
   ["es-formal"] = {"es"},
   an = {"es"},
   ay = {"es"},
   -- XXX ru fallbacks
   -- XXX fr fallbacks
   -- XXX de fallbacks
   -- XXX id fallbacks
   -- XXX ur fallbacks
   -- XXX fa fallbacks
   -- XXX zh-hans fallbacks
   -- XXX en fallbacks
   -- XXX pl fallbacks
   -- XXX da fallbacks
   -- XXX fi fallbacks
   -- XXX tr fallbacks
   -- XXX et fallbacks
   -- XXX nl fallbacks
   -- XXX ro fallbacks
   -- XXX hi fallbacks
   -- XXX it fallbacks
   -- XXX hr fallbacks
   -- XXX kk-cyrl fallbacks
   -- XXX pt fallbacks
   kjp = {"my"},
   mnw = {"my"},
   sgs = {"lt"},
   tcy = {"kn"},
   xmf = {"ka"},
   cs = {"sk"},
   sk = {"cs"},
   io = {"eo"},
   nn = {"nb"},
   nb = {"nn"},
   yi = {"he"},
   ["ko-kp"] = {"ko"},
   sr = {"sr-ec"},
   ["be-tarask"] = {"be"},
   ["hu-formal"] = {"hu"},
   ady = {"ady-cyrl"},
   crh = {"crh-latn"},
   hif = {"hif-latn"},
   iu = {"ike-cans"},
   kbd = {"kbd-cyrl"},
   ["ruq-cyrl"] = {"mk"},
   ks = {"ks-arab"},
   ku = {"ku-latn"},
   ["ku-arab"] = {"ckb"},
   tg = {"tg-cyrl"},
   ug = {"ug-arab"},
   aln = {"sq"},
   bh = {"bho"},
   bpy = {"bn"},
   dtp = {"ms"},
   dty = {"ne"},
   hyw = {"hy"},
   ltg = {"lv"},
   pnt = {"el"},
}



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

function Language:new(o)
   obj = obj or {}
   setmetatable(obj, self)
   self.__index = self
   return obj
end

function Language:getCode()
   return self.code
end

function Language:getFallbackLanguages()
   return fallbacks[lang] or {}
end

function Language:isRTL()
   -- XXX actually determine this somehow
   return false
end

function Language:lc(s)
   -- XXX language-specific variants
   return ustring.lower(s)
end

function Language:lcfirst(s)
   return self:lc(ustring.sub(s, 1, 1)) .. ustring.sub(s, 2)
end


function Language:uc(s)
   -- XXX language-specific variants
   return ustring.upper(s)
end

function Language:ucfirst(s)
   return self:uc(ustring.sub(s, 1, 1)) .. ustring.sub(s, 2)
end

function Language:caseFold(s)
   return self:lc(s)
end

function Language:formatNum(n, options)
   local noCommafy = options and options.noCommafy
   -- implement language-specific conventions
   return tostring(n)
end

function Language:formatDate(format, timestamp, localtime)
   -- XXX currently ignores localtime
   if not timestamp then
      timestamp = os.date("%Y-%m-%d %X")
   end
   -- XXX actually format the time.  See
   -- https://www.mediawiki.org/wiki/Help:Extension:ParserFunctions#.23time
   -- form supported timestamp formats and format specification.
   return timestamp
end

function Language:formatDuration(seconds, allowedIntervals)
   -- XXX actually implement language-specific formatting
   if seconds == 1 then
      return "1 second"
   end
   return tostring(seconds) .. " seconds"
end

function Language:parseFormattedNumber(s)
   -- XXX make this language-specific
   s = ustring.gsub(s, ",", "")
   return tonumber(s)
end

function Language:convertPlural(n, forms)
   -- XXX ... form
   print("XXX Language.convertPlural not yet implemented")
   assert(false)
end

function Language:plural(n, forms)
   -- XXX ... form
   return self:convertPlural(n, forms)
end

function Language:convertGrammar(word, case)
   print("XXX Language.convertGrammar not yet implemented")
   assert(false)
end

function Language:grammar(case, word)
   return self:convertGrammar(word, case)
end

function Language:gender(what, masculine, feminine, neutral)
   if type(masculine) == "table" then
      feminine = masculine[1]
      neutral = masculine[2]
      masculine = masculine[0]
   end
   -- XXX if what is a registered user name, determine its gender
   if what == "feminine" then return feminine end
   if what == "neutral" then return neutral end
   return masculine
end

function Language:getArrow(direction)
   -- XXX implement language-specific
   if direction == "forwards" then return "\u{2192}" end
   if direction == "backwards" then return "\u{2190}" end
   if direction == "left" then return "\u{2190}" end
   if direction == "right" then return "\u{2192}" end
   if direction == "up" then return "\u{2191}" end
   if direction == "down" then return "\u{2193}" end
   print("Language.getArrow unrecognized direction", direction)
   return "\u{2192}"
end

function Language:getDir()
   -- XXX make this language specific
   return "ltr"
end

function Language:getDirMark(opposite)
   local dir = self:getDir()
   if opposite then
      if dir == "ltr" then dir = "rtl" else dir = "ltr" end
   end
   if dir == "rtr" then return "\u{200f}" end
   return "\u{200e}"
end

function Language:getDirMarkEntity(opposite)
   local dir = self:getDir()
   if opposite then
      if dir == "ltr" then dir = "rtl" else dir = "ltr" end
   end
   if dir == "rtr" then return "&rlm;" end
   return "&lrm;"
end

local intervalBases = {
   { "millennia", 1000 * 3600 * 24 * 365 },
   { "centuries", 100 * 3600 * 24 * 365 },
   { "decades", 10 * 3600 * 24 * 365 },
   { "years", 3600 * 24 * 365 },
   { "days", 3600 * 24 },
   { "hours", 3600 },
   { "minutes", 60 }
}

function Language.getDurationIntervals(self, seconds, allowedIntervals)
   if not allowedIntervals then
      allowedIntervals = {}
      for i=1,len(intervalBases) do
         table.insert(allowedIntervals, intervalBases[i][0])
      end
   end
   ret = {}
   for i=1,len(intervalBases) do
      local name = intervalBases[i][0]
      local interval = intervalBases[i][1]
      local found = false
      for j=1,len(allowedIntervals) do
         if allowedIntervals[j] == name then
            found = true
            break
         end
      end
      if found then
         local v = math.floor(seconds / interval)
         seconds = seconds - v * interval
         ret[name] = v
      end
   end
   ret["seconds"] = seconds
   return ret
end

en_lang = Language:new{code="en"}

local mw_language = {
   -- fetchLanguageName(code, inLanguage)
   -- fetchLanguageNames(inLanguage=None, include=None)
   -- getContentLanguage()  (see below)
   -- getFallbacksFor(code)
   -- isKnownLanguageTag(code)  -- assigned in lua_set_fns
   -- isSupportedLanguage(code)
   -- isValidBuiltInCode(code)
   -- isValidCode(code)
   -- new(code)
}

function mw_language.fetchLanguageName(code, inLanguage)
   -- XXX inLanguage
   return mw.language.python_fetch_language_name(code)
end

function mw_language.fetchLanguageNames(inLanguage, include)
   include = include or "mw"
   return mw.language.python_fetch_language_names(include)
end

function mw_language.getContentLanguage()
   return en_lang
end

function mw_language.getFallbacksFor(code)
   return fallbacks[code] or {}
end

function mw_language.isKnownLanguageTag(code)
   return mw.language.fetchLanguageName(code) ~= nil
end

function mw_language.isSupportedLanguage(code)
   -- XXX
   return code == "en"
end

function mw_language.isValidBuiltInCode(code)
   if ustring.match(code, "[a-z0-9][-a-z0-9]*[a-z0-9]") then return true end
   return false
end

function mw_language.isValidCode(code)
   if len(code) < 1 then return false end
   if ustring.find(code, "[:'\"/\\<>]") then return false end
   return true
end

function mw_language.new(code)
   return Language:new{code=code}
end

function mw_language.getLanguage(code)
   return mw.language.new(code)
end

return mw_language
