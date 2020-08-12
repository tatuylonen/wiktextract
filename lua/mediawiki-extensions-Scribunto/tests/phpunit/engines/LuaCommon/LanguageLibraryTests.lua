local testframework = require 'Module:TestFramework'

local langs = nil
local function getLangs()
	if langs == nil then
		langs = {
			mw.language.new( 'en' ),
			mw.language.new( 'kaa' ),
			mw.language.new( 'fa' ),
			mw.language.new( '[[bogus]]' ),
		}
	end
	return langs
end

local function test_method( func, ... )
	local langs = getLangs()

	local ret = {}
	for i = 1, #langs do
		local got = { pcall( langs[i][func], langs[i], ... ) }
		if table.remove( got, 1 ) then
			ret[i] = got
		else
			ret[i] = string.gsub( got[1], '^%S+:%d+: ', '' )
		end
	end
	return unpack( ret )
end

local function test_method_lang( lang, func, ... )
	local obj = mw.language.new( lang )
	return obj[func]( obj, ... )
end

local function test_plural( lang )
	local obj = mw.language.new( lang )
	local ret1, ret2 = '', ''
	local ret3, ret4 = '', ''
	for i = 0, 29 do
		ret1 = ret1 .. obj:convertPlural( i, 'a', 'b', 'c', 'd', 'e' )
		ret2 = ret2 .. obj:convertPlural( i, { 'a', 'b', 'c', 'd', 'e' } )
		ret3 = ret3 .. obj:plural( i, 'a', 'b', 'c', 'd', 'e' )
		ret4 = ret4 .. obj:plural( i, { 'a', 'b', 'c', 'd', 'e' } )
	end
	if ret1 ~= ret2 or ret1 ~= ret3 or ret1 ~= ret4 then
		error( "Plural tests don't match:" ..
			" " .. ret1
			" " .. ret2
			" " .. ret3
			" " .. ret4
		)
	end
	return ret1
end

local function test_multi( func, ... )
	local ret = {}
	for i = 1, select( '#', ... ) do
		ret[i] = func( select( i, ... ) )
	end
	return unpack( ret, 1, select( '#', ... ) )
end

local function test_fetchLanguageNames( ... )
	local ret = mw.language.fetchLanguageNames( ... )
	if type( ret ) == 'table' then
		return {
			en = ret.en,
			ru = ret.ru,
		}
	else
		return ret
	end
end

local function test_parseFormattedNumber()
	local langs = getLangs()

	local ret = {}
	for i = 1, #langs do
		local ok, num = pcall( langs[i].formatNum, langs[i], 123456.78901 )
		local got = { pcall( langs[i].parseFormattedNumber, langs[i], num ) }
		if table.remove( got, 1 ) then
			ret[i] = got
		else
			ret[i] = string.gsub( got[1], '^%S+:%d+: ', '' )
		end
	end
	return unpack( ret )
end

return testframework.getTestProvider( {
	{ name = 'fetchLanguageName (en)', func = mw.language.fetchLanguageName,
	  args = { 'en' },
	  expect = { 'English' }
	},
	{ name = 'fetchLanguageName (ru)', func = mw.language.fetchLanguageName,
	  args = { 'ru' },
	  expect = { 'русский' }
	},
	{ name = 'fetchLanguageName (en,ru)', func = mw.language.fetchLanguageName,
	  args = { 'en', 'ru' },
	  expect = { 'английский' }
	},
	{ name = 'fetchLanguageName (ru,en)', func = mw.language.fetchLanguageName,
	  args = { 'ru', 'en' },
	  expect = { 'Russian' }
	},
	{ name = 'fetchLanguageName ([[bogus]])', func = mw.language.fetchLanguageName,
	  args = { '[[bogus]]' },
	  expect = { '' }
	},
	{ name = 'fetchLanguageName (en,[[bogus]])', func = mw.language.fetchLanguageName,
	  args = { 'en', '[[bogus]]' },
	  expect = { 'English' }
	},

	{ name = 'fetchLanguageNames ()', func = test_fetchLanguageNames,
	  args = {},
	  expect = { { en = 'English', ru = 'русский' } }
	},
	{ name = 'fetchLanguageNames (de)', func = test_fetchLanguageNames,
	  args = { 'de' },
	  expect = { { en = 'Englisch', ru = 'Russisch' } }
	},
	{ name = 'fetchLanguageNames ([[bogus]])', func = test_fetchLanguageNames,
	  args = { '[[bogus]]' },
	  expect = { { en = 'English', ru = 'Russian' } }
	},

	{ name = 'getFallbacksFor', func = test_multi,
	  args = { mw.language.getFallbacksFor, 'en', 'de', 'arz', '[[bogus]]' },
	  expect = { {}, { 'en' }, { 'ar', 'en' }, {} }
	},

	{ name = 'isKnownLanguageTag', func = test_multi,
	  args = { mw.language.isKnownLanguageTag, 'en', 'not-a-real-code', 'extension code', '[[bogus]]' },
	  expect = { true, false, false, false }
	},

	{ name = 'isSupportedLanguage', func = test_multi,
	  args = { mw.language.isSupportedLanguage, 'en', 'not-a-real-code', 'extension code', '[[bogus]]' },
	  expect = { true, false, false, false }
	},

	{ name = 'isValidBuiltInCode', func = test_multi,
	  args = { mw.language.isValidBuiltInCode, 'en', 'not-a-real-code', 'extension code', '[[bogus]]' },
	  expect = { true, true, false, false }
	},

	{ name = 'isValidCode', func = test_multi,
	  args = { mw.language.isValidCode, 'en', 'not-a-real-code', 'extension code', '[[bogus]]' },
	  expect = { true, true, true, false }
	},

	{ name = 'mw.language.new', func = test_multi, type = 'ToString',
	  args = { mw.language.new, 'en', 'ru', '[[bogus]]' },
	  expect = { 'table', 'table', 'table' }
	},

	{ name = 'lang:getCode', func = test_method,
	  args = { 'getCode' },
	  expect = {
		  { 'en' },
		  { 'kaa' },
		  { 'fa' },
		  { '[[bogus]]' },
	  }
	},

	{ name = 'lang:getFallbackLanguages', func = test_method,
	  args = { 'getFallbackLanguages' },
	  expect = {
		  { {} },
		  { { 'kk-latn', 'kk-cyrl', 'en' } },
		  { { 'en' } },
		  { {} },
	  }
	},

	{ name = 'lang:isRTL', func = test_method,
	  args = { 'isRTL' },
	  expect = {
		  { false },
		  { false },
		  { true },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:lc', func = test_method,
	  args = { 'lc', 'IX' },
	  expect = {
		  { 'ix' },
		  { 'ix' }, -- Probably not actually right, but it's what LanguageKaa returns
		  { 'ix' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:lcfirst', func = test_method,
	  args = { 'lcfirst', 'IX' },
	  expect = {
		  { 'iX' },
		  { 'ıX' },
		  { 'iX' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:uc', func = test_method,
	  args = { 'uc', 'ix' },
	  expect = {
		  { 'IX' },
		  { 'IX' }, -- Probably not actually right, but it's what LanguageKaa returns
		  { 'IX' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:ucfirst', func = test_method,
	  args = { 'ucfirst', 'ix' },
	  expect = {
		  { 'Ix' },
		  { 'İx' },
		  { 'Ix' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:caseFold', func = test_method,
	  args = { 'caseFold', 'ix' },
	  expect = {
		  { 'IX' },
		  { 'IX' }, -- Probably not actually right, but it's what LanguageKaa returns
		  { 'IX' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:formatNum', func = test_method,
	  args = { 'formatNum', 123456.78901 },
	  expect = {
		  { '123,456.78901' },
		  { "123\194\160456,78901" },
		  { '۱۲۳٬۴۵۶٫۷۸۹۰۱' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:formatDate', func = test_method,
	  args = { 'formatDate', 'Y-F-d H:i:s', '20140305123456' },
	  expect = {
		  { '2014-March-05 12:34:56' },
		  { '2014-Mart-05 12:34:56' },
		  { '۲۰۱۴-مارس-۰۵ ۱۲:۳۴:۵۶' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:formatDuration', func = test_method,
	  args = { 'formatDuration', 86461 },
	  expect = {
		  { "1 day, 1 minute and 1 second" },
		  { "1 күн, 1 минут ha&#039;m 1 секунд" },
		  { "۱ روز، ۱ دقیقه و ۱ ثانیه" },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:formatDuration (hours and minutes)', func = test_method,
	  args = { 'formatDuration', 86461, { 'hours', 'minutes' } },
	  expect = {
		  { "24 hours and 1 minute" },
		  { "24 сағат ha&#039;m 1 минут" },
		  { "۲۴ ساعت و ۱ دقیقه" },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:parseFormattedNumber', func = test_parseFormattedNumber,
	  args = {},
	  expect = {
		  { 123456.78901 },
		  { 123456.78901 },
		  { 123456.78901 },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:convertPlural (en)', func = test_plural,
	  args = { 'en' },
	  expect = { 'babbbbbbbbbbbbbbbbbbbbbbbbbbbb' }
	},
	{ name = 'lang:convertPlural (pl)', func = test_plural,
	  args = { 'pl' },
	  expect = { 'cabbbcccccccccccccccccbbbccccc' }
	},
	{ name = 'lang:convertPlural (bogus)', func = test_plural,
	  args = { '[[bogus]]' },
	  expect = "language code '[[bogus]]' is invalid",
	},

	{ name = 'lang:convertGrammar (ru)', func = test_method_lang,
	  args = { 'ru', 'convertGrammar', '**ия', 'genitive' },
	  expect = { '**ии' }
	},
	{ name = 'lang:convertGrammar (bogus)', func = test_method_lang,
	  args = { '[[bogus]]', 'convertGrammar', '**ия', 'genitive' },
	  expect = "language code '[[bogus]]' is invalid",
	},

	{ name = 'lang:grammar (ru)', func = test_method_lang,
	  args = { 'ru', 'grammar', 'genitive', '**ия' },
	  expect = { '**ии' }
	},
	{ name = 'lang:grammar (bogus)', func = test_method_lang,
	  args = { '[[bogus]]', 'grammar', 'genitive', '**ия' },
	  expect = "language code '[[bogus]]' is invalid",
	},

	{ name = 'lang:gender (male)', func = test_method,
	  args = { 'gender', 'male', 'masculine', 'feminine', 'neutral' },
	  expect = {
		  { 'masculine' },
		  { 'masculine' },
		  { 'masculine' },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:gender (female)', func = test_method,
	  args = { 'gender', 'female', 'masculine', 'feminine', 'neutral' },
	  expect = {
		  { 'feminine' },
		  { 'feminine' },
		  { 'feminine' },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:gender (male, with sequence)', func = test_method,
	  args = { 'gender', 'male', { 'masculine', 'feminine', 'neutral' } },
	  expect = {
		  { 'masculine' },
		  { 'masculine' },
		  { 'masculine' },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:getArrow (forward)', func = test_method,
	  args = { 'getArrow', 'forwards' },
	  expect = {
		  { "→" },
		  { "→" },
		  { "←" },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:getArrow (right)', func = test_method,
	  args = { 'getArrow', 'right' },
	  expect = {
		  { "→" },
		  { "→" },
		  { "→" },
		  { "→" },
	  }
	},

	{ name = 'lang:getDir', func = test_method,
	  args = { 'getDir' },
	  expect = {
		  { "ltr" },
		  { "ltr" },
		  { "rtl" },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:getDirMark', func = test_method,
	  args = { 'getDirMark' },
	  expect = {
		  { "\226\128\142" },
		  { "\226\128\142" },
		  { "\226\128\143" },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:getDirMark opposite', func = test_method,
	  args = { 'getDirMark', true },
	  expect = {
		  { "\226\128\143" },
		  { "\226\128\143" },
		  { "\226\128\142" },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:getDirMarkEntity', func = test_method,
	  args = { 'getDirMarkEntity' },
	  expect = {
		  { "&lrm;" },
		  { "&lrm;" },
		  { "&rlm;" },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:getDirMarkEntity opposite', func = test_method,
	  args = { 'getDirMarkEntity', true },
	  expect = {
		  { "&rlm;" },
		  { "&rlm;" },
		  { "&lrm;" },
		  "language code '[[bogus]]' is invalid",
	  }
	},

	{ name = 'lang:getDurationIntervals', func = test_method,
	  args = { 'getDurationIntervals', 86461 },
	  expect = {
		  { { days = 1, minutes = 1, seconds = 1 } },
		  { { days = 1, minutes = 1, seconds = 1 } },
		  { { days = 1, minutes = 1, seconds = 1 } },
		  "language code '[[bogus]]' is invalid",
	  }
	},
	{ name = 'lang:getDurationIntervals (hours and minutes)', func = test_method,
	  args = { 'getDurationIntervals', 86461, { 'hours', 'minutes' } },
	  expect = {
		  { { hours = 24, minutes = 1 } },
		  { { hours = 24, minutes = 1 } },
		  { { hours = 24, minutes = 1 } },
		  "language code '[[bogus]]' is invalid",
	  }
	},
} )
