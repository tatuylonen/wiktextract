local message = {}
local php

local util = require 'libraryUtil'
local checkType = util.checkType

local valuemt = {
	__tostring = function ( t )
		return tostring( t.raw or t.num )
	end
}

local function checkScalar( name, argIdx, arg, level, valuemtOk )
	local tp = type( arg )

	-- If special params are ok, detect them
	if valuemtOk and tp == 'table' and getmetatable( arg ) == valuemt then
		return arg
	end

	-- If it's a table with a custom __tostring function, use that string
	if tp == 'table' and getmetatable( arg ) and getmetatable( arg ).__tostring then
		return tostring( arg )
	end

	if tp ~= 'string' and tp ~= 'number' then
		error( string.format(
			"bad argument #%d to '%s' (string or number expected, got %s)",
			argIdx, name, tp
		), level + 1 )
	end

	return arg
end

local function checkParams( name, valueOk, ... )
	-- Accept an array of params, or params as individual command line arguments
	local params, nparams
	local first = select( 1, ... )
	if type( first ) == 'table' and
		not ( getmetatable( first ) and getmetatable( first ).__tostring )
	then
		if select( '#', ... ) == 1 then
			params = first
			nparams = table.maxn( params )
		else
			error(
				"bad arguments to '" .. name .. "' (pass either a table of params or params as individual arguments)",
				3
			)
		end
	else
		params = { ... }
		nparams = select( '#', ... )
	end
	for i = 1, nparams do
		params[i] = checkScalar( 'params', i, params[i], 3, valueOk )
	end
	return params
end

function message.setupInterface( options )
	-- Boilerplate
	message.setupInterface = nil
	php = mw_interface
	mw_interface = nil
	php.options = options

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.message = message

	package.loaded['mw.message'] = message
end

local function makeMessage( options )
	local obj = {}
	local checkSelf = util.makeCheckSelfFunction( 'mw.message', 'msg', obj, 'message object' )

	local data = {
		keys = options.keys,
		rawMessage = options.rawMessage,
		params = {},
		lang = php.options.lang,
		useDB = true,
	}

	function obj:params( ... )
		checkSelf( self, 'params' )
		local params = checkParams( 'params', true, ... )
		local j = #data.params
		for i = 1, #params do
			data.params[j + i] = params[i]
		end
		return self
	end

	function obj:rawParams( ... )
		checkSelf( self, 'rawParams' )
		local params = checkParams( 'rawParams', false, ... )
		local j = #data.params
		for i = 1, #params do
			data.params[j + i] = setmetatable( { raw = params[i] }, valuemt )
		end
		return self
	end

	function obj:numParams( ... )
		checkSelf( self, 'numParams' )
		local params = checkParams( 'numParams', false, ... )
		local j = #data.params
		for i = 1, #params do
			data.params[j + i] = setmetatable( { num = params[i] }, valuemt )
		end
		return self
	end

	function obj:inLanguage( lang )
		checkSelf( self, 'inLanguage' )
		if type( lang ) == 'table' and lang.getCode then
			-- probably a mw.language object
			lang = lang:getCode()
		end
		checkType( 'inLanguage', 1, lang, 'string' )
		data.lang = lang
		return self
	end

	function obj:useDatabase( value )
		checkSelf( self, 'useDatabase' )
		checkType( 'useDatabase', 1, value, 'boolean' )
		data.useDB = value
		return self
	end

	function obj:plain()
		checkSelf( self, 'plain' )
		return php.plain( data )
	end

	function obj:exists()
		checkSelf( self, 'exists' )
		return php.check( 'exists', data )
	end

	function obj:isBlank()
		checkSelf( self, 'isBlank' )
		return php.check( 'isBlank', data )
	end

	function obj:isDisabled()
		checkSelf( self, 'isDisabled' )
		return php.check( 'isDisabled', data )
	end

	return setmetatable( obj, {
		__tostring = function ( t )
			return t:plain()
		end
	} )
end

function message.new( key, ... )
	checkType( 'message.new', 1, key, 'string' )
	return makeMessage{ keys = { key } }:params( ... )
end

function message.newFallbackSequence( ... )
	for i = 1, math.max( 1, select( '#', ... ) ) do
		checkType( 'message.newFallbackSequence', i, select( i, ... ), 'string' )
	end
	return makeMessage{ keys = { ... } }
end

function message.newRawMessage( msg, ... )
	checkType( 'message.newRawMessage', 1, msg, 'string' )
	return makeMessage{ rawMessage = msg }:params( ... )
end

function message.rawParam( value )
	value = checkScalar( 'message.rawParam', 1, value )
	return setmetatable( { raw = value }, valuemt )
end

function message.numParam( value )
	value = checkScalar( 'message.numParam', 1, value )
	return setmetatable( { num = value }, valuemt )
end

function message.getDefaultLanguage()
	if mw.language then
		return mw.language.new( php.options.lang )
	else
		return php.options.lang
	end
end

return message
