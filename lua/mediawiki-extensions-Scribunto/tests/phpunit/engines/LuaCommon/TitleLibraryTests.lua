local testframework = require 'Module:TestFramework'

local title, title_copy, title2, title3, title4, title5, title6u, title6s, title4p
if mw.title.testPageId then
	title = mw.title.getCurrentTitle()
	title_copy = mw.title.getCurrentTitle()
	title2 = mw.title.new( 'Module:TestFramework' )
	title3 = mw.title.new( 'interwikiprefix:Module:TestFramework' )
	title4 = mw.title.new( 'Talk:Has/A/Subpage' )
	title5 = mw.title.new( 'Not/A/Subpage' )
	title4.fragment = 'frag'

	title4p = mw.title.new( 'Talk:Has/A' )

	title6u = mw.title.new( 'Module_talk:Test_Framework' )
	title6u.fragment = '__frag__frag__'

	title6s = mw.title.new( 'Module talk:Test Framework' )
	title6s.fragment = '  frag  frag  '
end

local function prop_foreach( prop )
	return title[prop], title2[prop], title3[prop], title4[prop], title5[prop], title6u[prop], title6s[prop]
end

local function func_foreach( func, ... )
	return title[func]( title, ... ),
		title2[func]( title2, ... ),
		title3[func]( title3, ... ),
		title4[func]( title4, ... ),
		title5[func]( title5, ... ),
		title6u[func]( title6u, ... ),
		title6s[func]( title6s, ... )
end

local function identity( ... )
	return ...
end

local function test_space_normalization( s )
	local title = mw.title.new( s )
	return tostring( title ), tostring( title.fragment )
end

local function test_expensive_10()
	for i = 1, 10 do
		local _ = mw.title.new( tostring( i ) ).id
	end
	return 'did not error'
end

local function test_expensive_11()
	for i = 1, 11 do
		local _ = mw.title.new( tostring( i ) ).id
	end
	return 'did not error'
end

local function test_expensive_cached()
	for i = 1, 100 do
		local _ = mw.title.new( 'Title' ).id
	end
	return 'did not error'
end

local function test_inexpensive()
	for i = 1, 100 do
		local _ = mw.title.new( 'Title' ).prefixedText
	end
	return 'did not error'
end

local function test_getContent()
	return mw.title.new( 'ScribuntoTestPage' ):getContent(),
		mw.title.new( 'ScribuntoTestNonExistingPage' ):getContent()
end

local function test_redirectTarget()
	local targets = {}
	local titles = {
		'ScribuntoTestRedirect',
		'ScribuntoTestNonRedirect',
		'ScribuntoTestNonExistingPage'
	}
	for _, title in ipairs( titles ) do
		local target = mw.title.new( title ).redirectTarget
		if title.prefixedText ~= nil then
			target = title.prefixedText
		end
		table.insert( targets, target )
	end
	return unpack( targets )
end

local function test_getCurrentTitle_fragment()
	mw.title.getCurrentTitle().fragment = 'bad'
	return mw.title.getCurrentTitle().fragment
end

-- Tests
local tests = {
	{ name = 'tostring', func = identity, type = 'ToString',
	  args = { title, title2, title3, title4, title5, title6u, title6s },
	  expect = {
		  'Main Page', 'Module:TestFramework', 'interwikiprefix:Module:TestFramework',
		  'Talk:Has/A/Subpage', 'Not/A/Subpage',
		  'Module talk:Test Framework', 'Module talk:Test Framework'
	  }
	},

	{ name = 'title.equal', func = mw.title.equals,
	  args = { title, title },
	  expect = { true }
	},
	{ name = 'title.equal (2)', func = mw.title.equals,
	  args = { title, title_copy },
	  expect = { true }
	},
	{ name = 'title.equal (3)', func = mw.title.equals,
	  args = { title, title2 },
	  expect = { false }
	},
	{ name = '==', func = function ()
		return rawequal( title, title_copy ), title == title, title == title_copy, title == title2
	  end,
	  expect = { false, true, true, false }
	},

	{ name = 'title.compare', func = mw.title.compare,
	  args = { title, title },
	  expect = { 0 }
	},
	{ name = 'title.compare (2)', func = mw.title.compare,
	  args = { title, title_copy },
	  expect = { 0 }
	},
	{ name = 'title.compare (3)', func = mw.title.compare,
	  args = { title, title2 },
	  expect = { -1 }
	},
	{ name = 'title.compare (4)', func = mw.title.compare,
	  args = { title2, title },
	  expect = { 1 }
	},
	{ name = 'title.compare (5)', func = mw.title.compare,
	  args = { title2, title3 },
	  expect = { -1 }
	},
	{ name = 'title.compare (6)', func = mw.title.compare,
	  args = { title6s, title6u },
	  expect = { 0 }
	},
	{ name = '<', func = function ()
		return title < title, title < title_copy, title < title2, title2 < title
	  end,
	  expect = { false, false, true, false }
	},
	{ name = '<=', func = function ()
		return title <= title, title <= title_copy, title <= title2, title2 <= title
	  end,
	  expect = { true, true, true, false }
	},

	{ name = 'title.new with namespace', func = mw.title.new, type = 'ToString',
	  args = { 'TestFramework', 'Module' },
	  expect = { 'Module:TestFramework' }
	},
	{ name = 'title.new with namespace (2)', func = mw.title.new, type = 'ToString',
	  args = { 'TestFramework', mw.site.namespaces.Module.id },
	  expect = { 'Module:TestFramework' }
	},
	{ name = 'title.new with namespace (3)', func = mw.title.new, type = 'ToString',
	  args = { 'Template:TestFramework', 'Module' },
	  expect = { 'Template:TestFramework' }
	},
	{ name = 'title.new space normalization', func = test_space_normalization,
	  args = { ' __ Template __ : __ Test _ Framework __ # _ frag _ frag _ ' },
	  expect = { 'Template:Test Framework', ' frag frag' }
	},
	{ name = 'title.new with invalid title', func = mw.title.new,
	  args = { '<bad title>' },
	  expect = { nil }
	},
	{ name = 'title.new with nonexistent pageid', func = mw.title.new,
	  args = { -1 },
	  expect = { nil }
	},
	{ name = 'title.new with pageid 0', func = mw.title.new,
	  args = { 0 },
	  expect = { nil }
	},
	{ name = 'title.new with existing pageid', func = mw.title.new, type = 'ToString',
	  args = { mw.title.testPageId },
	  expect = { 'ScribuntoTestPage' }
	},

	{ name = 'title.makeTitle', func = mw.title.makeTitle, type = 'ToString',
	  args = { 'Module', 'TestFramework' },
	  expect = { 'Module:TestFramework' }
	},
	{ name = 'title.makeTitle (2)', func = mw.title.makeTitle, type = 'ToString',
	  args = { mw.site.namespaces.Module.id, 'TestFramework' },
	  expect = { 'Module:TestFramework' }
	},
	{ name = 'title.makeTitle (3)', func = mw.title.makeTitle, type = 'ToString',
	  args = { mw.site.namespaces.Module.id, 'Template:TestFramework' },
	  expect = { 'Module:Template:TestFramework' }
	},

	{ name = '.isLocal', func = prop_foreach,
	  args = { 'isLocal' },
	  expect = { true, true, false, true, true, true, true }
	},
	{ name = '.isTalkPage', func = prop_foreach,
	  args = { 'isTalkPage' },
	  expect = { false, false, false, true, false, true, true }
	},
	{ name = '.isSubpage', func = prop_foreach,
	  args = { 'isSubpage' },
	  expect = { false, false, false, true, false, false, false }
	},
	{ name = '.text', func = prop_foreach,
	  args = { 'text' },
	  expect = {
		  'Main Page', 'TestFramework', 'Module:TestFramework', 'Has/A/Subpage', 'Not/A/Subpage',
		  'Test Framework', 'Test Framework'
	  }
	},
	{ name = '.prefixedText', func = prop_foreach,
	  args = { 'prefixedText' },
	  expect = {
		  'Main Page', 'Module:TestFramework', 'interwikiprefix:Module:TestFramework',
		  'Talk:Has/A/Subpage', 'Not/A/Subpage', 'Module talk:Test Framework', 'Module talk:Test Framework',
	  }
	},
	{ name = '.rootText', func = prop_foreach,
	  args = { 'rootText' },
	  expect = {
		  'Main Page', 'TestFramework', 'Module:TestFramework', 'Has', 'Not/A/Subpage',
		  'Test Framework', 'Test Framework'
	  }
	},
	{ name = '.baseText', func = prop_foreach,
	  args = { 'baseText' },
	  expect = {
		  'Main Page', 'TestFramework', 'Module:TestFramework', 'Has/A', 'Not/A/Subpage',
		  'Test Framework', 'Test Framework'
	  }
	},
	{ name = '.subpageText', func = prop_foreach,
	  args = { 'subpageText' },
	  expect = {
		  'Main Page', 'TestFramework', 'Module:TestFramework', 'Subpage', 'Not/A/Subpage',
		  'Test Framework', 'Test Framework'
	  }
	},
	{ name = '.fullText', func = prop_foreach,
	  args = { 'fullText' },
	  expect = {
		  'Main Page', 'Module:TestFramework', 'interwikiprefix:Module:TestFramework',
		  'Talk:Has/A/Subpage#frag', 'Not/A/Subpage',
		  'Module talk:Test Framework# frag frag', 'Module talk:Test Framework# frag frag'
	  }
	},
	{ name = '.subjectNsText', func = prop_foreach,
	  args = { 'subjectNsText' },
	  expect = { '', 'Module', '', '', '', 'Module', 'Module' }
	},
	{ name = '.fragment', func = prop_foreach,
	  args = { 'fragment' },
	  expect = { '', '', '', 'frag', '', ' frag frag', ' frag frag' }
	},
	{ name = '.interwiki', func = prop_foreach,
	  args = { 'interwiki' },
	  expect = { '', '', 'interwikiprefix', '', '', '', '' }
	},
	{ name = '.namespace', func = prop_foreach,
	  args = { 'namespace' },
	  expect = {
		  0, mw.site.namespaces.Module.id, 0, 1, 0,
		  mw.site.namespaces.Module_talk.id, mw.site.namespaces.Module_talk.id
	  }
	},
	{ name = '.protectionLevels', func = prop_foreach,
	  args = { 'protectionLevels' },
	  expect = {
		  { edit = {}, move = {} }, { edit = { 'sysop', 'bogus' }, move = { 'sysop', 'bogus' } },
		  {}, { create = { 'sysop' } }, { edit = { 'autoconfirmed' }, move = { 'sysop' } },
		  { edit = {}, move = { 'sysop' } }, { edit = {}, move = { 'sysop' } }
	  }
	},
	{ name = '.cascadingProtection', func = prop_foreach,
	  args = { 'cascadingProtection' },
	  expect = {
		  { restrictions = { edit = { 'sysop' } }, sources = { 'Lockbox', 'Lockbox2' } }, { restrictions = {}, sources = {} },
		  { restrictions = {}, sources = {} }, { restrictions = {}, sources = {} }, { restrictions = {}, sources = {} },
		  { restrictions = {}, sources = {} }, { restrictions = {}, sources = {} }
	  }
	},
	{ name = '.inNamespace()', func = func_foreach,
	  args = { 'inNamespace', 'Module' },
	  expect = { false, true, false, false, false, false, false }
	},
	{ name = '.inNamespace() 2', func = func_foreach,
	  args = { 'inNamespace', mw.site.namespaces.Module.id },
	  expect = { false, true, false, false, false, false, false }
	},
	{ name = '.inNamespaces()', func = func_foreach,
	  args = { 'inNamespaces', 0, 1 },
	  expect = { true, false, true, true, true, false, false }
	},
	{ name = '.hasSubjectNamespace()', func = func_foreach,
	  args = { 'hasSubjectNamespace', 0 },
	  expect = { true, false, true, true, true, false, false }
	},
	{ name = '.isSubpageOf() 1', func = func_foreach,
	  args = { 'isSubpageOf', title },
	  expect = { false, false, false, false, false, false, false }
	},
	{ name = '.isSubpageOf() 2', func = func_foreach,
	  args = { 'isSubpageOf', title4p },
	  expect = { false, false, false, true, false, false, false }
	},
	{ name = '.partialUrl()', func = func_foreach,
	  args = { 'partialUrl' },
	  expect = {
		  'Main_Page', 'TestFramework', 'Module:TestFramework', 'Has/A/Subpage', 'Not/A/Subpage',
		  'Test_Framework', 'Test_Framework'
	  }
	},
	{ name = '.fullUrl()', func = func_foreach,
	  args = { 'fullUrl' },
	  expect = {
		  '//wiki.local/wiki/Main_Page',
		  '//wiki.local/wiki/Module:TestFramework',
		  '//test.wikipedia.org/wiki/Module:TestFramework',
		  '//wiki.local/wiki/Talk:Has/A/Subpage#frag',
		  '//wiki.local/wiki/Not/A/Subpage',
		  '//wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
		  '//wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
	  }
	},
	{ name = '.fullUrl() 2', func = func_foreach,
	  args = { 'fullUrl', { action = 'test' } },
	  expect = {
		  '//wiki.local/w/index.php?title=Main_Page&action=test',
		  '//wiki.local/w/index.php?title=Module:TestFramework&action=test',
		  '//test.wikipedia.org/wiki/Module:TestFramework?action=test',
		  '//wiki.local/w/index.php?title=Talk:Has/A/Subpage&action=test#frag',
		  '//wiki.local/w/index.php?title=Not/A/Subpage&action=test',
		  '//wiki.local/w/index.php?title=Module_talk:Test_Framework&action=test#_frag_frag',
		  '//wiki.local/w/index.php?title=Module_talk:Test_Framework&action=test#_frag_frag',
	  }
	},
	{ name = '.fullUrl() 3', func = func_foreach,
	  args = { 'fullUrl', nil, 'http' },
	  expect = {
		  'http://wiki.local/wiki/Main_Page',
		  'http://wiki.local/wiki/Module:TestFramework',
		  'http://test.wikipedia.org/wiki/Module:TestFramework',
		  'http://wiki.local/wiki/Talk:Has/A/Subpage#frag',
		  'http://wiki.local/wiki/Not/A/Subpage',
		  'http://wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
		  'http://wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
	  }
	},
	{ name = '.localUrl()', func = func_foreach,
	  args = { 'localUrl' },
	  expect = {
		  '/wiki/Main_Page',
		  '/wiki/Module:TestFramework',
		  '//test.wikipedia.org/wiki/Module:TestFramework',
		  '/wiki/Talk:Has/A/Subpage',
		  '/wiki/Not/A/Subpage',
		  '/wiki/Module_talk:Test_Framework',
		  '/wiki/Module_talk:Test_Framework',
	  }
	},
	{ name = '.canonicalUrl()', func = func_foreach,
	  args = { 'canonicalUrl' },
	  expect = {
		  'http://wiki.local/wiki/Main_Page',
		  'http://wiki.local/wiki/Module:TestFramework',
		  'http://test.wikipedia.org/wiki/Module:TestFramework',
		  'http://wiki.local/wiki/Talk:Has/A/Subpage#frag',
		  'http://wiki.local/wiki/Not/A/Subpage',
		  'http://wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
		  'http://wiki.local/wiki/Module_talk:Test_Framework#_frag_frag',
	  }
	},

	{ name = '.getContent()', func = test_getContent,
	  expect = {
		  '{{int:mainpage}}<includeonly>...</includeonly><noinclude>...</noinclude>',
		  nil,
	  }
	},

	{ name = '.redirectTarget', func = test_redirectTarget, type = 'ToString',
	  expect = { 'ScribuntoTestTarget', false, false }
	},

	{ name = 'not quite too many expensive functions', func = test_expensive_10,
	  expect = { 'did not error' }
	},
	{ name = 'too many expensive functions', func = test_expensive_11,
	  expect = 'too many expensive function calls'
	},
	{ name = "previously cached titles shouldn't count as expensive", func = test_expensive_cached,
	  expect = { 'did not error' }
	},
	{ name = "inexpensive actions shouldn't count as expensive", func = test_inexpensive,
	  expect = { 'did not error' }
	},
	{ name = "fragments don't leak via getCurrentTitle()", func = test_getCurrentTitle_fragment,
	  expect = { '' }
	},
}

return testframework.getTestProvider( tests )
