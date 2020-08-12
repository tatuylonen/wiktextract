local testframework = require 'Module:TestFramework'

local function nsTest( ... )
	local args = { ... }
	local t = mw.site.namespaces
	local path = 'mw.site.namespaces'
	for i = 1, #args do
		t = t[args[i]]
		path = path .. string.format( '[%q]', args[i] )
		if t == nil then
			error( path .. ' is nil!' )
		end
	end
	return t
end

local function isNonEmptyString( val )
	return type( val ) == 'string' and val ~= ''
end

local function isValidInterwikiMap( map )
	assert( type( map ) == 'table', "mw.site.interwikiMap did not return a table" )
	local stringKeys = { 'prefix', 'url' }
	local boolKeys = {
		'isProtocolRelative',
		'isLocal',
		'isTranscludable',
		'isCurrentWiki',
		'isExtraLanguageLink'
	}
	local maybeStringKeys = { 'displayText', 'tooltip' }
	for prefix, data in pairs( map ) do
		for _, key in ipairs( stringKeys ) do
			assert( isNonEmptyString( data[key] ),
				key .. " is not a string or is the empty string"
			)
		end
		assert( prefix == data.prefix, string.format(
			"table key '%s' and prefix '%s' do not match",
			tostring( prefix ), tostring( data.prefix )
		) )
		for _, key in ipairs( boolKeys ) do
			assert( type( data[key] ) == 'boolean', key .. " is not a boolean" )
		end
		for _, key in ipairs( maybeStringKeys ) do
			assert( data[key] == nil or isNonEmptyString( data[key] ),
				key .. " is not a string or is the empty string, and is not nil"
			)
		end
	end
	return true
end

return testframework.getTestProvider( {
	{ name = 'parameter: siteName',
	  func = type, args = { mw.site.siteName },
	  expect = { 'string' }
	},
	{ name = 'parameter: server',
	  func = type, args = { mw.site.server },
	  expect = { 'string' }
	},
	{ name = 'parameter set: scriptPath',
	  func = type, args = { mw.site.scriptPath },
	  expect = { 'string' }
	},

	{ name = 'parameter set: stats.pages',
	  func = type, args = { mw.site.stats.pages },
	  expect = { 'number' }
	},

	{ name = 'pagesInCategory',
	  func = type, args = { mw.site.stats.pagesInCategory( "Example" ) },
	  expect = { 'number' }
	},

	{ name = 'pagesInNamespace',
	  func = type, args = { mw.site.stats.pagesInNamespace( 0 ) },
	  expect = { 'number' }
	},

	{ name = 'usersInGroup',
	  func = type, args = { mw.site.stats.usersInGroup( 'sysop' ) },
	  expect = { 'number' }
	},

	{ name = 'Project namespace by number',
	  func = nsTest, args = { 4, 'canonicalName' },
	  expect = { 'Project' }
	},

	{ name = 'Project namespace by name',
	  func = nsTest, args = { 'Project', 'id' },
	  expect = { 4 }
	},

	{ name = 'Project namespace by name (2)',
	  func = nsTest, args = { 'PrOjEcT', 'canonicalName' },
	  expect = { 'Project' }
	},

	{ name = 'Project namespace subject is itself',
	  func = nsTest, args = { 'Project', 'subject', 'canonicalName' },
	  expect = { 'Project' }
	},

	{ name = 'Project talk namespace via Project',
	  func = nsTest, args = { 'Project', 'talk', 'canonicalName' },
	  expect = { 'Project talk' }
	},

	{ name = 'Project namespace via Project talk',
	  func = nsTest, args = { 'Project_talk', 'subject', 'canonicalName' },
	  expect = { 'Project' }
	},

	{ name = 'Project talk namespace via Project (associated)',
	  func = nsTest, args = { 'Project', 'associated', 'canonicalName' },
	  expect = { 'Project talk' }
	},

	{ name = 'Project talk namespace by name (standard caps, no underscores)',
	  func = nsTest, args = { 'Project talk', 'id' },
	  expect = { 5 }
	},

	{ name = 'Project talk namespace by name (standard caps, underscores)',
	  func = nsTest, args = { 'Project_talk', 'id' },
	  expect = { 5 }
	},

	{ name = 'Project talk namespace by name (odd caps, no underscores)',
	  func = nsTest, args = { 'pRoJeCt tAlK', 'id' },
	  expect = { 5 }
	},

	{ name = 'Project talk namespace by name (odd caps, underscores)',
	  func = nsTest, args = { 'pRoJeCt_tAlK', 'id' },
	  expect = { 5 }
	},

	{ name = 'Project talk namespace by name (extraneous spaces and underscores)',
	  func = nsTest, args = { '_ _ _Project_ _talk_ _ _', 'id' },
	  expect = { 5 }
	},

	{ name = 'interwikiMap (all prefixes)',
	  func = isValidInterwikiMap, args = { mw.site.interwikiMap() },
	  expect = { true }
	},

	{ name = 'interwikiMap (local prefixes)',
	  func = isValidInterwikiMap, args = { mw.site.interwikiMap( 'local' ) },
	  expect = { true }
	},

	{ name = 'interwikiMap (non-local prefixes)',
	  func = isValidInterwikiMap, args = { mw.site.interwikiMap( '!local' ) },
	  expect = { true }
	},

	{ name = 'interwikiMap (type error 1)',
	  func = mw.site.interwikiMap, args = { 123 },
	  expect = "bad argument #1 to 'interwikiMap' (string expected, got number)"
	},

	{ name = 'interwikiMap (type error 2)',
	  func = mw.site.interwikiMap, args = { false },
	  expect = "bad argument #1 to 'interwikiMap' (string expected, got boolean)"
	},

	{ name = 'interwikiMap (unknown filter 1)',
	  func = mw.site.interwikiMap, args = { '' },
	  expect = "bad argument #1 to 'interwikiMap' (unknown filter '')"
	},

	{ name = 'interwikiMap (unknown filter 2)',
	  func = mw.site.interwikiMap, args = { 'foo' },
	  expect = "bad argument #1 to 'interwikiMap' (unknown filter 'foo')"
	},
} )
