local testframework = require 'Module:TestFramework'

local message1 = mw.message.new( 'mainpage' )
local message1_copy = mw.message.new( 'mainpage' )
local message2 = mw.message.new( 'i-dont-exist-evar' )

function test_exists( key )
	return mw.message.new( key ):exists()
end

function test_language( key )
	-- If mw.language is available, test that too
	local lang = 'ru'
	if mw.language then
		lang = mw.language.new( 'ru' )
	end

	return mw.message.new( 'mainpage' ):useDatabase( false ):inLanguage( 'en' ):plain(),
		mw.message.new( 'mainpage' ):useDatabase( false ):inLanguage( 'ru' ):plain(),
		mw.message.new( 'mainpage' ):useDatabase( false ):inLanguage( lang ):plain()
end

function test_params( rawMessage, func, ... )
	local msg = mw.message.newRawMessage( rawMessage ):inLanguage( 'en' )
	return msg[func]( msg, ... ):plain()
end

return testframework.getTestProvider( {
	{ name = 'exists (1)', func = test_exists,
	  args = { 'mainpage' },
	  expect = { true }
	},
	{ name = 'exists (2)', func = test_exists,
	  args = { 'i-dont-exist-evar' },
	  expect = { false }
	},

	{ name = 'inLanguage', func = test_language,
	  expect = { 'Main Page', 'Заглавная страница', 'Заглавная страница' }
	},

	{ name = 'plain param', func = test_params,
	  args = { '($1 $2)', 'params', "'''foo'''", 123456 },
	  expect = { "('''foo''' 123456)" }
	},
	{ name = 'raw param', func = test_params,
	  args = { '($1 $2)', 'rawParams', "'''foo'''", 123456 },
	  expect = { "('''foo''' 123456)" }
	},
	{ name = 'num param', func = test_params,
	  args = { '($1 $2)', 'numParams', "'''foo'''", 123456 },
	  expect = { "('''foo''' 123,456)" }
	},
	{ name = 'mixed params', func = test_params,
	  args = { '($1 $2 $3)', 'params',
		"'''foo'''", mw.message.rawParam( "'''foo'''" ), mw.message.numParam( 123456 )
	  },
	  expect = { "('''foo''' '''foo''' 123,456)" }
	},

	{ name = 'message as param', func = test_params,
	  args = { '($1)', 'params', mw.message.newRawMessage( 'bar' ) },
	  expect = { "(bar)" }
	},

	{ name = 'different title', func = test_params,
	  args = { '($1)', 'params', mw.message.newRawMessage( 'bar' ) },
	  expect = { "(bar)" }
	},
} )
