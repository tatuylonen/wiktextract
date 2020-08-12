local ustring = {}

-- Copy these, just in case
local S = {
	byte = string.byte,
	char = string.char,
	len = string.len,
	sub = string.sub,
	find = string.find,
	match = string.match,
	gmatch = string.gmatch,
	gsub = string.gsub,
	format = string.format,
}

---- Configuration ----
-- To limit the length of strings or patterns processed, set these
ustring.maxStringLength = math.huge
ustring.maxPatternLength = math.huge

---- Utility functions ----

local function checkType( name, argidx, arg, expecttype, nilok )
	if arg == nil and nilok then
		return
	end
	if type( arg ) ~= expecttype then
		local msg = S.format( "bad argument #%d to '%s' (%s expected, got %s)",
			argidx, name, expecttype, type( arg )
		)
		error( msg, 3 )
	end
end

local function checkString( name, s )
	if type( s ) == 'number' then
		s = tostring( s )
	end
	if type( s ) ~= 'string' then
		local msg = S.format( "bad argument #1 to '%s' (string expected, got %s)",
			name, type( s )
		)
		error( msg, 3 )
	end
	if S.len( s ) > ustring.maxStringLength then
		local msg = S.format( "bad argument #1 to '%s' (string is longer than %d bytes)",
			name, ustring.maxStringLength
		)
		error( msg, 3 )
	end
end

local function checkPattern( name, pattern )
	if type( pattern ) == 'number' then
		pattern = tostring( pattern )
	end
	if type( pattern ) ~= 'string' then
		local msg = S.format( "bad argument #2 to '%s' (string expected, got %s)",
			name, type( pattern )
		)
		error( msg, 3 )
	end
	if S.len( pattern ) > ustring.maxPatternLength then
		local msg = S.format( "bad argument #2 to '%s' (pattern is longer than %d bytes)",
			name, ustring.maxPatternLength
		)
		error( msg, 3 )
	end
end

-- A private helper that splits a string into codepoints, and also collects the
-- starting position of each character and the total length in codepoints.
--
-- @param s string  utf8-encoded string to decode
-- @return table
local function utf8_explode( s )
	local ret = {
		len = 0,
		codepoints = {},
		bytepos = {},
	}

	local i = 1
	local l = S.len( s )
	local cp, b, b2, trail
	local min
	while i <= l do
		b = S.byte( s, i )
		if b < 0x80 then
			-- 1-byte code point, 00-7F
			cp = b
			trail = 0
			min = 0
		elseif b < 0xc2 then
			-- Either a non-initial code point (invalid here) or
			-- an overlong encoding for a 1-byte code point
			return nil
		elseif b < 0xe0 then
			-- 2-byte code point, C2-DF
			trail = 1
			cp = b - 0xc0
			min = 0x80
		elseif b < 0xf0 then
			-- 3-byte code point, E0-EF
			trail = 2
			cp = b - 0xe0
			min = 0x800
		elseif b < 0xf4 then
			-- 4-byte code point, F0-F3
			trail = 3
			cp = b - 0xf0
			min = 0x10000
		elseif b == 0xf4 then
			-- 4-byte code point, F4
			-- Make sure it doesn't decode to over U+10FFFF
			if S.byte( s, i + 1 ) > 0x8f then
				return nil
			end
			trail = 3
			cp = 4
			min = 0x100000
		else
			-- Code point over U+10FFFF, or invalid byte
			return nil
		end

		-- Check subsequent bytes for multibyte code points
		for j = i + 1, i + trail do
			b = S.byte( s, j )
			if not b or b < 0x80 or b > 0xbf then
				return nil
			end
			cp = cp * 0x40 + b - 0x80
		end
		if cp < min then
			-- Overlong encoding
			return nil
		end

		ret.codepoints[#ret.codepoints + 1] = cp
		ret.bytepos[#ret.bytepos + 1] = i
		ret.len = ret.len + 1
		i = i + 1 + trail
	end

	-- Two past the end (for sub with empty string)
	ret.bytepos[#ret.bytepos + 1] = l + 1
	ret.bytepos[#ret.bytepos + 1] = l + 1

	return ret
end

-- A private helper that finds the character offset for a byte offset.
--
-- @param cps table  from utf8_explode
-- @param i int  byte offset
-- @return int
local function cpoffset( cps, i )
	local min, max, p = 0, cps.len + 1
	if i == 0 then
		return 0
	end
	while min + 1 < max do
		p = math.floor( ( min + max ) / 2 ) + 1
		if cps.bytepos[p] <= i then
			min = p - 1
		end
		if cps.bytepos[p] >= i then
			max = p - 1
		end
	end
	return min + 1
end

---- Trivial functions ----
-- These functions are the same as the standard string versions

ustring.byte = string.byte
ustring.format = string.format
ustring.rep = string.rep

---- Non-trivial functions ----
-- These functions actually have to be UTF-8 aware


-- Determine if a string is valid UTF-8
--
-- @param s string
-- @return boolean
function ustring.isutf8( s )
	checkString( 'isutf8', s )
	return utf8_explode( s ) ~= nil
end

-- Return the byte offset of a character in a string
--
-- @param s string
-- @param l int  codepoint number [default 1]
-- @param i int  starting byte offset [default 1]
-- @return int|nil
function ustring.byteoffset( s, l, i )
	checkString( 'byteoffset', s )
	checkType( 'byteoffset', 2, l, 'number', true )
	checkType( 'byteoffset', 3, i, 'number', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'byteoffset' (string is not UTF-8)", 2 )
	end

	i = i or 1
	if i < 0 then
		i = S.len( s ) + i + 1
	end
	if i < 1 or i > S.len( s ) then
		return nil
	end
	local p = cpoffset( cps, i )
	if l > 0 and cps.bytepos[p] == i then
		l = l - 1
	end
	if p + l > cps.len then
		return nil
	end
	return cps.bytepos[p + l]
end

-- Return codepoints from a string
--
-- @see string.byte
-- @param s string
-- @param i int  Starting character [default 1]
-- @param j int  Ending character [default i]
-- @return int*  Zero or more codepoints
function ustring.codepoint( s, i, j )
	checkString( 'codepoint', s )
	checkType( 'codepoint', 2, i, 'number', true )
	checkType( 'codepoint', 3, j, 'number', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'codepoint' (string is not UTF-8)", 2 )
	end
	i = i or 1
	if i < 0 then
		i = cps.len + i + 1
	end
	j = j or i
	if j < 0 then
		j = cps.len + j + 1
	end
	if j < i then
		return -- empty result set
	end
	i = math.max( 1, math.min( i, cps.len + 1 ) )
	j = math.max( 1, math.min( j, cps.len + 1 ) )
	return unpack( cps.codepoints, i, j )
end

-- Return an iterator over the codepoint (as integers)
--   for cp in ustring.gcodepoint( s ) do ... end
--
-- @param s string
-- @param i int  Starting character [default 1]
-- @param j int  Ending character [default -1]
-- @return function
-- @return nil
-- @return nil
function ustring.gcodepoint( s, i, j )
	checkString( 'gcodepoint', s )
	checkType( 'gcodepoint', 2, i, 'number', true )
	checkType( 'gcodepoint', 3, j, 'number', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'gcodepoint' (string is not UTF-8)", 2 )
	end
	i = i or 1
	if i < 0 then
		i = cps.len + i + 1
	end
	j = j or -1
	if j < 0 then
		j = cps.len + j + 1
	end
	if j < i then
		return function ()
			return nil
		end
	end
	i = math.max( 1, math.min( i, cps.len + 1 ) )
	j = math.max( 1, math.min( j, cps.len + 1 ) )
	return function ()
		if i <= j then
			local ret = cps.codepoints[i]
			i = i + 1
			return ret
		end
		return nil
	end
end

-- Convert codepoints to a string
--
-- @see string.char
-- @param ... int  List of codepoints
-- @return string
local function internalChar( t, s, e )
	local ret = {}
	for i = s, e do
		local v = t[i]
		if type( v ) ~= 'number' then
			checkType( 'char', i, v, 'number' )
		end
		v = math.floor( v )
		if v < 0 or v > 0x10ffff then
			error( S.format( "bad argument #%d to 'char' (value out of range)", i ), 2 )
		elseif v < 0x80 then
			ret[#ret + 1] = v
		elseif v < 0x800 then
			ret[#ret + 1] = 0xc0 + math.floor( v / 0x40 ) % 0x20
			ret[#ret + 1] = 0x80 + v % 0x40
		elseif v < 0x10000 then
			ret[#ret + 1] = 0xe0 + math.floor( v / 0x1000 ) % 0x10
			ret[#ret + 1] = 0x80 + math.floor( v / 0x40 ) % 0x40
			ret[#ret + 1] = 0x80 + v % 0x40
		else
			ret[#ret + 1] = 0xf0 + math.floor( v / 0x40000 ) % 0x08
			ret[#ret + 1] = 0x80 + math.floor( v / 0x1000 ) % 0x40
			ret[#ret + 1] = 0x80 + math.floor( v / 0x40 ) % 0x40
			ret[#ret + 1] = 0x80 + v % 0x40
		end
	end
	return S.char( unpack( ret ) )
end
function ustring.char( ... )
	return internalChar( { ... }, 1, select( '#', ... ) )
end

-- Return the length of a string in codepoints, or
-- nil if the string is not valid UTF-8.
--
-- @see string.len
-- @param string
-- @return int|nil
function ustring.len( s )
	checkString( 'len', s )
	local cps = utf8_explode( s )
	if cps == nil then
		return nil
	else
		return cps.len
	end
end

-- Private function to return a substring of a string
--
-- @param s string
-- @param cps table  Exploded string
-- @param i int  Starting character [default 1]
-- @param j int  Ending character [default -1]
-- @return string
local function sub( s, cps, i, j )
	return S.sub( s, cps.bytepos[i], cps.bytepos[j+1] - 1 )
end

-- Return a substring of a string
--
-- @see string.sub
-- @param s string
-- @param i int  Starting character [default 1]
-- @param j int  Ending character [default -1]
-- @return string
function ustring.sub( s, i, j )
	checkString( 'sub', s )
	checkType( 'sub', 2, i, 'number', true )
	checkType( 'sub', 3, j, 'number', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'sub' (string is not UTF-8)", 2 )
	end
	i = i or 1
	if i < 0 then
		i = cps.len + i + 1
	end
	j = j or -1
	if j < 0 then
		j = cps.len + j + 1
	end
	if j < i then
		return ''
	end
	i = math.max( 1, math.min( i, cps.len + 1 ) )
	j = math.max( 1, math.min( j, cps.len + 1 ) )
	return sub( s, cps, i, j )
end

---- Table-driven functions ----
-- These functions load a conversion table when called

-- Convert a string to uppercase
--
-- @see string.upper
-- @param s string
-- @return string
function ustring.upper( s )
	checkString( 'upper', s )
	local map = require 'ustring/upper';
	local ret = S.gsub( s, '([^\128-\191][\128-\191]*)', map )
	return ret
end

-- Convert a string to lowercase
--
-- @see string.lower
-- @param s string
-- @return string
function ustring.lower( s )
	checkString( 'lower', s )
	local map = require 'ustring/lower';
	local ret = S.gsub( s, '([^\128-\191][\128-\191]*)', map )
	return ret
end

---- Pattern functions ----
-- Ugh. Just ugh.

-- Cache for character sets (e.g. [a-z])
local charset_cache = {}
setmetatable( charset_cache, { __weak = 'kv' } )

-- Private function to find a pattern in a string
-- Yes, this basically reimplements the whole of Lua's pattern matching, in
-- Lua.
--
-- @see ustring.find
-- @param s string
-- @param cps table  Exploded string
-- @param rawpat string  Pattern
-- @param pattern table  Exploded pattern
-- @param init int  Starting index
-- @param noAnchor boolean  True to ignore '^'
-- @return int starting index of the match
-- @return int ending index of the match
-- @return string|int* captures
local function find( s, cps, rawpat, pattern, init, noAnchor )
	local charsets = require 'ustring/charsets'
	local anchor = false
	local ncapt, captures
	local captparen = {}

	-- Extract the value of a capture from the
	-- upvalues ncapt and capture.
	local function getcapt( n, err, errl )
		if n > ncapt then
			error( err, errl + 1 )
		elseif type( captures[n] ) == 'table' then
			if captures[n][2] == '' then
				error( err, errl + 1 )
			end
			return sub( s, cps, captures[n][1], captures[n][2] ), captures[n][2] - captures[n][1] + 1
		else
			return captures[n], math.floor( math.log10( captures[n] ) ) + 1
		end
	end

	local match, match_charset, parse_charset

	-- Main matching function. Uses tail recursion where possible.
	-- Returns the position of the character after the match, and updates the
	-- upvalues ncapt and captures.
	match = function ( sp, pp )
		local c = pattern.codepoints[pp]
		if c == 0x28 then -- '(': starts capture group
			ncapt = ncapt + 1
			captparen[ncapt] = pp
			local ret
			if pattern.codepoints[pp + 1] == 0x29 then -- ')': Pattern is '()', capture position
				captures[ncapt] = sp
				ret = match( sp, pp + 2 )
			else
				-- Start capture group
				captures[ncapt] = { sp, '' }
				ret = match( sp, pp + 1 )
			end
			if ret then
				return ret
			else
				-- Failed, rollback
				ncapt = ncapt - 1
				return nil
			end
		elseif c == 0x29 then -- ')': ends capture group, pop current capture index from stack
			for n = ncapt, 1, -1 do
				if type( captures[n] ) == 'table' and captures[n][2] == '' then
					captures[n][2] = sp - 1
					local ret = match( sp, pp + 1 )
					if ret then
						return ret
					else
						-- Failed, rollback
						captures[n][2] = ''
						return nil
					end
				end
			end
			error( 'Unmatched close-paren at pattern character ' .. pp, 3 )
		elseif c == 0x5b then -- '[': starts character set
			return match_charset( sp, parse_charset( pp ) )
		elseif c == 0x5d then -- ']'
			error( 'Unmatched close-bracket at pattern character ' .. pp, 3 )
		elseif c == 0x25 then -- '%'
			c = pattern.codepoints[pp + 1]
			if charsets[c] then -- A character set like '%a'
				return match_charset( sp, pp + 2, charsets[c] )
			elseif c == 0x62 then -- '%b': balanced delimiter match
				local d1 = pattern.codepoints[pp + 2]
				local d2 = pattern.codepoints[pp + 3]
				if not d1 or not d2 then
					error( 'malformed pattern (missing arguments to \'%b\')', 3 )
				end
				if cps.codepoints[sp] ~= d1 then
					return nil
				end
				sp = sp + 1
				local ct = 1
				while true do
					c = cps.codepoints[sp]
					sp = sp + 1
					if not c then
						return nil
					elseif c == d2 then
						if ct == 1 then
							return match( sp, pp + 4 )
						end
						ct = ct - 1
					elseif c == d1 then
						ct = ct + 1
					end
				end
			elseif c == 0x66 then -- '%f': frontier pattern match
				if pattern.codepoints[pp + 2] ~= 0x5b then
					error( 'missing \'[\' after %f in pattern at pattern character ' .. pp, 3 )
				end
				local pp, charset = parse_charset( pp + 2 )
				local c1 = cps.codepoints[sp - 1] or 0
				local c2 = cps.codepoints[sp] or 0
				if not charset[c1] and charset[c2] then
					return match( sp, pp )
				else
					return nil
				end
			elseif c >= 0x30 and c <= 0x39 then -- '%0' to '%9': backreference
				local m, l = getcapt( c - 0x30, 'invalid capture index %' .. c .. ' at pattern character ' .. pp, 3 )
				local ep = math.min( cps.len + 1, sp + l )
				if sub( s, cps, sp, ep - 1 ) == m then
					return match( ep, pp + 2 )
				else
					return nil
				end
			elseif not c then -- percent at the end of the pattern
				error( 'malformed pattern (ends with \'%\')', 3 )
			else -- something else, treat as a literal
				return match_charset( sp, pp + 2, { [c] = 1 } )
			end
		elseif c == 0x2e then -- '.': match anything
			if not charset_cache['.'] then
				local t = {}
				setmetatable( t, { __index = function ( t, k ) return k end } )
				charset_cache['.'] = { 1, t }
			end
			return match_charset( sp, pp + 1, charset_cache['.'][2] )
		elseif c == nil then -- end of pattern
			return sp
		elseif c == 0x24 and pattern.len == pp then -- '$': assert end of string
			return ( sp == cps.len + 1 ) and sp or nil
		else
			-- Any other character matches itself
			return match_charset( sp, pp + 1, { [c] = 1 } )
		end
	end

	-- Parse a bracketed character set (e.g. [a-z])
	-- Returns the position after the set and a table holding the matching characters
	parse_charset = function ( pp )
		local _, ep
		local epp = pattern.bytepos[pp] + 1
		if S.sub( rawpat, epp, epp ) == '^' then
			epp = epp + 1
		end
		if S.sub( rawpat, epp, epp ) == ']' then
			-- Lua's string module effectively does this
			epp = epp + 1
		end
		repeat
			_, ep = S.find( rawpat, ']', epp, true )
			if not ep then
				error( 'Missing close-bracket for character set beginning at pattern character ' .. pp, 3 )
			end
			epp = ep + 1
		until S.byte( rawpat, ep - 1 ) ~= 0x25 or S.byte( rawpat, ep - 2 ) == 0x25
		local key = S.sub( rawpat, pattern.bytepos[pp], ep )
		if charset_cache[key] then
			local pl, cs = unpack( charset_cache[key] )
			return pp + pl, cs
		end

		local p0 = pp
		local cs = {}
		local csrefs = { cs }
		local invert = false
		pp = pp + 1
		if pattern.codepoints[pp] == 0x5e then -- '^'
			invert = true
			pp = pp + 1
		end
		local first = true
		while true do
			local c = pattern.codepoints[pp]
			if not first and c == 0x5d then -- closing ']'
				pp = pp + 1
				break
			elseif c == 0x25 then -- '%'
				c = pattern.codepoints[pp + 1]
				if charsets[c] then
					csrefs[#csrefs + 1] = charsets[c]
				else
					cs[c] = 1
				end
				pp = pp + 2
			elseif pattern.codepoints[pp + 1] == 0x2d and pattern.codepoints[pp + 2] and pattern.codepoints[pp + 2] ~= 0x5d then -- '-' followed by another char (not ']'), it's a range
				for i = c, pattern.codepoints[pp + 2] do
					cs[i] = 1
				end
				pp = pp + 3
			elseif not c then -- Should never get here, but Just In Case...
				error( 'Missing close-bracket', 3 )
			else
				cs[c] = 1
				pp = pp + 1
			end
			first = false
		end

		local ret
		if not csrefs[2] then
			if not invert then
				-- If there's only the one charset table, we can use it directly
				ret = cs
			else
				-- Simple invert
				ret = {}
				setmetatable( ret, { __index = function ( t, k ) return k and not cs[k] end } )
			end
		else
			-- Ok, we have to iterate over multiple charset tables
			ret = {}
			setmetatable( ret, { __index = function ( t, k )
				if not k then
					return nil
				end
				for i = 1, #csrefs do
					if csrefs[i][k] then
						return not invert
					end
				end
				return invert
			end } )
		end

		charset_cache[key] = { pp - p0, ret }
		return pp, ret
	end

	-- Match a character set table with optional quantifier, followed by
	-- the rest of the pattern.
	-- Returns same as 'match' above.
	match_charset = function ( sp, pp, charset )
		local q = pattern.codepoints[pp]
		if q == 0x2a then -- '*', 0 or more matches
			pp = pp + 1
			local i = 0
			while charset[cps.codepoints[sp + i]] do
				i = i + 1
			end
			while i >= 0 do
				local ret = match( sp + i, pp )
				if ret then
					return ret
				end
				i = i - 1
			end
			return nil
		elseif q == 0x2b then -- '+', 1 or more matches
			pp = pp + 1
			local i = 0
			while charset[cps.codepoints[sp + i]] do
				i = i + 1
			end
			while i > 0 do
				local ret = match( sp + i, pp )
				if ret then
					return ret
				end
				i = i - 1
			end
			return nil
		elseif q == 0x2d then -- '-', 0 or more matches non-greedy
			pp = pp + 1
			while true do
				local ret = match( sp, pp )
				if ret then
					return ret
				end
				if not charset[cps.codepoints[sp]] then
					return nil
				end
				sp = sp + 1
			end
		elseif q == 0x3f then -- '?', 0 or 1 match
			pp = pp + 1
			if charset[cps.codepoints[sp]] then
				local ret = match( sp + 1, pp )
				if ret then
					return ret
				end
			end
			return match( sp, pp )
		else -- no suffix, must match 1
			if charset[cps.codepoints[sp]] then
				return match( sp + 1, pp )
			else
				return nil
			end
		end
	end

	init = init or 1
	if init < 0 then
		init = cps.len + init + 1
	end
	init = math.max( 1, math.min( init, cps.len + 1 ) )

	-- Here is the actual match loop. It just calls 'match' on successive
	-- starting positions (or not, if the pattern is anchored) until it finds a
	-- match.
	local sp = init
	local pp = 1
	if not noAnchor and pattern.codepoints[1] == 0x5e then -- '^': Pattern is anchored
		anchor = true
		pp = 2
	end

	repeat
		ncapt, captures = 0, {}
		local ep = match( sp, pp )
		if ep then
			for i = 1, ncapt do
				captures[i] = getcapt( i, 'Unclosed capture beginning at pattern character ' .. captparen[i], 2 )
			end
			return sp, ep - 1, unpack( captures )
		end
		sp = sp + 1
	until anchor or sp > cps.len + 1
	return nil
end

-- Private function to decide if a pattern looks simple enough to use
-- Lua's built-in string library. The following make a pattern not simple:
--  * If it contains any bytes over 0x7f. We could skip these if they're not
--    inside brackets and aren't followed by quantifiers and aren't part of a
--    '%b', but that's too complicated to check.
--  * If it contains a negated character set.
--  * If it contains "%a" or any of the other %-prefixed character sets except %z.
--  * If it contains a '.' not followed by '*', '+', '-'. A bare '.' or '.?'
--    matches a partial UTF-8 character, but the others will happily enough
--    match a whole UTF-8 character thinking it's 2, 3 or 4.
--  * If it contains position-captures.
--  * If it matches the empty string
--
-- @param string pattern
-- @return boolean
local function patternIsSimple( pattern )
	local findWithPcall = function ( ... )
		local ok, ret = pcall( S.find, ... )
		return ok and ret
	end

	return not (
		S.find( pattern, '[\128-\255]' ) or
		S.find( pattern, '%[%^' ) or
		S.find( pattern, '%%[acdlpsuwxACDLPSUWXZ]' ) or
		S.find( pattern, '%.[^*+-]' ) or S.find( pattern, '%.$' ) or
		S.find( pattern, '()', 1, true ) or
		pattern == '' or findWithPcall( '', pattern )
	)
end

-- Find a pattern in a string
--
-- This works just like string.find, with the following changes:
--  * Everything works on UTF-8 characters rather than bytes
--  * Character classes are redefined in terms of Unicode properties:
--    * %a - Letter
--    * %c - Control
--    * %d - Decimal Number
--    * %l - Lower case letter
--    * %p - Punctuation
--    * %s - Separator, plus HT, LF, FF, CR, and VT
--    * %u - Upper case letter
--    * %w - Letter or Decimal Number
--    * %x - [0-9A-Fa-f０-９Ａ-Ｆａ-ｆ]
--
-- @see string.find
-- @param s string
-- @param pattern string  Pattern
-- @param init int  Starting index
-- @param plain boolean  Literal match, no pattern matching
-- @return int starting index of the match
-- @return int ending index of the match
-- @return string|int* captures
function ustring.find( s, pattern, init, plain )
	checkString( 'find', s )
	checkPattern( 'find', pattern )
	checkType( 'find', 3, init, 'number', true )
	checkType( 'find', 4, plain, 'boolean', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'find' (string is not UTF-8)", 2 )
	end
	local pat = utf8_explode( pattern )
	if pat == nil then
		error( "bad argument #2 for 'find' (string is not UTF-8)", 2 )
	end

	if plain or patternIsSimple( pattern ) then
		if init and init > cps.len + 1 then
			init = cps.len + 1
		end
		local m
		if plain then
			m = { true, S.find( s, pattern, cps.bytepos[init], plain ) }
		else
			m = { pcall( S.find, s, pattern, cps.bytepos[init], plain ) }
		end
		if m[1] then
			if m[2] then
				m[2] = cpoffset( cps, m[2] )
				m[3] = cpoffset( cps, m[3] )
			end
			return unpack( m, 2 )
		end
	end

	return find( s, cps, pattern, pat, init )
end

-- Match a string against a pattern
--
-- @see ustring.find
-- @see string.match
-- @param s string
-- @param pattern string
-- @param init int Starting offset for match
-- @return string|int* captures, or the whole match if there are none
function ustring.match( s, pattern, init )
	checkString( 'match', s )
	checkPattern( 'match', pattern )
	checkType( 'match', 3, init, 'number', true )
	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'match' (string is not UTF-8)", 2 )
	end
	local pat = utf8_explode( pattern )
	if pat == nil then
		error( "bad argument #2 for 'match' (string is not UTF-8)", 2 )
	end

	if patternIsSimple( pattern ) then
		local ret = { pcall( S.match, s, pattern, cps.bytepos[init] ) }
		if ret[1] then
			return unpack( ret, 2 )
		end
	end

	local m = { find( s, cps, pattern, pat, init ) }
	if not m[1] then
		return nil
	end
	if m[3] then
		return unpack( m, 3 )
	end
	return sub( s, cps, m[1], m[2] )
end

-- Return an iterator function over the matches for a pattern
--
-- @see ustring.find
-- @see string.gmatch
-- @param s string
-- @param pattern string
-- @return function
-- @return nil
-- @return nil
function ustring.gmatch( s, pattern )
	checkString( 'gmatch', s )
	checkPattern( 'gmatch', pattern )
	if patternIsSimple( pattern ) then
		local ret = { pcall( S.gmatch, s, pattern ) }
		if ret[1] then
			return unpack( ret, 2 )
		end
	end

	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'gmatch' (string is not UTF-8)", 2 )
	end
	local pat = utf8_explode( pattern )
	if pat == nil then
		error( "bad argument #2 for 'gmatch' (string is not UTF-8)", 2 )
	end
	local init = 1

	return function ()
		local m = { find( s, cps, pattern, pat, init, true ) }
		if not m[1] then
			return nil
		end
		init = m[2] + 1
		if m[3] then
			return unpack( m, 3 )
		end
		return sub( s, cps, m[1], m[2] )
	end
end

-- Replace pattern matches in a string
--
-- @see ustring.find
-- @see string.gsub
-- @param s string
-- @param pattern string
-- @param repl string|function|table
-- @param int n
-- @return string
-- @return int
function ustring.gsub( s, pattern, repl, n )
	checkString( 'gsub', s )
	checkPattern( 'gsub', pattern )
	checkType( 'gsub', 4, n, 'number', true )
	if patternIsSimple( pattern ) then
		local ret = { pcall( S.gsub, s, pattern, repl, n ) }
		if ret[1] then
			return unpack( ret, 2 )
		end
	end

	if n == nil then
		n = 1e100
	end
	if n < 1 then
		-- No replacement
		return s, 0
	end

	local cps = utf8_explode( s )
	if cps == nil then
		error( "bad argument #1 for 'gsub' (string is not UTF-8)", 2 )
	end
	local pat = utf8_explode( pattern )
	if pat == nil then
		error( "bad argument #2 for 'gsub' (string is not UTF-8)", 2 )
	end

	if pat.codepoints[1] == 0x5e then -- '^': Pattern is anchored
		-- There can be only the one match, so make that explicit
		n = 1
	end

	local tp
	if type( repl ) == 'function' then
		tp = 1
	elseif type( repl ) == 'table' then
		tp = 2
	elseif type( repl ) == 'string' then
		tp = 3
	elseif type( repl ) == 'number' then
		repl = tostring( repl )
		tp = 3
	else
		checkType( 'gsub', 3, repl, 'function or table or string' )
	end

	local init = 1
	local ct = 0
	local ret = {}
	local zeroAdjustment = 0
	repeat
		local m = { find( s, cps, pattern, pat, init + zeroAdjustment ) }
		if not m[1] then
			break
		end
		if init < m[1] then
			ret[#ret + 1] = sub( s, cps, init, m[1] - 1 )
		end
		local mm = sub( s, cps, m[1], m[2] )

		-- This simplifies the code for the function and table cases (tp == 1 and tp == 2) when there are
		-- no captures in the pattern. As documented it would be incorrect for the string case by making
		-- %1 act like %0 instead of raising an "invalid capture index" error, but Lua in fact does
		-- exactly that for string.gsub.
		if #m < 3 then
			m[3] = mm
		end

		local val, valType
		if tp == 1 then
			val = repl( unpack( m, 3 ) )
		elseif tp == 2 then
			val = repl[m[3]]
		elseif tp == 3 then
			if ct == 0 and #m < 11 then
				local ss = S.gsub( repl, '%%[%%0-' .. ( #m - 2 ) .. ']', 'x' )
				ss = S.match( ss, '%%[0-9]' )
				if ss then
					error( 'invalid capture index ' .. ss .. ' in replacement string', 2 )
				end
			end
			local t = {
				["%0"] = mm,
				["%1"] = m[3],
				["%2"] = m[4],
				["%3"] = m[5],
				["%4"] = m[6],
				["%5"] = m[7],
				["%6"] = m[8],
				["%7"] = m[9],
				["%8"] = m[10],
				["%9"] = m[11],
				["%%"] = "%"
			}
			val = S.gsub( repl, '%%[%%0-9]', t )
		end
		valType = type( val )
		if valType ~= 'nil' and valType ~= 'string' and valType ~= 'number' then
			error( 'invalid replacement value (a ' .. valType .. ')', 2 )
		end
		ret[#ret + 1] = val or mm
		init = m[2] + 1
		ct = ct + 1
		zeroAdjustment = m[2] < m[1] and 1 or 0
	until init > cps.len or ct >= n
	if init <= cps.len then
		ret[#ret + 1] = sub( s, cps, init, cps.len )
	end
	return table.concat( ret ), ct
end

---- Unicode Normalization ----
-- These functions load a conversion table when called

local function internalDecompose( cps, decomp )
	local cp = {}
	local normal = require 'ustring/normalization-data'

	-- Decompose into cp, using the lookup table and logic for hangul
	for i = 1, cps.len do
		local c = cps.codepoints[i]
		local m = decomp[c]
		if m then
			for j = 0, #m do
				cp[#cp + 1] = m[j]
			end
		else
			cp[#cp + 1] = c
		end
	end

	-- Now sort combiners by class
	local i, l = 1, #cp
	while i < l do
		local cc1 = normal.combclass[cp[i]]
		local cc2 = normal.combclass[cp[i+1]]
		if cc1 and cc2 and cc1 > cc2 then
			cp[i], cp[i+1] = cp[i+1], cp[i]
			if i > 1 then
				i = i - 1
			else
				i = i + 1
			end
		else
			i = i + 1
		end
	end

	return cp, 1, l
end

local function internalCompose( cp, _, l )
	local normal = require 'ustring/normalization-data'

	-- Since NFD->NFC can never expand a character sequence, we can do this
	-- in-place.
	local comp = normal.comp[cp[1]]
	local sc = 1
	local j = 1
	local lastclass = 0
	for i = 2, l do
		local c = cp[i]
		local ccc = normal.combclass[c]
		if ccc then
			-- Trying a combiner with the starter
			if comp and lastclass < ccc and comp[c] then
				-- Yes!
				c = comp[c]
				cp[sc] = c
				comp = normal.comp[c]
			else
				-- No, copy it to the right place for output
				j = j + 1
				cp[j] = c
				lastclass = ccc
			end
		elseif comp and lastclass == 0 and comp[c] then
			-- Combining two adjacent starters
			c = comp[c]
			cp[sc] = c
			comp = normal.comp[c]
		else
			-- New starter, doesn't combine
			j = j + 1
			cp[j] = c
			comp = normal.comp[c]
			sc = j
			lastclass = 0
		end
	end

	return cp, 1, j
end

-- Normalize a string to NFC
--
-- Based on MediaWiki's UtfNormal class. Returns nil if the string is not valid
-- UTF-8.
--
-- @param s string
-- @return string|nil
function ustring.toNFC( s )
	checkString( 'toNFC', s )

	-- ASCII is always NFC
	if not S.find( s, '[\128-\255]' ) then
		return s
	end

	local cps = utf8_explode( s )
	if cps == nil then
		return nil
	end
	local normal = require 'ustring/normalization-data'

	-- First, scan through to see if the string is definitely already NFC
	local ok = true
	for i = 1, cps.len do
		local c = cps.codepoints[i]
		if normal.check[c] then
			ok = false
			break
		end
	end
	if ok then
		return s
	end

	-- Next, expand to NFD then recompose
	return internalChar( internalCompose( internalDecompose( cps, normal.decomp ) ) )
end

-- Normalize a string to NFD
--
-- Based on MediaWiki's UtfNormal class. Returns nil if the string is not valid
-- UTF-8.
--
-- @param s string
-- @return string|nil
function ustring.toNFD( s )
	checkString( 'toNFD', s )

	-- ASCII is always NFD
	if not S.find( s, '[\128-\255]' ) then
		return s
	end

	local cps = utf8_explode( s )
	if cps == nil then
		return nil
	end

	local normal = require 'ustring/normalization-data'
	return internalChar( internalDecompose( cps, normal.decomp ) )
end

-- Normalize a string to NFKC
--
-- Based on MediaWiki's UtfNormal class. Returns nil if the string is not valid
-- UTF-8.
--
-- @param s string
-- @return string|nil
function ustring.toNFKC( s )
	checkString( 'toNFKC', s )

	-- ASCII is always NFKC
	if not S.find( s, '[\128-\255]' ) then
		return s
	end

	local cps = utf8_explode( s )
	if cps == nil then
		return nil
	end
	local normal = require 'ustring/normalization-data'

	-- Next, expand to NFKD then recompose
	return internalChar( internalCompose( internalDecompose( cps, normal.decompK ) ) )
end

-- Normalize a string to NFKD
--
-- Based on MediaWiki's UtfNormal class. Returns nil if the string is not valid
-- UTF-8.
--
-- @param s string
-- @return string|nil
function ustring.toNFKD( s )
	checkString( 'toNFKD', s )

	-- ASCII is always NFKD
	if not S.find( s, '[\128-\255]' ) then
		return s
	end

	local cps = utf8_explode( s )
	if cps == nil then
		return nil
	end

	local normal = require 'ustring/normalization-data'
	return internalChar( internalDecompose( cps, normal.decompK ) )
end

return ustring
