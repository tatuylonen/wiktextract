local language = {}
local php
local util = require 'libraryUtil'

function language.setupInterface()
	-- Boilerplate
	language.setupInterface = nil
	php = mw_interface
	mw_interface = nil

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.language = language
	mw.getContentLanguage = language.getContentLanguage
	mw.getLanguage = mw.language.new

	local lang = mw.getContentLanguage();

	-- Extend ustring
	if mw.ustring then
		mw.ustring.upper = function ( s )
			return lang:uc( s )
		end
		mw.ustring.lower = function ( s )
			return lang:lc( s )
		end
		string.uupper = mw.ustring.upper
		string.ulower = mw.ustring.lower
	end

	package.loaded['mw.language'] = language
end

function language.isSupportedLanguage( code )
	return php.isSupportedLanguage( code )
end

function language.isKnownLanguageTag( code )
	return php.isKnownLanguageTag( code )
end

function language.isValidCode( code )
	return php.isValidCode( code )
end

function language.isValidBuiltInCode( code )
	return php.isValidBuiltInCode( code )
end

function language.fetchLanguageName( code, inLanguage )
	return php.fetchLanguageName( code, inLanguage )
end

function language.fetchLanguageNames( inLanguage, include )
	return php.fetchLanguageNames( inLanguage, include )
end

function language.getFallbacksFor( code )
	return php.getFallbacksFor( code )
end

function language.new( code )
	if code == nil then
		error( "too few arguments to mw.language.new()", 2 )
	end

	local lang = { code = code }

	local checkSelf = util.makeCheckSelfFunction( 'mw.language', 'lang', lang, 'language object' )

	local wrappers = {
		lcfirst = 1,
		ucfirst = 1,
		lc = 1,
		uc = 1,
		caseFold = 1,
		formatNum = 1,
		formatDate = 1,
		formatDuration = 1,
		getDurationIntervals = 1,
		convertPlural = 2,
		convertGrammar = 2,
		gender = 2,
	}

	for name, numArgs in pairs( wrappers ) do
		lang[name] = function ( self, ... )
			checkSelf( self, name )
			if select( '#', ... ) < numArgs then
				error( "too few arguments to mw.language:" .. name, 2 )
			end
			return php[name]( self.code, ... )
		end
	end

	-- This one could use caching
	function lang:isRTL()
		checkSelf( self, 'isRTL' )
		local rtl = php.isRTL( self.code )
		self.isRTL = function ()
			return rtl
		end
		return rtl
	end

	-- Fix semantics
	function lang:parseFormattedNumber( ... )
		checkSelf( self, 'parseFormattedNumber' )
		if select( '#', ... ) < 1 then
			error( "too few arguments to mw.language:parseFormattedNumber", 2 )
		end
		return tonumber( php.parseFormattedNumber( self.code, ... ) )
	end

	-- Alias
	lang.plural = lang.convertPlural

	-- Parser function compat
	function lang:grammar( case, word )
		checkSelf( self, name )
		return self:convertGrammar( word, case )
	end

	-- Other functions
	function lang:getCode()
		checkSelf( self, 'getCode' )
		return self.code
	end

	function lang:getDir()
		checkSelf( self, 'getDir' )
		return self:isRTL() and 'rtl' or 'ltr'
	end

	function lang:getDirMark( opposite )
		checkSelf( self, 'getDirMark' )
		local b = self:isRTL()
		if opposite then
			b = not b
		end
		return b and '\226\128\143' or '\226\128\142'
	end

	function lang:getDirMarkEntity( opposite )
		checkSelf( self, 'getDirMarkEntity' )
		local b = self:isRTL()
		if opposite then
			b = not b
		end
		return b and '&rlm;' or '&lrm;'
	end

	function lang:getArrow( direction )
		checkSelf( self, 'getArrow' )
		direction = direction or 'forwards'
		util.checkType( 'getArrow', 1, direction, 'string' )
		if direction == 'forwards' then
			return self:isRTL() and '←' or '→'
		elseif direction == 'backwards' then
			return self:isRTL() and '→' or '←'
		elseif direction == 'left' then
			return '←'
		elseif direction == 'right' then
			return '→'
		elseif direction == 'up' then
			return '↑'
		elseif direction == 'down' then
			return '↓'
		end
	end

	function lang:getFallbackLanguages()
		checkSelf( self, 'getFallbackLanguages' )
		return language.getFallbacksFor( self.code )
	end

	return lang
end

local contLangCode

function language.getContentLanguage()
	if contLangCode == nil then
		contLangCode = php.getContLangCode()
	end
	return language.new( contLangCode )
end

return language
