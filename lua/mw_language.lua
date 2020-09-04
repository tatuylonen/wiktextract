-- Simplified implementation of mw.language for running WikiMedia Scribunto
-- code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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

default_lang = Language:new{}

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

function mw_language.getContentLanguage()
   return default_lang
end

return mw_language
