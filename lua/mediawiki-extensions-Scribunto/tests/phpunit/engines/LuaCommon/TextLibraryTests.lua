local testframework = require 'Module:TestFramework'

-- Force the argument list to be ordered
local tagattrs = { absent = false, present = true, key = 'value', n = 42 }
setmetatable( tagattrs, { __pairs = function ( t )
	local keys = { 'absent', 'present', 'key', 'n' }
	local i = 0
	return function()
		i = i + 1
		if i <= #keys then
			return keys[i], t[keys[i]]
		end
	end
end } )

-- For data provider, make sure this is defined
mw.text.stripTest = mw.text.stripTest or { nowiki = '!!!', general = '!!!' }

-- Can't directly expect the value from mw.text.stripTest, because when
-- 'expect' is processed by the data provider it's the dummy entry above.
local function stripTest( func, marker )
	local result = func( marker )
	if result == marker then
		result = 'strip-marker'
	end
	return result
end

-- Round-trip test for json encode/decode, mainly because we can't rely on
-- order when encoding multi-element objects.
function jsonRoundTripTest( tree )
	return mw.text.jsonDecode( mw.text.jsonEncode( tree ) )
end

local recursiveTable = {}
recursiveTable.recursiveTable = recursiveTable

-- Tests
local tests = {
	{ name = 'trim',
	  func = mw.text.trim, args = { '  foo bar  ' },
	  expect = { 'foo bar' }
	},
	{ name = 'trim right',
	  func = mw.text.trim, args = { 'foo bar  ' },
	  expect = { 'foo bar' }
	},
	{ name = 'trim left',
	  func = mw.text.trim, args = { '  foo bar' },
	  expect = { 'foo bar' }
	},
	{ name = 'trim none',
	  func = mw.text.trim, args = { 'foo bar' },
	  expect = { 'foo bar' }
	},
	{ name = 'trim charset',
	  func = mw.text.trim, args = { 'xxx foo bar xxx', 'x' },
	  expect = { ' foo bar ' }
	},

	{ name = 'encode',
	  func = mw.text.encode, args = { '<b>foo\194\160"bar"</b> & \'baz\'' },
	  expect = { '&lt;b&gt;foo&nbsp;&quot;bar&quot;&lt;/b&gt; &amp; &#039;baz&#039;' }
	},
	{ name = 'encode charset',
	  func = mw.text.encode, args = { '<b>foo\194\160"bar"</b> & \'baz\'', 'aeiou' },
	  expect = { '<b>f&#111;&#111;\194\160"b&#97;r"</b> & \'b&#97;z\'' }
	},

	{ name = 'decode',
	  func = mw.text.decode,
	  args = { '&lt;&gt;&amp;&quot; &#102;&#111;&#x6f; &#x0066;&#00111;&#x6F; &hearts; &amp;quot;' },
	  expect = { '<>&" foo foo &hearts; &quot;' }
	},
	{ name = 'decode named',
	  func = mw.text.decode,
	  args = { '&lt;&gt;&amp;&quot; &#102;&#111;&#x6f; &#x0066;&#00111;&#x6F; &hearts; &amp;quot;', true },
	  expect = { '<>&" foo foo ♥ &quot;' }
	},

	{ name = 'nowiki',
	  func = mw.text.nowiki,
	  args = { '*"&\'<=>[]{|}#*:;\n*\n#\n:\n;\nhttp://example.com:80/\nRFC 123, ISBN 456' },
	  expect = {
		  '&#42;&#34;&#38;&#39;&#60;&#61;&#62;&#91;&#93;&#123;&#124;&#125;#*:;' ..
		  '\n&#42;\n&#35;\n&#58;\n&#59;\nhttp&#58;//example.com:80/' ..
		  '\nRFC&#32;123, ISBN&#32;456'
	  }
	},

	{ name = 'tag, simple',
	  func = mw.text.tag,
	  args = { { name = 'b' } },
	  expect = { '<b>' }
	},
	{ name = 'tag, simple with content',
	  func = mw.text.tag,
	  args = { { name = 'b', content = 'foo' } },
	  expect = { '<b>foo</b>' }
	},
	{ name = 'tag, simple self-closing',
	  func = mw.text.tag,
	  args = { { name = 'br', content = false } },
	  expect = { '<br />' }
	},
	{ name = 'tag, args',
	  func = mw.text.tag,
	  args = { { name = 'b', attrs = tagattrs } },
	  expect = { '<b present key="value" n="42">' }
	},
	{ name = 'tag, args with content',
	  func = mw.text.tag,
	  args = { { name = 'b', attrs = tagattrs, content = 'foo' } },
	  expect = { '<b present key="value" n="42">foo</b>' }
	},
	{ name = 'tag, args self-closing',
	  func = mw.text.tag,
	  args = { { name = 'br', attrs = tagattrs, content = false } },
	  expect = { '<br present key="value" n="42" />' }
	},
	{ name = 'tag, args, positional params',
	  func = mw.text.tag,
	  args = { 'b', tagattrs },
	  expect = { '<b present key="value" n="42">' }
	},
	{ name = 'tag, args with content, positional params',
	  func = mw.text.tag,
	  args = { 'b', tagattrs, 'foo' },
	  expect = { '<b present key="value" n="42">foo</b>' }
	},

	{ name = 'unstrip (nowiki)',
	  func = stripTest,
	  args = { mw.text.unstrip, mw.text.stripTest.nowiki },
	  expect = { 'NoWiki' }
	},
	{ name = 'unstrip (general)',
	  func = stripTest,
	  args = { mw.text.unstrip, mw.text.stripTest.general },
	  expect = { '' }
	},

	{ name = 'unstripNoWiki (nowiki)',
	  func = stripTest,
	  args = { mw.text.unstripNoWiki, mw.text.stripTest.nowiki },
	  expect = { 'NoWiki' }
	},
	{ name = 'unstripNoWiki (general)',
	  func = stripTest,
	  args = { mw.text.unstripNoWiki, mw.text.stripTest.general },
	  expect = { 'strip-marker' }
	},

	{ name = 'killMarkers',
	  func = mw.text.killMarkers,
	  args = { 'a' .. mw.text.stripTest.nowiki .. 'b' .. mw.text.stripTest.general .. 'c' },
	  expect = { 'abc' }
	},

	{ name = 'split, simple',
	  func = mw.text.split, args = { 'a,b,c,d', ',' },
	  expect = { { 'a', 'b', 'c', 'd' } }
	},
	{ name = 'split, no separator',
	  func = mw.text.split, args = { 'xxx', ',' },
	  expect = { { 'xxx' } }
	},
	{ name = 'split, empty string',
	  func = mw.text.split, args = { '', ',' },
	  expect = { { '' } }
	},
	{ name = 'split, with empty items',
	  func = mw.text.split, args = { ',,', ',' },
	  expect = { { '', '', '' } }
	},
	{ name = 'split, with empty items (1)',
	  func = mw.text.split, args = { 'x,,', ',' },
	  expect = { { 'x', '', '' } }
	},
	{ name = 'split, with empty items (2)',
	  func = mw.text.split, args = { ',x,', ',' },
	  expect = { { '', 'x', '' } }
	},
	{ name = 'split, with empty items (3)',
	  func = mw.text.split, args = { ',,x', ',' },
	  expect = { { '', '', 'x' } }
	},
	{ name = 'split, with empty items (4)',
	  func = mw.text.split, args = { ',x,x', ',' },
	  expect = { { '', 'x', 'x' } }
	},
	{ name = 'split, with empty items (5)',
	  func = mw.text.split, args = { 'x,,x', ',' },
	  expect = { { 'x', '', 'x' } }
	},
	{ name = 'split, with empty items (7)',
	  func = mw.text.split, args = { 'x,x,', ',' },
	  expect = { { 'x', 'x', '' } }
	},
	{ name = 'split, with empty pattern',
	  func = mw.text.split, args = { 'xxx', '' },
	  expect = { { 'x', 'x', 'x' } }
	},
	{ name = 'split, with empty pattern (2)',
	  func = mw.text.split, args = { 'xxx', ',?' },
	  expect = { { 'x', 'x', 'x' } }
	},

	{ name = 'listToText (0)',
	  func = mw.text.listToText, args = { {} },
	  expect = { '' }
	},
	{ name = 'listToText (1)',
	  func = mw.text.listToText, args = { { 1 } },
	  expect = { '1' }
	},
	{ name = 'listToText (2)',
	  func = mw.text.listToText, args = { { 1, 2 } },
	  expect = { '1 and 2' }
	},
	{ name = 'listToText (3)',
	  func = mw.text.listToText, args = { { 1, 2, 3 } },
	  expect = { '1, 2 and 3' }
	},
	{ name = 'listToText (4)',
	  func = mw.text.listToText, args = { { 1, 2, 3, 4 } },
	  expect = { '1, 2, 3 and 4' }
	},
	{ name = 'listToText, alternate separator',
	  func = mw.text.listToText, args = { { 1, 2, 3, 4 }, '; ' },
	  expect = { '1; 2; 3 and 4' }
	},
	{ name = 'listToText, alternate conjunction',
	  func = mw.text.listToText, args = { { 1, 2, 3, 4 }, nil, ' or ' },
	  expect = { '1, 2, 3 or 4' }
	},

	{ name = 'truncate, no truncation',
	  func = mw.text.truncate, args = { 'foobarbaz', 9 },
	  expect = { 'foobarbaz' }
	},
	{ name = 'truncate, no truncation (2)',
	  func = mw.text.truncate, args = { 'foobarbaz', -9 },
	  expect = { 'foobarbaz' }
	},
	{ name = 'truncate, tail truncation',
	  func = mw.text.truncate, args = { 'foobarbaz', 3 },
	  expect = { 'foo...' }
	},
	{ name = 'truncate, head truncation',
	  func = mw.text.truncate, args = { 'foobarbaz', -3 },
	  expect = { '...baz' }
	},
	{ name = 'truncate, avoid silly truncation',
	  func = mw.text.truncate, args = { 'foobarbaz', 8 },
	  expect = { 'foobarbaz' }
	},
	{ name = 'truncate, avoid silly truncation (2)',
	  func = mw.text.truncate, args = { 'foobarbaz', 6 },
	  expect = { 'foobarbaz' }
	},
	{ name = 'truncate, alternate ellipsis',
	  func = mw.text.truncate, args = { 'foobarbaz', 3, '!' },
	  expect = { 'foo!' }
	},
	{ name = 'truncate, with adjusted length',
	  func = mw.text.truncate, args = { 'foobarbaz', 6, nil, true },
	  expect = { 'foo...' }
	},
	{ name = 'truncate, with adjusted length (2)',
	  func = mw.text.truncate, args = { 'foobarbaz', -6, nil, true },
	  expect = { '...baz' }
	},
	{ name = 'truncate, ridiculously short',
	  func = mw.text.truncate, args = { 'foobarbaz', 1, nil, true },
	  expect = { '...' }
	},
	{ name = 'truncate, ridiculously short (2)',
	  func = mw.text.truncate, args = { 'foobarbaz', -1, nil, true },
	  expect = { '...' }
	},

	{ name = 'json encode-decode round trip, simple object',
	  func = jsonRoundTripTest,
	  args = { {
		  int = 2,
		  string = "foo",
		  ['true'] = true,
		  ['false'] = false,
	  } },
	  expect = { {
		  int = 2,
		  string = "foo",
		  ['true'] = true,
		  ['false'] = false,
	  } },
	},
	{ name = 'json decode, simple object',
	  func = mw.text.jsonDecode,
	  args = { '{"int":2,"string":"foo","true":true,"false":false}' },
	  expect = { {
		  int = 2,
		  string = "foo",
		  ['true'] = true,
		  ['false'] = false,
	  } },
	},
	{ name = 'json encode, simple array',
	  func = mw.text.jsonEncode,
	  args = { { 1, "foo", true, false } },
	  expect = { '[1,"foo",true,false]' }
	},
	{ name = 'json decode, simple array',
	  func = mw.text.jsonDecode,
	  args = { '[1,"foo",true,false]' },
	  expect = { { 1, "foo", true, false } }
	},
	{ name = 'json encode-decode round trip, object with numeric keys',
	  func = jsonRoundTripTest,
	  args = { { x = "x", [1] = 1, [2] = 2 } },
	  expect = { { x = "x", [1] = 1, [2] = 2 } }
	},
	{ name = 'json decode, object with numeric keys',
	  func = mw.text.jsonDecode,
	  args = { '{"x":"x","1":1,"2":2}' },
	  expect = { { x = "x", [1] = 1, [2] = 2 } }
	},
	{ name = 'json encode, simple array, preserve keys',
	  func = mw.text.jsonEncode,
	  args = { { 1, "foo", true, false }, mw.text.JSON_PRESERVE_KEYS },
	  expect = { '{"1":1,"2":"foo","3":true,"4":false}' }
	},
	{ name = 'json decode, simple array, preserve keys',
	  func = mw.text.jsonDecode,
	  args = { '[1,"foo",true,false]', mw.text.JSON_PRESERVE_KEYS },
	  expect = { { [0] = 1, "foo", true, false } }
	},
	{ name = 'json encode, nested arrays',
	  func = mw.text.jsonEncode,
	  args = { { 1, 2, 3, { 4, 5, { 6, 7, 8 } } } },
	  expect = { '[1,2,3,[4,5,[6,7,8]]]' }
	},
	{ name = 'json decode, nested arrays',
	  func = mw.text.jsonDecode,
	  args = { '[1,2,3,[4,5,[6,7,8]]]' },
	  expect = { { 1, 2, 3, { 4, 5, { 6, 7, 8 } } } }
	},
	{ name = 'json encode, array in object',
	  func = mw.text.jsonEncode,
	  args = { { x = { 1, 2, { y = { 3, 4 } } } } },
	  expect = { '{"x":[1,2,{"y":[3,4]}]}' }
	},
	{ name = 'json decode, array in object',
	  func = mw.text.jsonDecode,
	  args = { '{"x":[1,2,{"y":[3,4]}],"z":[5,6]}' },
	  expect = { { x = { 1, 2, { y = { 3, 4 } } }, z = { 5, 6 } } }
	},
	{ name = 'json decode, empty array',
	  func = mw.text.jsonDecode,
	  args = { '[]' },
	  expect = { {} }
	},
	{ name = 'json decode, empty object',
	  func = mw.text.jsonDecode,
	  args = { '{}' },
	  expect = { {} }
	},
	{ name = 'json encode, object with one large numeric index',
	  func = mw.text.jsonEncode,
	  args = { { [1000] = 1 } },
	  expect = { '{"1000":1}' }
	},
	{ name = 'json decode, object with one large numeric index',
	  func = mw.text.jsonDecode,
	  args = { '{"1000":1}' },
	  expect = { { [1000] = 1 } }
	},
	{ name = 'json encode, array with holes (ideally would be "[1,2,nil,4]", but probably not worth worrying about)',
	  func = mw.text.jsonEncode,
	  args = { { 1, 2, nil, 4 } },
	  expect = { '{"1":1,"2":2,"4":4}' }
	},
	{ name = 'json decode, array with null (ideally would somehow insist on having a [3] = nil element, but that\'s not easily possible)',
	  func = mw.text.jsonDecode,
	  args = { '[1,2,null,4]' },
	  expect = { { 1, 2, [4] = 4 } }
	},
	{ name = 'json encode, empty table (could be either [] or {}, but change should be announced)',
	  func = mw.text.jsonEncode,
	  args = { {} },
	  expect = { '[]' }
	},
	{ name = 'json encode, table with index 0 (technically wrong, but probably not worth working around)',
	  func = mw.text.jsonEncode,
	  args = { { [0] = "zero" } },
	  expect = { '["zero"]' }
	},
	{ name = 'json decode, object with index 1 (technically wrong, but probably not worth working around)',
	  func = mw.text.jsonDecode,
	  args = { '{"1":"one"}' },
	  expect = { { 'one' } }
	},
	{ name = 'json encode, pretty',
	  func = mw.text.jsonEncode,
	  args = { { 1, 2, 3, { 4, 5, { 6, 7, { x = 8 } } } }, mw.text.JSON_PRETTY },
	  expect = { [=[[
    1,
    2,
    3,
    [
        4,
        5,
        [
            6,
            7,
            {
                "x": 8
            }
        ]
    ]
]]=] }
	},
	{ name = 'json encode, raw value (technically not allowed, but a common extension)',
	  func = mw.text.jsonEncode,
	  args = { "foo" },
	  expect = { '"foo"' }
	},
	{ name = 'json decode, raw value (technically not allowed, but a common extension)',
	  func = mw.text.jsonDecode,
	  args = { '"foo"' },
	  expect = { 'foo' }
	},
	{ name = 'json encode, sneaky nil injection (object)',
	  func = mw.text.jsonEncode,
	  args = { setmetatable( {}, {
		  __pairs = function ( t )
			  return function ( t, k )
				  if k ~= "foo" then
					  return "foo", nil
				  end
			  end, t, nil
		  end,
	  } ) },
	  expect = { '{"foo":null}' }
	},
	{ name = 'json encode, sneaky nil injection (array)',
	  func = mw.text.jsonEncode,
	  args = { setmetatable( { "one", "two", nil, "four" }, {
		  __pairs = function ( t )
			  return function ( t, k )
				  k = k and k + 1 or 1
				  if k <= 4 then
					  return k, t[k]
				  end
			  end, t, nil
		  end,
	  } ) },
	  expect = { '["one","two",null,"four"]' }
	},

	{ name = 'json encode, invalid values (inf)',
	  func = mw.text.jsonEncode,
	  args = { { 1/0 } },
	  expect = 'mw.text.jsonEncode: Cannot encode non-finite numbers'
	},
	{ name = 'json encode, invalid values (nan)',
	  func = mw.text.jsonEncode,
	  args = { { 0/0 } },
	  expect = 'mw.text.jsonEncode: Cannot encode non-finite numbers'
	},
	{ name = 'json encode, invalid values (function)',
	  func = mw.text.jsonEncode,
	  args = { { function () end } },
	  expect = 'mw.text.jsonEncode: Cannot encode type \'function\''
	},
	{ name = 'json encode, invalid values (recursive table)',
	  func = mw.text.jsonEncode,
	  args = { { recursiveTable } },
	  expect = 'mw.text.jsonEncode: Cannot use recursive tables'
	},
	{ name = 'json encode, invalid values (table with bool key)',
	  func = mw.text.jsonEncode,
	  args = { { [true] = 1 } },
	  expect = 'mw.text.jsonEncode: Cannot use type \'boolean\' as a table key'
	},
	{ name = 'json encode, invalid values (table with function key)',
	  func = mw.text.jsonEncode,
	  args = { { [function() end] = 1 } },
	  expect = 'mw.text.jsonEncode: Cannot use type \'function\' as a table key'
	},
	{ name = 'json encode, invalid values (table with inf key)',
	  func = mw.text.jsonEncode,
	  args = { { [1/0] = 1 } },
	  expect = 'mw.text.jsonEncode: Cannot use \'inf\' as a table key'
	},

	{ name = 'json decode, invalid values (trailing comma)',
	  func = mw.text.jsonDecode,
	  args = { '{"x":1,}' },
	  expect = 'mw.text.jsonDecode: Syntax error'
	},
	{ name = 'json decode, trailing comma with JSON_TRY_FIXING',
	  func = mw.text.jsonDecode,
	  args = { '{"x":1,}', mw.text.JSON_TRY_FIXING },
	  expect = { { x = 1 } }
	},
}

return testframework.getTestProvider( tests )
