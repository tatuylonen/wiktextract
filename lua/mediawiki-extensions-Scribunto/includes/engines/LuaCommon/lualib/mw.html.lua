--[[
	A module for building complex HTML from Lua using a
	fluent interface.

	Originally written on the English Wikipedia by
	Toohool and Mr. Stradivarius.

	Code released under the GPL v2+ as per:
	https://en.wikipedia.org/w/index.php?diff=next&oldid=581399786
	https://en.wikipedia.org/w/index.php?diff=next&oldid=581403025

	@license GNU GPL v2+
	@author Marius Hoch < hoo@online.de >
]]

local HtmlBuilder = {}
local options

local util = require 'libraryUtil'
local checkType = util.checkType
local checkTypeMulti = util.checkTypeMulti

local metatable = {}
local methodtable = {}

local selfClosingTags = {
	area = true,
	base = true,
	br = true,
	col = true,
	command = true,
	embed = true,
	hr = true,
	img = true,
	input = true,
	keygen = true,
	link = true,
	meta = true,
	param = true,
	source = true,
	track = true,
	wbr = true,
}

local htmlencodeMap = {
	['>'] = '&gt;',
	['<'] = '&lt;',
	['&'] = '&amp;',
	['"'] = '&quot;',
}

metatable.__index = methodtable

metatable.__tostring = function( t )
	local ret = {}
	t:_build( ret )
	return table.concat( ret )
end

-- Get an attribute table (name, value) and its index
--
-- @param name
local function getAttr( t, name )
	for i, attr in ipairs( t.attributes ) do
		if attr.name == name then
			return attr, i
		end
	end
end

-- Is this a valid attribute name?
--
-- @param s
local function isValidAttributeName( s )
	-- Good estimate: http://www.w3.org/TR/2000/REC-xml-20001006#NT-Name
	return s:match( '^[a-zA-Z_:][a-zA-Z0-9_.:-]*$' )
end

-- Is this a valid tag name?
--
-- @param s
local function isValidTag( s )
	return s:match( '^[a-zA-Z0-9]+$' )
end

-- Escape a value, for use in HTML
--
-- @param s
local function htmlEncode( s )
	-- The parentheses ensure that there is only one return value
	local tmp = string.gsub( s, '[<>&"]', htmlencodeMap );
	-- Don't encode strip markers here (T110143)
	tmp = string.gsub( tmp, options.encodedUniqPrefixPat, options.uniqPrefixRepl )
	tmp = string.gsub( tmp, options.encodedUniqSuffixPat, options.uniqSuffixRepl )
	return tmp
end

local function cssEncode( s )
	-- mw.ustring is so slow that it's worth searching the whole string
	-- for non-ASCII characters to avoid it if possible
	return ( string.find( s, '[^%z\1-\127]' ) and mw.ustring or string )
		-- XXX: I'm not sure this character set is complete.
		-- bug #68011: allow delete character (\127)
		.gsub( s, '[^\32-\57\60-\127]', function ( m )
			return string.format( '\\%X ', mw.ustring.codepoint( m ) )
		end )
end

-- Create a builder object. This is a separate function so that we can show the
-- correct error levels in both HtmlBuilder.create and metatable.tag.
--
-- @param tagName
-- @param args
local function createBuilder( tagName, args )
	if tagName ~= nil and tagName ~= '' and not isValidTag( tagName ) then
		error( string.format( "invalid tag name '%s'", tagName ), 3 )
	end

	args = args or {}
	local builder = {}
	setmetatable( builder, metatable )
	builder.nodes = {}
	builder.attributes = {}
	builder.styles = {}

	if tagName ~= '' then
		builder.tagName = tagName
	end

	builder.parent = args.parent
	builder.selfClosing = selfClosingTags[tagName] or args.selfClosing or false
	return builder
end

-- Append a builder to the current node. This is separate from methodtable.node
-- so that we can show the correct error level in both methodtable.node and
-- methodtable.wikitext.
--
-- @param builder
local function appendBuilder( t, builder )
	if t.selfClosing then
		error( "self-closing tags can't have child nodes", 3 )
	end

	if builder then
		table.insert( t.nodes, builder )
	end
	return t
end

methodtable._build = function( t, ret )
	if t.tagName then
		table.insert( ret, '<' .. t.tagName )
		for i, attr in ipairs( t.attributes ) do
			table.insert(
				ret,
				-- Note: Attribute names have already been validated
				' ' .. attr.name .. '="' .. htmlEncode( attr.val ) .. '"'
			)
		end
		if #t.styles > 0 then
			table.insert( ret, ' style="' )
			local css = {}
			for i, prop in ipairs( t.styles ) do
				if type( prop ) ~= 'table' then -- added with cssText()
					table.insert( css, htmlEncode( prop ) )
				else -- added with css()
					table.insert(
						css,
						htmlEncode( cssEncode( prop.name ) .. ':' .. cssEncode( prop.val ) )
					)
				end
			end
			table.insert( ret, table.concat( css, ';' ) )
			table.insert( ret, '"' )
		end
		if t.selfClosing then
			table.insert( ret, ' />' )
			return
		end
		table.insert( ret, '>' )
	end
	for i, node in ipairs( t.nodes ) do
		if node then
			if type( node ) == 'table' then
				node:_build( ret )
			else
				table.insert( ret, tostring( node ) )
			end
		end
	end
	if t.tagName then
		table.insert( ret, '</' .. t.tagName .. '>' )
	end
end

-- Append a builder to the current node
--
-- @param builder
methodtable.node = function( t, builder )
	return appendBuilder( t, builder )
end

-- Appends some markup to the node. This will be treated as wikitext.
methodtable.wikitext = function( t, ... )
	for k,v in ipairs{...} do
		checkTypeMulti( 'wikitext', k, v, { 'string', 'number' } )
		appendBuilder( t, v )
	end
	return t
end

-- Appends a newline character to the node.
methodtable.newline = function( t )
	return t:wikitext( '\n' )
end

-- Appends a new child node to the builder, and returns an HtmlBuilder instance
-- representing that new node.
--
-- @param tagName
-- @param args
methodtable.tag = function( t, tagName, args )
	checkType( 'tag', 1, tagName, 'string' )
	checkType( 'tag', 2, args, 'table', true )
	args = args or {}

	args.parent = t
	local builder = createBuilder( tagName, args )
	t:node( builder )
	return builder
end

-- Get the value of an html attribute
--
-- @param name
methodtable.getAttr = function( t, name )
	checkType( 'getAttr', 1, name, 'string' )

	local attr = getAttr( t, name )
	return attr and attr.val
end

-- Set an HTML attribute on the node.
--
-- @param name Attribute to set, alternative table of name-value pairs
-- @param val Value of the attribute. Nil causes the attribute to be unset
methodtable.attr = function( t, name, val )
	if type( name ) == 'table' then
		if val ~= nil then
			error(
				"bad argument #2 to 'attr' " ..
				'(if argument #1 is a table, argument #2 must be left empty)',
				2
			)
		end

		local callForTable = function()
			for attrName, attrValue in pairs( name ) do
				t:attr( attrName, attrValue )
			end
		end

		if not pcall( callForTable ) then
			error(
				"bad argument #1 to 'attr' " ..
				'(table keys must be strings, and values must be strings or numbers)',
				2
			)
		end

		return t
	end

	checkType( 'attr', 1, name, 'string' )
	checkTypeMulti( 'attr', 2, val, { 'string', 'number', 'nil' } )

	-- if caller sets the style attribute explicitly, then replace all styles
	-- previously added with css() and cssText()
	if name == 'style' then
		t.styles = { val }
		return t
	end

	if not isValidAttributeName( name ) then
		error( string.format(
			"bad argument #1 to 'attr' (invalid attribute name '%s')",
			name
		), 2 )
	end

	local attr, i = getAttr( t, name )
	if attr then
		if val ~= nil then
			attr.val = val
		else
			table.remove( t.attributes, i )
		end
	elseif val ~= nil then
		table.insert( t.attributes, { name = name, val = val } )
	end

	return t
end

-- Adds a class name to the node's class attribute. Spaces will be
-- automatically added to delimit each added class name.
--
-- @param class
methodtable.addClass = function( t, class )
	checkTypeMulti( 'addClass', 1, class, { 'string', 'number', 'nil' } )

	if class ~= nil then
		local attr = getAttr( t, 'class' )
		if attr then
			attr.val = attr.val .. ' ' .. class
		else
			t:attr( 'class', class )
		end
	end
	return t
end

-- Set a CSS property to be added to the node's style attribute.
--
-- @param name CSS attribute to set, alternative table of name-value pairs
-- @param val The value to set. Nil causes it to be unset
methodtable.css = function( t, name, val )
	if type( name ) == 'table' then
		if val ~= nil then
			error(
				"bad argument #2 to 'css' " ..
				'(if argument #1 is a table, argument #2 must be left empty)',
				2
			)
		end

		local callForTable = function()
			for attrName, attrValue in pairs( name ) do
				t:css( attrName, attrValue )
			end
		end

		if not pcall( callForTable ) then
			error(
				"bad argument #1 to 'css' " ..
				'(table keys and values must be strings or numbers)',
				2
			)
		end

		return t
	end

	checkTypeMulti( 'css', 1, name, { 'string', 'number' } )
	checkTypeMulti( 'css', 2, val, { 'string', 'number', 'nil' } )

	for i, prop in ipairs( t.styles ) do
		if prop.name == name then
			if val ~= nil then
				prop.val = val
			else
				table.remove( t.styles, i )
			end
			return t
		end
	end

	if val ~= nil then
		table.insert( t.styles, { name = name, val = val } )
	end

	return t
end

-- Add some raw CSS to the node's style attribute. This is typically used
-- when a template allows some CSS to be passed in as a parameter
--
-- @param css
methodtable.cssText = function( t, css )
	checkTypeMulti( 'cssText', 1, css, { 'string', 'number', 'nil' } )
	table.insert( t.styles, css )
	return t
end

-- Returns the parent node under which the current node was created. Like
-- jQuery.end, this is a convenience function to allow the construction of
-- several child nodes to be chained together into a single statement.
methodtable.done = function( t )
	return t.parent or t
end

-- Like .done(), but traverses all the way to the root node of the tree and
-- returns it.
methodtable.allDone = function( t )
	while t.parent do
		t = t.parent
	end
	return t
end

-- Create a new instance
--
-- @param tagName
-- @param args
function HtmlBuilder.create( tagName, args )
	checkType( 'mw.html.create', 1, tagName, 'string', true )
	checkType( 'mw.html.create', 2, args, 'table', true )
	return createBuilder( tagName, args )
end

function HtmlBuilder.setupInterface( opts )
	-- Boilerplate
	HtmlBuilder.setupInterface = nil
	mw_interface = nil
	options = opts

	-- Prepare patterns for unencoding strip markers
	options.encodedUniqPrefixPat = string.gsub( options.uniqPrefix, '[<>&"]', htmlencodeMap );
	options.encodedUniqPrefixPat = string.gsub( options.encodedUniqPrefixPat, '%p', '%%%0' );
	options.uniqPrefixRepl = string.gsub( options.uniqPrefix, '%%', '%%%0' );
	options.encodedUniqSuffixPat = string.gsub( options.uniqSuffix, '[<>&"]', htmlencodeMap );
	options.encodedUniqSuffixPat = string.gsub( options.encodedUniqSuffixPat, '%p', '%%%0' );
	options.uniqSuffixRepl = string.gsub( options.uniqSuffix, '%%', '%%%0' );

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.html = HtmlBuilder

	package.loaded['mw.html'] = HtmlBuilder
end

return HtmlBuilder
