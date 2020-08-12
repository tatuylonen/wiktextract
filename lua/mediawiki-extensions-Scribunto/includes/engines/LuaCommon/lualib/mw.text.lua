local mwtext = {}
local php
local options

local util = require 'libraryUtil'
local checkType = util.checkType
local checkTypeForNamedArg = util.checkTypeForNamedArg

function mwtext.setupInterface( opts )
	-- Boilerplate
	mwtext.setupInterface = nil
	php = mw_interface
	mw_interface = nil
	options = opts

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.text = mwtext

	package.loaded['mw.text'] = mwtext
end

function mwtext.trim( s, charset )
	charset = charset or '\t\r\n\f '
	s = mw.ustring.gsub( s, '^[' .. charset .. ']*(.-)[' .. charset .. ']*$', '%1' )
	return s
end

local htmlencode_map = {
	['>'] = '&gt;',
	['<'] = '&lt;',
	['&'] = '&amp;',
	['"'] = '&quot;',
	["'"] = '&#039;',
	['\194\160'] = '&nbsp;',
}
local htmldecode_map = {}
for k, v in pairs( htmlencode_map ) do
	htmldecode_map[v] = k
end
local decode_named_entities = nil

function mwtext.encode( s, charset )
	charset = charset or '<>&"\'\194\160'
	s = mw.ustring.gsub( s, '[' .. charset .. ']', function ( m )
		if not htmlencode_map[m] then
			local e = string.format( '&#%d;', mw.ustring.codepoint( m ) )
			htmlencode_map[m] = e
			htmldecode_map[e] = m
		end
		return htmlencode_map[m]
	end )
	return s
end

function mwtext.decode( s, decodeNamedEntities )
	local dec
	if decodeNamedEntities then
		if decode_named_entities == nil then
			decode_named_entities = php.getEntityTable()
			setmetatable( decode_named_entities, { __index = htmldecode_map } )
		end
		dec = decode_named_entities
	else
		dec = htmldecode_map
	end
	-- string.gsub is safe here, because only ASCII chars are in the pattern
	s = string.gsub( s, '(&(#?x?)([a-zA-Z0-9]+);)', function ( m, flg, name )
		if not dec[m] then
			local n = nil
			if flg == '#' then
				n = tonumber( name, 10 )
			elseif flg == '#x' then
				n = tonumber( name, 16 )
			end
			if n and n <= 0x10ffff then
				n = mw.ustring.char( n )
				if n then
					htmldecode_map[m] = n
					htmlencode_map[n] = m
				end
			end
		end
		return dec[m]
	end )
	return s
end

local nowikiRepl1 = {
	['"'] = '&#34;',
	['&'] = '&#38;',
	["'"] = '&#39;',
	['<'] = '&#60;',
	['='] = '&#61;',
	['>'] = '&#62;',
	['['] = '&#91;',
	[']'] = '&#93;',
	['{'] = '&#123;',
	['|'] = '&#124;',
	['}'] = '&#125;',
}

local nowikiRepl2 = {
	["\n#"] = "\n&#35;", ["\r#"] = "\r&#35;",
	["\n*"] = "\n&#42;", ["\r*"] = "\r&#42;",
	["\n:"] = "\n&#58;", ["\r:"] = "\r&#58;",
	["\n;"] = "\n&#59;", ["\r;"] = "\r&#59;",
	["\n "] = "\n&#32;", ["\r "] = "\r&#32;",
	["\n\n"] = "\n&#10;", ["\r\n"] = "&#13;\n",
	["\n\r"] = "\n&#13;", ["\r\r"] = "\r&#13;",
	["\n\t"] = "\n&#9;", ["\r\t"] = "\r&#9;",
}

local nowikiReplMagic = {}
for sp, esc in pairs( {
	[' '] = '&#32;',
	['\t'] = '&#9;',
	['\r'] = '&#13;',
	['\n'] = '&#10;',
	['\f'] = '&#12;',
} ) do
	nowikiReplMagic['ISBN' .. sp] = 'ISBN' .. esc
	nowikiReplMagic['RFC' .. sp] = 'RFC' .. esc
	nowikiReplMagic['PMID' .. sp] = 'PMID' .. esc
end

function mwtext.nowiki( s )
	-- string.gsub is safe here, because we're only caring about ASCII chars
	s = string.gsub( s, '["&\'<=>%[%]{|}]', nowikiRepl1 )
	s = '\n' .. s
	s = string.gsub( s, '[\r\n][#*:; \n\r\t]', nowikiRepl2 )
	s = string.gsub( s, '([\r\n])%-%-%-%-', '%1&#45;---' )
	s = string.sub( s, 2 )
	s = string.gsub( s, '__', '_&#95;' )
	s = string.gsub( s, '://', '&#58;//' )
	s = string.gsub( s, 'ISBN%s', nowikiReplMagic )
	s = string.gsub( s, 'RFC%s', nowikiReplMagic )
	s = string.gsub( s, 'PMID%s', nowikiReplMagic )
	for k, v in pairs( options.nowiki_protocols ) do
		s = string.gsub( s, k, v )
	end

	return s
end

function mwtext.tag( name, attrs, content )
	local named = false
	if type( name ) == 'table' then
		named = true
		name, attrs, content = name.name, name.attrs, name.content
		checkTypeForNamedArg( 'tag', 'name', name, 'string' )
		checkTypeForNamedArg( 'tag', 'attrs', attrs, 'table', true )
	else
		checkType( 'tag', 1, name, 'string' )
		checkType( 'tag', 2, attrs, 'table', true )
	end

	local ret = { '<' .. name }
	for k, v in pairs( attrs or {} ) do
		if type( k ) ~= 'string' then
			error( "bad named argument attrs to 'tag' (keys must be strings, found " .. type( k ) .. ")", 2 )
		end
		if string.match( k, '[\t\r\n\f /<>"\'=]' ) then
			error( "bad named argument attrs to 'tag' (invalid key '" .. k .. "')", 2 )
		end
		local tp = type( v )
		if tp == 'boolean' then
			if v then
				ret[#ret+1] = ' ' .. k
			end
		elseif tp == 'string' or tp == 'number' then
			ret[#ret+1] = string.format( ' %s="%s"', k, mwtext.encode( tostring( v ) ) )
		else
			error( "bad named argument attrs to 'tag' (value for key '" .. k .. "' may not be " .. tp .. ")", 2 )
		end
	end

	local tp = type( content )
	if content == nil then
		ret[#ret+1] = '>'
	elseif content == false then
		ret[#ret+1] = ' />'
	elseif tp == 'string' or tp == 'number' then
		ret[#ret+1] = '>'
		ret[#ret+1] = content
		ret[#ret+1] = '</' .. name .. '>'
	else
		if named then
			checkTypeForNamedArg( 'tag', 'content', content, 'string, number, nil, or false' )
		else
			checkType( 'tag', 3, content, 'string, number, nil, or false' )
		end
	end

	return table.concat( ret )
end

function mwtext.unstrip( s )
	return php.unstrip( s )
end

function mwtext.unstripNoWiki( s )
	return php.unstripNoWiki( s )
end

function mwtext.killMarkers( s )
	return php.killMarkers( s )
end

function mwtext.split( text, pattern, plain )
	local ret = {}
	for m in mwtext.gsplit( text, pattern, plain ) do
		ret[#ret+1] = m
	end
	return ret
end

function mwtext.gsplit( text, pattern, plain )
	local s, l = 1, mw.ustring.len( text )
	return function ()
		if s then
			local e, n = mw.ustring.find( text, pattern, s, plain )
			local ret
			if not e then
				ret = mw.ustring.sub( text, s )
				s = nil
			elseif n < e then
				-- Empty separator!
				ret = mw.ustring.sub( text, s, e )
				if e < l then
					s = e + 1
				else
					s = nil
				end
			else
				ret = e > s and mw.ustring.sub( text, s, e - 1 ) or ''
				s = n + 1
			end
			return ret
		end
	end, nil, nil
end

function mwtext.listToText( list, separator, conjunction )
	separator = separator or options.comma
	conjunction = conjunction or options['and']
	local n = #list

	local ret
	if n > 1 then
		ret = table.concat( list, separator, 1, n - 1 ) .. conjunction .. list[n]
	else
		ret = tostring( list[1] or '' )
	end

	return ret
end

function mwtext.truncate( text, length, ellipsis, adjustLength )
	local l = mw.ustring.len( text )
	if l <= math.abs( length ) then
		return text
	end

	ellipsis = ellipsis or options.ellipsis
	local elen = 0
	if adjustLength then
		elen = mw.ustring.len( ellipsis )
	end

	local ret
	if math.abs( length ) <= elen then
		ret = ellipsis
	elseif length > 0 then
		ret = mw.ustring.sub( text, 1, length - elen ) .. ellipsis
	else
		ret = ellipsis .. mw.ustring.sub( text, length + elen )
	end

	if mw.ustring.len( ret ) < l then
		return ret
	else
		return text
	end
end

-- Check for stuff that can't even be passed to PHP properly and other stuff
-- that gives different error messages in different versions of PHP
local function checkForJsonEncode( t, seen, lvl )
	local tp = type( t )
	if tp == 'table' then
		if seen[t] then
			error( "mw.text.jsonEncode: Cannot use recursive tables", lvl )
		end
		seen[t] = 1
		for k, v in pairs( t ) do
			if type( k ) == 'number' then
				if k >= math.huge or k <= -math.huge then
					error( string.format( "mw.text.jsonEncode: Cannot use 'inf' as a table key", type( k ) ), lvl )
				end
			elseif type( k ) ~= 'string' then
				error( string.format( "mw.text.jsonEncode: Cannot use type '%s' as a table key", type( k ) ), lvl )
			end
			checkForJsonEncode( v, seen, lvl + 1 )
		end
		seen[t] = nil
	elseif tp == 'number' then
		if t ~= t or t >= math.huge or t <= -math.huge then
			error( "mw.text.jsonEncode: Cannot encode non-finite numbers", lvl )
		end
	elseif tp ~= 'boolean' and tp ~= 'string' and tp ~= 'nil' then
		error( string.format( "mw.text.jsonEncode: Cannot encode type '%s'", tp ), lvl )
	end
end

function mwtext.jsonEncode( value, flags )
	checkForJsonEncode( value, {}, 3 )
	return php.jsonEncode( value, flags )
end

function mwtext.jsonDecode( json, flags )
	return php.jsonDecode( json, flags )
end

-- Matches PHP Scribunto_LuaTextLibrary constants
mwtext.JSON_PRESERVE_KEYS = 1
mwtext.JSON_TRY_FIXING = 2
mwtext.JSON_PRETTY = 4

return mwtext
