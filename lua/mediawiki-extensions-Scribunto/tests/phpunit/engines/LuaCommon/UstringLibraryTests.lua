local testframework = require 'Module:TestFramework'

local str1 = "\0\127\194\128\223\191\224\160\128\239\191\191\240\144\128\128\244\143\191\191"
local str2 = "foo bar főó foó baz foooo foofoo fo"
local str3 = "??? foo bar főó foó baz foooo foofoo fo ok?"
local str4 = {}
for i = 1, 10000/4 do
	str4[i] = "főó "
end
str4 = table.concat( str4 )

local function testLongGcodepoint()
	local ret = {}
	local i = 1
	for cp in mw.ustring.gcodepoint( str4 ) do
		if i <= 4 or i > 9996 then
			ret[i] = cp
		end
		i = i + 1
	end
	return ret
end

return testframework.getTestProvider( {
	{ name = 'isutf8: valid string', func = mw.ustring.isutf8,
	  args = { "\0 \127 \194\128 \223\191 \224\160\128 \239\191\191 \240\144\128\128 \244\143\191\191" },
	  expect = { true }
	},
	{ name = 'isutf8: out of range character', func = mw.ustring.isutf8,
	  args = { "\244\144\128\128" },
	  expect = { false }
	},
	{ name = 'isutf8: insufficient continuation bytes', func = mw.ustring.isutf8,
	  args = { "\240\128\128" },
	  expect = { false }
	},
	{ name = 'isutf8: excess continuation bytes', func = mw.ustring.isutf8,
	  args = { "\194\128\128" },
	  expect = { false }
	},
	{ name = 'isutf8: bare continuation byte', func = mw.ustring.isutf8,
	  args = { "\128" },
	  expect = { false }
	},
	{ name = 'isutf8: overlong encoding', func = mw.ustring.isutf8,
	  args = { "\192\128" },
	  expect = { false }
	},
	{ name = 'isutf8: overlong encoding (2)', func = mw.ustring.isutf8,
	  args = { "\193\191" },
	  expect = { false }
	},

	{ name = 'byteoffset: (1)', func = mw.ustring.byteoffset,
	  args = { "fóo", 1 },
	  expect = { 1 }
	},
	{ name = 'byteoffset: (2)', func = mw.ustring.byteoffset,
	  args = { "fóo", 2 },
	  expect = { 2 }
	},
	{ name = 'byteoffset: (3)', func = mw.ustring.byteoffset,
	  args = { "fóo", 3 },
	  expect = { 4 }
	},
	{ name = 'byteoffset: (4)', func = mw.ustring.byteoffset,
	  args = { "fóo", 4 },
	  expect = { nil }
	},
	{ name = 'byteoffset: (0,1)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, 1 },
	  expect = { 1 }
	},
	{ name = 'byteoffset: (0,2)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, 2 },
	  expect = { 2 }
	},
	{ name = 'byteoffset: (0,3)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, 3 },
	  expect = { 2 }
	},
	{ name = 'byteoffset: (0,4)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, 4 },
	  expect = { 4 }
	},
	{ name = 'byteoffset: (0,5)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, 5 },
	  expect = { nil }
	},
	{ name = 'byteoffset: (0,-1)', func = mw.ustring.byteoffset,
	  args = { "fóo", 0, -1 },
	  expect = { 4 }
	},
	{ name = 'byteoffset: (0,-1)', func = mw.ustring.byteoffset,
	  args = { "foó", 0, -1 },
	  expect = { 3 }
	},
	{ name = 'byteoffset: (1,-1)', func = mw.ustring.byteoffset,
	  args = { "fóo", 1, -1 },
	  expect = { 4 }
	},
	{ name = 'byteoffset: (1,-1)', func = mw.ustring.byteoffset,
	  args = { "foó", 1, -1 },
	  expect = { nil }
	},

	{ name = 'codepoint: whole string', func = mw.ustring.codepoint,
	  args = { str1, 1, -1 },
	  expect = { 0, 0x7f, 0x80, 0x7ff, 0x800, 0xffff, 0x10000, 0x10ffff }
	},
	{ name = 'codepoint: substring', func = mw.ustring.codepoint,
	  args = { str1, 5, -2 },
	  expect = { 0x800, 0xffff, 0x10000 }
	},
	{ name = 'codepoint: (5,4)', func = mw.ustring.codepoint,
	  args = { str1, 5, 4 },
	  expect = {}
	},
	{ name = 'codepoint: (1,0)', func = mw.ustring.codepoint,
	  args = { str1, 1, 0 },
	  expect = {}
	},
	{ name = 'codepoint: (9,9)', func = mw.ustring.codepoint,
	  args = { str1, 9, 9 },
	  expect = {}
	},
	{ name = 'codepoint: end of a really long string', func = mw.ustring.codepoint,
	  args = { str4, 9000, 9004 },
	  expect = { 0x20, 0x66, 0x151, 0xf3, 0x20 }
	},

	{ name = 'char: basic test', func = mw.ustring.char,
	  args = { 0, 0x7f, 0x80, 0x7ff, 0x800, 0xffff, 0x10000, 0x10ffff },
	  expect = { str1 }
	},
	{ name = 'char: invalid codepoint', func = mw.ustring.char,
	  args = { 0x110000 },
	  expect = "bad argument #1 to 'char' (value out of range)"
	},
	{ name = 'char: invalid value', func = mw.ustring.char,
	  args = { 'foo' },
	  expect = "bad argument #1 to 'char' (number expected, got string)"
	},

	{ name = 'len: basic test', func = mw.ustring.len,
	  args = { str1 },
	  expect = { 8 }
	},
	{ name = 'len: invalid string', func = mw.ustring.len,
	  args = { "\244\144\128\128" },
	  expect = { nil }
	},

	{ name = 'sub: (4)', func = mw.ustring.sub,
	  args = { str1, 4 },
	  expect = { "\223\191\224\160\128\239\191\191\240\144\128\128\244\143\191\191" }
	},
	{ name = 'sub: (4,7)', func = mw.ustring.sub,
	  args = { str1, 4, 7 },
	  expect = { "\223\191\224\160\128\239\191\191\240\144\128\128" }
	},
	{ name = 'sub: (4,-1)', func = mw.ustring.sub,
	  args = { str1, 4, -1 },
	  expect = { "\223\191\224\160\128\239\191\191\240\144\128\128\244\143\191\191" }
	},
	{ name = 'sub: (4,-2)', func = mw.ustring.sub,
	  args = { str1, 4, -2 },
	  expect = { "\223\191\224\160\128\239\191\191\240\144\128\128" }
	},
	{ name = 'sub: (-2)', func = mw.ustring.sub,
	  args = { str1, -2 },
	  expect = { "\240\144\128\128\244\143\191\191" }
	},
	{ name = 'sub: (9)', func = mw.ustring.sub,
	  args = { str1, 9 },
	  expect = { "" }
	},
	{ name = 'sub: (0)', func = mw.ustring.sub,
	  args = { str1, 0 },
	  expect = { str1 }
	},
	{ name = 'sub: (4,3)', func = mw.ustring.sub,
	  args = { str1, 4, 3 },
	  expect = { "" }
	},
	{ name = 'sub: (1,0)', func = mw.ustring.sub,
	  args = { str2, 1, 0 },
	  expect = { "" }
	},
	{ name = 'sub: (5,5)', func = mw.ustring.sub,
	  args = { str1, 5, 5 },
	  expect = { "\224\160\128" }
	},
	{ name = 'sub: (9,9)', func = mw.ustring.sub,
	  args = { str1, 9, 9 },
	  expect = { "" }
	},
	{ name = 'sub: empty string', func = mw.ustring.sub,
	  args = { '', 5 },
	  expect = { "" }
	},

	{ name = 'upper: basic test', func = mw.ustring.upper,
	  args = { "fóó?" },
	  expect = { "FÓÓ?" }
	},
	{ name = 'lower: basic test', func = mw.ustring.lower,
	  args = { "FÓÓ?" },
	  expect = { "fóó?" }
	},

	{ name = 'find: (simple)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡foo' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (%)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fo%+' },
	  expect = { }
	},
	{ name = 'find: (%)', func = mw.ustring.find,
	  args = { "bar ¡fo+ bar", '¡fo%+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (+)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fo+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (+) (2)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fx+o+' },
	  expect = {}
	},
	{ name = 'find: (?)', func = mw.ustring.find,
	  args = { "bar ¡foox bar", '¡foox?' },
	  expect = { 5, 9 }
	},
	{ name = 'find: (?) (2)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡foox?' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (*)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fx*oo' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (-)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fo-' },
	  expect = { 5, 6 }
	},
	{ name = 'find: (-)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡fo-o' },
	  expect = { 5, 7 }
	},
	{ name = 'find: (-)', func = mw.ustring.find,
	  args = { "bar ¡foox bar", '¡fo-x' },
	  expect = { 5, 9 }
	},
	{ name = 'find: (%a)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '¡f%a' },
	  expect = { 5, 7 }
	},
	{ name = 'find: (%a, utf8)', func = mw.ustring.find,
	  args = { "bar ¡fóó bar", '¡f%a' },
	  expect = { 5, 7 }
	},
	{ name = 'find: (%a, utf8 2)', func = mw.ustring.find,
	  args = { "bar ¡fóó bar", 'f%a' },
	  expect = { 6, 7 }
	},
	{ name = 'find: (%a+)', func = mw.ustring.find,
	  args = { "bar ¡fóó bar", '¡f%a+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: ([]+)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '¡f[oó]+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: ([-]+)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '¡f[a-uá-ú]+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: ([-]+ 2)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '¡f[a-ú]+' },
	  expect = { 5, 8 }
	},
	{ name = 'find: (%b)', func = mw.ustring.find,
	  args = { "bar ¡<foo <foo> foo> bar", '¡%b<>' },
	  expect = { 5, 20 }
	},
	{ name = 'find: (%b 2)', func = mw.ustring.find,
	  args = { "bar ¡(foo (foo) foo) bar", '¡%b()' },
	  expect = { 5, 20 }
	},
	{ name = 'find: (%b 3)', func = mw.ustring.find,
	  args = { "bar ¡-foo-foo- bar", '¡%b--' },
	  expect = { 5, 10 }
	},
	{ name = 'find: (%b 4)', func = mw.ustring.find,
	  args = { "bar «foo «foo» foo» bar", '%b«»' },
	  expect = { 5, 19 }
	},
	{ name = 'find: (%b 5)', func = mw.ustring.find,
	  args = { "bar !foo !foo¡ foo¡ bar", '%b!¡' },
	  expect = { 5, 19 }
	},
	{ name = 'find: (%b 6)', func = mw.ustring.find,
	  args = { "bar ¡foo ¡foo! foo! bar", '%b¡!' },
	  expect = { 5, 19 }
	},
	{ name = 'find: (%b 7)', func = mw.ustring.find,
	  args = { "bar ¡foo¡foo¡ bar", '%b¡¡' },
	  expect = { 5, 9 }
	},
	{ name = 'find: (%f)', func = mw.ustring.find,
	  args = { "foo ¡foobar ¡foo bar baz", '¡.-%f[%s]' },
	  expect = { 5, 11 }
	},
	{ name = 'find: (%f 2)', func = mw.ustring.find,
	  args = { "foo ¡foobar ¡foo bar baz", '¡foo%f[%s]' },
	  expect = { 13, 16 }
	},
	{ name = 'find: (%f 3)', func = mw.ustring.find,
	  args = { "foo foo¡foobar ¡foo bar baz", '%f[%S]¡.-%f[%s]' },
	  expect = { 16, 19 }
	},
	{ name = 'find: (%f 4)', func = mw.ustring.find,
	  args = { "foo foo¡foobar ¡foo bar baz", '%f[%S]¡.-%f[%s]', 16 },
	  expect = { 16, 19 }
	},
	{ name = 'find: (%f 5)', func = mw.ustring.find,
	  args = { "foo ¡bar baz", '%f[%Z]' },
	  expect = { 1, 0 }
	},
	{ name = 'find: (%f 6)', func = mw.ustring.find,
	  args = { "foo ¡bar baz", '%f[%z]' },
	  expect = { 13, 12 }
	},
	{ name = 'find: (%f 7)', func = mw.ustring.find,
	  args = { "foo ¡b\0r baz", '%f[%Z]', 2 },
	  expect = { 8, 7 }
	},
	{ name = 'find: (%f 8)', func = mw.ustring.find,
	  args = { "\0foo ¡b\0r baz", '%f[%z]' },
	  expect = { 8, 7 }
	},
	{ name = 'find: (%f 9)', func = mw.ustring.find,
	  args = { "\0foo ¡b\0r baz", '%f[%Z]' },
	  expect = { 2, 1 }
	},
	{ name = 'find: (%A)', func = mw.ustring.find,
	  args = { "fóó? bar", '%A+' },
	  expect = { 4, 5 }
	},
	{ name = 'find: (%W)', func = mw.ustring.find,
	  args = { "fóó? bar", '%W+' },
	  expect = { 4, 5 }
	},
	{ name = 'find: ([^])', func = mw.ustring.find,
	  args = { "fóó? bar", '[^a-zó]+' },
	  expect = { 4, 5 }
	},
	{ name = 'find: ([^] 2)', func = mw.ustring.find,
	  args = { "fó0? bar", '[^%a0-9]+' },
	  expect = { 4, 5 }
	},
	{ name = 'find: ([^] 3)', func = mw.ustring.find,
	  args = { "¡fó0% bar", '¡[^%%]+' },
	  expect = { 1, 4 }
	},
	{ name = 'find: ($)', func = mw.ustring.find,
	  args = { "¡foo1 ¡foo2 ¡foo3", '¡foo[0-9]+$' },
	  expect = { 13, 17 }
	},
	{ name = 'find: (.*)', func = mw.ustring.find,
	  args = { "¡foo¡ ¡bar¡ baz", '¡.*¡' },
	  expect = { 1, 11 }
	},
	{ name = 'find: (.-)', func = mw.ustring.find,
	  args = { "¡foo¡ ¡bar¡ baz", '¡.-¡' },
	  expect = { 1, 5 }
	},
	{ name = 'find: plain', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '¡.¡', 1, true },
	  expect = { 5, 7 }
	},
	{ name = 'find: empty delimiter', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '' },
	  expect = { 1, 0 }
	},
	{ name = 'find: empty delimiter (2)', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '', 2 },
	  expect = { 2, 1 }
	},
	{ name = 'find: plain + empty delimiter', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '', 1, true },
	  expect = { 1, 0 }
	},
	{ name = 'find: plain + empty delimiter (2)', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '', 2, true },
	  expect = { 2, 1 }
	},
	{ name = 'find: excessive init', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '()', 20 },
	  expect = { 8, 7, 8 }
	},
	{ name = 'find: excessive init (2)', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '()', -20 },
	  expect = { 1, 0, 1 }
	},
	{ name = 'find: plain + excessive init', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '', 20, true },
	  expect = { 8, 7 }
	},
	{ name = 'find: plain + excessive init', func = mw.ustring.find,
	  args = { "¡a¡ ¡.¡", '', -20, true },
	  expect = { 1, 0 }
	},

	{ name = 'find: capture (1)', func = mw.ustring.find,
	  args = { "bar ¡foo bar", '(¡foo)' },
	  expect = { 5, 8, '¡foo' }
	},
	{ name = 'find: capture (2)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '(¡f%a+)' },
	  expect = { 5, 8, '¡fóo' }
	},
	{ name = 'find: capture (3)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '(¡f(%a)%a)' },
	  expect = { 5, 8, '¡fóo', 'ó' }
	},
	{ name = 'find: capture (4)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '(¡f(%a-)%a)' },
	  expect = { 5, 7, '¡fó', '' }
	},
	{ name = 'find: capture (5)', func = mw.ustring.find,
	  args = { "bar ¡fóo bar", '()(()¡f()(%a)()%a())()' },
	  expect = { 5, 8, 5, '¡fóo', 5, 7, 'ó', 8, 9, 9 }
	},
	{ name = 'find: capture (6)', func = mw.ustring.find,
	  args = { "fóó", "()(f)()(óó)()" },
	  expect = { 1, 3, 1, 'f', 2, 'óó', 4 }
	},
	{ name = 'find: capture (7)', func = mw.ustring.find,
	  args = { "fóó fóó", "()(f)()(óó)()", 2 },
	  expect = { 5, 7, 5, 'f', 6, 'óó', 8 }
	},
	{ name = 'find: (%1)', func = mw.ustring.find,
	  args = { "foo foofóó foófoó bar", '(f%a+)%1' },
	  expect = { 12, 17, 'foó' }
	},
	{ name = 'find: deceptively-simple pattern', func = mw.ustring.find,
	  args = { "fóó", '([^a-z])' },
	  expect = { 2, 2, 'ó' }
	},
	{ name = 'find: Bracket at start of a character set doesn\'t close', func = mw.ustring.find,
	  args = { "fóó", '()[]' },
	  expect = "Missing close-bracket for character set beginning at pattern character 3"
	},
	{ name = 'find: Bracket at start of a negated character set doesn\'t close', func = mw.ustring.find,
	  args = { "fóó", '()[^]' },
	  expect = "Missing close-bracket for character set beginning at pattern character 3"
	},
	{ name = 'find: Bracket at start of a character set is literal', func = mw.ustring.find,
	  args = { "foo]bar¿", '()([]])' },
	  expect = { 4, 4, 4, ']' }
	},
	{ name = 'find: Bracket at start of a negated character set is literal', func = mw.ustring.find,
	  args = { "]bar¿", '()([^]])' },
	  expect = { 2, 2, 2, 'b' }
	},
	{ name = 'find: Bracket at start of a character set can be a range endpoint', func = mw.ustring.find,
	  args = { "foo]bar¿", '()([]-z]+)' },
	  expect = { 1, 7, 1, 'foo]bar' }
	},
	{ name = 'find: Bracket at start of a negated character can be a range endpoint', func = mw.ustring.find,
	  args = { "fOO]bar¿", '()([^]-z]+)' },
	  expect = { 2, 3, 2, 'OO' }
	},
	{ name = 'find: Weird edge-case that was failing (1)', func = mw.ustring.find,
	  args = { "foo]ba-]r¿", '()([a]-%]+)' },
	  expect = { 4, 4, 4, ']' }
	},
	{ name = 'find: Weird edge-case that was failing (2)', func = mw.ustring.find,
	  args = { "foo¿", '()[!-%]' },
	  expect = "Missing close-bracket for character set beginning at pattern character 3"
	},
	{ name = 'find: Inverted range (1)', func = mw.ustring.find,
	  args = { "foo¿", '()([z-a]+)' },
	  expect = { nil }
	},
	{ name = 'find: Inverted range (2)', func = mw.ustring.find,
	  args = { "foo¿", '()([^z-a]+)' },
	  expect = { 1, 4, 1, 'foo¿' }
	},
	{ name = 'find: Inverted range (3)', func = mw.ustring.find,
	  args = { "foo¿", '()(f[z-a]o)' },
	  expect = { nil }
	},
	{ name = 'find: Inverted range (4)', func = mw.ustring.find,
	  args = { "foo¿", '()(f[z-a]*o)' },
	  expect = { 1, 2, 1, 'fo' }
	},

	{ name = 'match: (1)', func = mw.ustring.match,
	  args = { "bar fóo bar", 'f%a+' },
	  expect = { 'fóo' }
	},
	{ name = 'match: (2)', func = mw.ustring.match,
	  args = { "bar fóo bar", 'f(%a+)' },
	  expect = { 'óo' }
	},
	{ name = 'match: empty pattern', func = mw.ustring.match,
	  args = { "¡a¡ ¡.¡", '()' },
	  expect = { 1 }
	},
	{ name = 'match: empty pattern (2)', func = mw.ustring.match,
	  args = { "¡a¡ ¡.¡", '()', 2 },
	  expect = { 2 }
	},
	{ name = 'match: excessive init', func = mw.ustring.match,
	  args = { "¡a¡ ¡.¡", '()', 20 },
	  expect = { 8 }
	},
	{ name = 'match: excessive init (2)', func = mw.ustring.match,
	  args = { "¡a¡ ¡.¡", '()', -20 },
	  expect = { 1 }
	},

	{ name = 'gsub: (emtpy string, empty pattern)', func = mw.ustring.gsub,
	  args = { '', '', 'X' },
	  expect = { 'X', 1 }
	},
	{ name = 'gsub: (emtpy string, one char pattern)', func = mw.ustring.gsub,
	  args = { '', 'á', 'X' },
	  expect = { '', 0 }
	},
	{ name = 'gsub: (one char string, one char pattern)', func = mw.ustring.gsub,
	  args = { 'á', 'á', 'X' },
	  expect = { 'X', 1 }
	},
	{ name = 'gsub: (one char string, empty pattern)', func = mw.ustring.gsub,
	  args = { 'á', '', 'X' },
	  expect = { 'XáX', 2 }
	},
	{ name = 'gsub: (empty pattern with position captures)', func = mw.ustring.gsub,
	  args = { 'ábć', '()', '%1' },
	  expect = { '1á2b3ć4', 4 }
	},
	{ name = 'gsub: (limited to 1 replacement)', func = mw.ustring.gsub,
	  args = { 'áá', 'á', 'X', 1 },
	  expect = { 'Xá', 1 }
	},
	{ name = 'gsub: (limited to 0 replacements)', func = mw.ustring.gsub,
	  args = { 'áá', 'á', 'X', 0 },
	  expect = { 'áá', 0 }
	},
	{ name = 'gsub: (string 1)', func = mw.ustring.gsub,
	  args = { str2, 'f%a+', 'X' },
	  expect = { 'X bar X X baz X X X', 6 }
	},
	{ name = 'gsub: (string 2)', func = mw.ustring.gsub,
	  args = { str3, 'f%a+', 'X' },
	  expect = { '??? X bar X X baz X X X ok?', 6 }
	},
	{ name = 'gsub: (string 3)', func = mw.ustring.gsub,
	  args = { str2, 'f%a+', 'X', 3 },
	  expect = { 'X bar X X baz foooo foofoo fo', 3 }
	},
	{ name = 'gsub: (string 4)', func = mw.ustring.gsub,
	  args = { str3, 'f%a+', 'X', 3 },
	  expect = { '??? X bar X X baz foooo foofoo fo ok?', 3 }
	},
	{ name = 'gsub: (string 5)', func = mw.ustring.gsub,
	  args = { 'foo; fóó', '(f)(%a+)', '%%0=%0 %%1=%1 %%2=%2' },
	  expect = { '%0=foo %1=f %2=oo; %0=fóó %1=f %2=óó', 2 }
	},
	{ name = 'gsub: string, undocumented behavior where %1 works as %0 if there are no captures', func = mw.ustring.gsub,
	  args = { 'foo; fóó', '%a+', '%1!' },
	  expect = { 'foo!; fóó!', 2 }
	},
	{ name = 'gsub: (anchored)', func = mw.ustring.gsub,
	  args = { 'foofoofoo foo', '^foo', 'X' },
	  expect = { 'Xfoofoo foo', 1 }
	},
	{ name = 'gsub: (table 1)', func = mw.ustring.gsub,
	  args = { str2, 'f%a+', { foo = 'X', ['főó'] = 'Y', ['foó'] = 'Z' } },
	  expect = { 'X bar Y Z baz foooo foofoo fo', 6 }
	},
	{ name = 'gsub: (table 2)', func = mw.ustring.gsub,
	  args = { str3, 'f%a+', { foo = 'X', ['főó'] = 'Y', ['foó'] = 'Z' } },
	  expect = { '??? X bar Y Z baz foooo foofoo fo ok?', 6 }
	},
	{ name = 'gsub: (table 3)', func = mw.ustring.gsub,
	  args = { str2, 'f%a+', { ['főó'] = 'Y', ['foó'] = 'Z' }, 1 },
	  expect = { str2, 1 }
	},
	{ name = 'gsub: (table 4)', func = mw.ustring.gsub,
	  args = { str3, 'f(%a+)', { oo = 'X', ['őó'] = 'Y', ['oó'] = 'Z' } },
	  expect = { '??? X bar Y Z baz foooo foofoo fo ok?', 6 }
	},
	{ name = 'gsub: (table 5)', func = mw.ustring.gsub,
	  args = { str3, '(f)(%a+)', { f = 'F', oo = 'X', ['őó'] = 'Y', ['oó'] = 'Z' } },
	  expect = { '??? F bar F F baz F F F ok?', 6 }
	},
	{ name = 'gsub: (inverted zero character class)', func = mw.ustring.gsub,
	  args = { "ó", '%Z', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (single dot pattern at end)', func = mw.ustring.gsub,
	  args = { "ó", '.', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (single dot pattern at end + leading)', func = mw.ustring.gsub,
	  args = { 'fó', 'f.', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (dot pattern)', func = mw.ustring.gsub,
	  args = { 'f ó b', 'f . b', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (dot pattern with +)', func = mw.ustring.gsub,
	  args = { 'f óóó b', 'f .+ b', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (dot pattern with -)', func = mw.ustring.gsub,
	  args = { 'f óóó b', 'f .- b', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (dot pattern with *)', func = mw.ustring.gsub,
	  args = { 'f óóó b', 'f .* b', 'repl' },
	  expect = { 'repl', 1 }
	},
	{ name = 'gsub: (function 1)', func = mw.ustring.gsub,
	  args = { str2, 'f%a+', function(m) if m == 'fo' then return nil end return '-' .. mw.ustring.upper(m) .. '-' end },
	  expect = { '-FOO- bar -FŐÓ- -FOÓ- baz -FOOOO- -FOOFOO- fo', 6 }
	},
	{ name = 'gsub: (function 2)', func = mw.ustring.gsub,
	  args = { str3, 'f%a+', function(m) if m == 'fo' then return nil end return '-' .. mw.ustring.upper(m) .. '-' end },
	  expect = { '??? -FOO- bar -FŐÓ- -FOÓ- baz -FOOOO- -FOOFOO- fo ok?', 6 }
	},
	{ name = 'gsub: (function 3)', func = mw.ustring.gsub,
	  args = { str3, '(f)(%a+)', function(m1, m2) if m2 == 'o' then return nil end return '-' .. m1 .. mw.ustring.upper(m2) .. '-' end },
	  expect = { '??? -fOO- bar -fŐÓ- -fOÓ- baz -fOOOO- -fOOFOO- fo ok?', 6 }
	},
	{ name = 'gsub: invalid replacement string', func = mw.ustring.gsub,
	  args = { 'foo; fóó', '(%a+)', '%2' },
	  expect = "invalid capture index %2 in replacement string"
	},
	{ name = 'gsub: passing numbers instead of strings (1)', func = mw.ustring.gsub,
	  args = { 12345, '[3３]', '9' },
	  expect = { '12945', 1 }
	},
	{ name = 'gsub: passing numbers instead of strings (2)', func = mw.ustring.gsub,
	  args = { '12345', 3, '9' },
	  expect = { '12945', 1 }
	},
	{ name = 'gsub: passing numbers instead of strings (3)', func = mw.ustring.gsub,
	  args = { '12345', '[3３]', 9 },
	  expect = { '12945', 1 }
	},
	{ name = 'gsub: table replacement with a bad type (boolean)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', { b = true } },
	  expect = 'invalid replacement value (a boolean)'
	},
	{ name = 'gsub: table replacement with a bad type (table)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', { b = {} } },
	  expect = 'invalid replacement value (a table)'
	},
	{ name = 'gsub: table replacement with a bad type (function)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', { b = function () end } },
	  expect = 'invalid replacement value (a function)'
	},
	{ name = 'gsub: function replacement with a bad type (boolean)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', function () return true end },
	  expect = 'invalid replacement value (a boolean)'
	},
	{ name = 'gsub: function replacement with a bad type (table)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', function () return {} end },
	  expect = 'invalid replacement value (a table)'
	},
	{ name = 'gsub: function replacement with a bad type (function)', func = mw.ustring.gsub,
	  args = { 'abc', 'b', function () return function () end end },
	  expect = 'invalid replacement value (a function)'
	},

	{ name = 'gcodepoint: basic test', func = mw.ustring.gcodepoint,
	  args = { str1 },
	  expect = { { 0 }, { 0x7f }, { 0x80 }, { 0x7ff }, { 0x800 }, { 0xffff }, { 0x10000 }, { 0x10ffff } },
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: (4)', func = mw.ustring.gcodepoint,
	  args = { str1, 4 },
	  expect = { { 0x7ff }, { 0x800 }, { 0xffff }, { 0x10000 }, { 0x10ffff } },
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: (4, -2)', func = mw.ustring.gcodepoint,
	  args = { str1, 4, -2 },
	  expect = { { 0x7ff }, { 0x800 }, { 0xffff }, { 0x10000 } },
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: (4, 3)', func = mw.ustring.gcodepoint,
	  args = { str1, 4, 3 },
	  expect = {},
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: (1, 0)', func = mw.ustring.gcodepoint,
	  args = { str1, 1, 0 },
	  expect = {},
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: (9, 9)', func = mw.ustring.gcodepoint,
	  args = { str1, 9, 9 },
	  expect = {},
	  type = 'Iterator'
	},
	{ name = 'gcodepoint: really long string', func = testLongGcodepoint,
	  args = {},
	  expect = { {
		  [1] = 0x66, [2] = 0x151, [3] = 0xf3, [4] = 0x20,
		  [9997] = 0x66, [9998] = 0x151, [9999] = 0xf3, [10000] = 0x20,
	  } },
	},

	{ name = 'gmatch: test string 1', func = mw.ustring.gmatch,
	  args = { str2, 'f%a+' },
	  expect = { { 'foo' }, { 'főó' }, { 'foó' }, { 'foooo' }, { 'foofoo' }, { 'fo' } },
	  type = 'Iterator'
	},
	{ name = 'gmatch: test string 2', func = mw.ustring.gmatch,
	  args = { str3, 'f%a+' },
	  expect = { { 'foo' }, { 'főó' }, { 'foó' }, { 'foooo' }, { 'foofoo' }, { 'fo' } },
	  type = 'Iterator'
	},
	{ name = 'gmatch: anchored', func = mw.ustring.gmatch,
	  args = { "fóó1 ^fóó2 fóó3 ^fóó4", '^fóó%d+' },
	  expect = { { "^fóó2" }, { "^fóó4" } },
	  type = 'Iterator'
	},

	{ name = 'find: Pure-lua version, non-native error message', func = mw.ustring.find,
	  args = { "fóó", '[]' },
	  expect = "Missing close-bracket for character set beginning at pattern character 1"
	},
	{ name = 'match: Pure-lua version, non-native error message', func = mw.ustring.match,
	  args = { "fóó", '[]' },
	  expect = "Missing close-bracket for character set beginning at pattern character 1"
	},
	{ name = 'gsub: Pure-lua version, non-native error message', func = mw.ustring.gsub,
	  args = { "fóó", '[]', '' },
	  expect = "Missing close-bracket for character set beginning at pattern character 1"
	},

	{ name = 'string length limit',
	  func = function ()
		  local s = string.rep( "x", mw.ustring.maxStringLength + 1 )
		  local ret = { mw.ustring.gsub( s, 'a', 'b' ) }
		  -- So the output isn't insanely long
		  ret[1] = string.gsub( ret[1], 'xxxxx(x*)', function ( m )
			  return 'xxxxx[snip ' .. #m .. ' more]'
		  end )
		  return unpack( ret )
	  end,
	  expect = "bad argument #1 to 'gsub' (string is longer than " .. mw.ustring.maxStringLength .. " bytes)"
	},
	{ name = 'pattern length limit',
	  func = function ()
		  local pattern = string.rep( "x", mw.ustring.maxPatternLength + 1 )
		  return mw.ustring.gsub( 'a', pattern, 'b' )
	  end,
	  expect = "bad argument #2 to 'gsub' (pattern is longer than " .. mw.ustring.maxPatternLength .. " bytes)"
	},
} )
