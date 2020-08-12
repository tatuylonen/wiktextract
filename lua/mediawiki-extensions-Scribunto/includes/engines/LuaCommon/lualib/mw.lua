mw = mw or {}

local packageCache
local packageModuleFunc
local php
local allowEnvFuncs = false
local logBuffer = ''
local loadedData = {}
local executeFunctionDepth = 0

--- Put an isolation-friendly package module into the specified environment
-- table. The package module will have an empty cache, because caching of
-- module functions from other cloned environments would break module isolation.
--
-- @param env The cloned environment
local function makePackageModule( env )
	-- Remove loaders from env, we don't want it inheriting our loadPackage.
	if env.package then
		env.package.loaders = nil
	end

	-- Create the package globals in the given environment
	setfenv( packageModuleFunc, env )()

	-- Make a loader function
	local function loadPackage( modName )
		local init
		if packageCache[modName] == 'missing' then
			return nil
		elseif packageCache[modName] == nil then
			local lib = php.loadPHPLibrary( modName )
			if lib ~= nil then
				init = function ()
					return mw.clone( lib )
				end
			else
				init = php.loadPackage( modName )
				if init == nil then
					packageCache[modName] = 'missing'
					return nil
				end
			end
			packageCache[modName] = init
		else
			init = packageCache[modName]
		end

		setfenv( init, env )
		return init
	end

	table.insert( env.package.loaders, loadPackage )
end

--- Set up the base environment. The PHP host calls this function after any
-- necessary host-side initialisation has been done.
function mw.setupInterface( options )
	-- Don't allow any more calls
	mw.setupInterface = nil

	-- Don't allow getmetatable() on a non-table, since if you can get the metatable,
	-- you can set values in it, breaking isolation
	local old_getmetatable = getmetatable
	function getmetatable(obj)
		if type(obj) == 'table' then
			return old_getmetatable(obj)
		else
			return nil
		end
	end

	if options.allowEnvFuncs then
		allowEnvFuncs = true
	end

	-- Store the interface table
	--
	-- mw_interface.loadPackage() returns function values with their environment
	-- set to the base environment, which would violate module isolation if they
	-- were run from a cloned environment. We can only allow access to
	-- mw_interface.loadPackage via our environment-setting wrapper.
	--
	php = mw_interface
	mw_interface = nil

	packageModuleFunc = php.loadPackage( 'package' )
	makePackageModule( _G )
	package.loaded.mw = mw
	packageCache = {}
end

--- Create a table like the one os.date() returns, but with a metatable that sets TTLs as the values are looked at.
local function wrapDateTable( now )
	return setmetatable( {}, {
		__index = function( t, k )
			if k == 'sec' then
				php.setTTL( 1 )
			elseif k == 'min' then
				php.setTTL( 60 - now.sec )
			elseif k == 'hour' then
				php.setTTL( 3600 - now.min * 60 - now.sec )
			elseif now[k] ~= nil then
				php.setTTL( 86400 - now.hour * 3600 - now.min * 60 - now.sec )
			end
			t[k] = now[k]
			return now[k]
		end
	} )
end

--- Wrappers for os.date() and os.time() that set the TTL of the output, if necessary
local function ttlDate( format, time )
	if time == nil and ( format == nil or type( format ) == 'string' ) then
		local now = os.date( format and format:sub( 1, 1 ) == '!' and '!*t' or '*t' )
		if format == '!*t' or format == '*t' then
			return wrapDateTable( now )
		end
		local cleanedFormat = format and format:gsub( '%%%%', '' )
		if not format or cleanedFormat:find( '%%[EO]?[crsSTX+]' ) then
			php.setTTL( 1 ) -- second
		elseif cleanedFormat:find( '%%[EO]?[MR]' ) then
			php.setTTL( 60 - now.sec ) -- minute
		elseif cleanedFormat:find( '%%[EO]?[HIkl]' ) then
			php.setTTL( 3600 - now.min * 60 - now.sec ) -- hour
		elseif cleanedFormat:find( '%%[EO]?[pP]' ) then
			php.setTTL( 43200 - ( now.hour % 12 ) * 3600 - now.min * 60 - now.sec ) -- am/pm
		else
			-- It's not worth the complexity to figure out the exact TTL of larger units than days.
			-- If they haven't used anything shorter than days, then just set the TTL to expire at
			-- the end of today.
			php.setTTL( 86400 - now.hour * 3600 - now.min * 60 - now.sec )
		end
	end
	return os.date( format, time )
end

local function ttlTime( t )
	if t == nil then
		php.setTTL( 1 )
	end
	return os.time( t )
end

local function newFrame( frameId, ... )
	if not php.frameExists( frameId ) then
		return nil
	end

	local frame = {}
	local parentFrameIds = { ... }
	local argCache = {}
	local argNames
	local args_mt = {}

	local function checkSelf( self, method )
		if self ~= frame then
			error( "frame:" .. method .. ": invalid frame object. " ..
				"Did you call " .. method .. " with a dot instead of a colon, i.e. " ..
				"frame." .. method .. "() instead of frame:" .. method .. "()?",
				3 )
		end
	end

	-- Getter for args
	local function getExpandedArgument( dummy, name )
		name = tostring( name )
		if argCache[name] == nil then
			local arg = php.getExpandedArgument( frameId, name )
			if arg == nil then
				argCache[name] = false
			else
				argCache[name] = arg
			end
		end
		if argCache[name] == false then
			return nil
		else
			return argCache[name]
		end
	end

	args_mt.__index = getExpandedArgument

	-- pairs handler for args
	args_mt.__pairs = function ()
		if not argNames then
			local arguments = php.getAllExpandedArguments( frameId )
			argNames = {}
			for name, value in pairs( arguments ) do
				table.insert( argNames, name )
				argCache[name] = value
			end
		end

		local index = 0
		return function ()
			index = index + 1
			if argNames[index] then
				return argNames[index], argCache[argNames[index]]
			end
		end
	end

	-- ipairs 'next' function for args
	local function argsInext( dummy, i )
		local value = getExpandedArgument( dummy, i + 1 )
		if value then
			return i + 1, value
		end
	end

	args_mt.__ipairs = function () return argsInext, nil, 0 end

	frame.args = {}
	setmetatable( frame.args, args_mt )

	local function newCallbackParserValue( callback )
		local value = {}
		local cache

		function value:expand()
			if not cache then
				cache = callback()
			end
			return cache
		end

		return value
	end

	function frame:getArgument( opt )
		checkSelf( self, 'getArgument' )

		local name
		if type( opt ) == 'table' then
			name = opt.name
		else
			name = opt
		end

		return newCallbackParserValue(
			function ()
				return getExpandedArgument( nil, name )
			end
			)
	end

	function frame:getParent()
		checkSelf( self, 'getParent' )

		return newFrame( unpack( parentFrameIds ) )
	end

	local function checkArgs( name, args )
		local ret = {}
		for k, v in pairs( args ) do
			local tp = type( k )
			if tp ~= 'string' and tp ~= 'number' then
				error( name .. ": arg keys must be strings or numbers, " .. tp .. " given", 3 )
			end
			tp = type( v )
			if tp == 'boolean' then
				ret[k] = v and '1' or ''
			elseif tp == 'string' or tp == 'number' then
				ret[k] = tostring( v )
			else
				error( name .. ": invalid type " .. tp .. " for arg '" .. k .. "'", 3 )
			end
		end
		return ret
	end

	function frame:newChild( opt )
		checkSelf( self, 'newChild' )

		if type( opt ) ~= 'table' then
			error( "frame:newChild: the first parameter must be a table", 2 )
		end

		local title, args
		if opt.title == nil then
			title = false
		else
			title = tostring( opt.title )
		end
		if opt.args == nil then
			args = {}
		elseif type( opt.args ) ~= 'table' then
			error( "frame:newChild: args must be a table", 2 )
		else
			args = checkArgs( 'frame:newChild', opt.args )
		end

		local newFrameId = php.newChildFrame( frameId, title, args )
		return newFrame( newFrameId, frameId, unpack( parentFrameIds ) )
	end

	function frame:expandTemplate( opt )
		checkSelf( self, 'expandTemplate' )

		local title

		if type( opt ) ~= 'table' then
			error( "frame:expandTemplate: the first parameter must be a table" )
		end
		if opt.title == nil then
			error( "frame:expandTemplate: a title is required" )
		else
			if type( opt.title ) == 'table' and opt.title.namespace == 0 then
				title = ':' .. tostring( opt.title )
			else
				title = tostring( opt.title )
			end
		end
		local args
		if opt.args == nil then
			args = {}
		elseif type( opt.args ) ~= 'table' then
			error( "frame:expandTemplate: args must be a table" )
		else
			args = checkArgs( 'frame:expandTemplate', opt.args )
		end

		return php.expandTemplate( frameId, title, args )
	end

	function frame:callParserFunction( name, args, ... )
		checkSelf( self, 'callParserFunction' )

		if type( name ) == 'table' then
			name, args = name.name, name.args
			if type( args ) ~= 'table' then
				args = { args }
			end
		elseif type( args ) ~= 'table' then
			args = { args, ... }
		end

		if name == nil then
			error( "frame:callParserFunction: a function name is required", 2 )
		elseif type( name ) == 'string' or type( name ) == 'number' then
			name = tostring( name )
		else
			error( "frame:callParserFunction: function name must be a string or number", 2 )
		end

		args = checkArgs( 'frame:callParserFunction', args )

		return php.callParserFunction( frameId, name, args )
	end

	function frame:extensionTag( name, content, args )
		checkSelf( self, 'extensionTag' )

		if type( name ) == 'table' then
			name, content, args = name.name, name.content, name.args
		end

		if name == nil then
			error( "frame:extensionTag: a function name is required", 2 )
		elseif type( name ) == 'string' or type( name ) == 'number' then
			name = tostring( name )
		else
			error( "frame:extensionTag: tag name must be a string or number", 2 )
		end

		if content == nil then
			content = ''
		elseif type( content ) == 'string' or type( content ) == 'number' then
			content = tostring( content )
		else
			error( "frame:extensionTag: content must be a string or number", 2 )
		end

		if args == nil then
			args = { content }
		elseif type( args ) == 'string' or type( args ) == 'number' then
			args = { content, args }
		elseif type( args ) == 'table' then
			args = checkArgs( 'frame:extensionTag', args )
			table.insert( args, 1, content )
		else
			error( "frame:extensionTag: args must be a string, number, or table", 2 )
		end

		return php.callParserFunction( frameId, '#tag:' .. name, args )
	end

	function frame:preprocess( opt )
		checkSelf( self, 'preprocess' )

		local text
		if type( opt ) == 'table' then
			text = opt.text
		else
			text = opt
		end
		text = tostring( text )
		return php.preprocess( frameId, text )
	end

	function frame:newParserValue( opt )
		checkSelf( self, 'newParserValue' )

		local text
		if type( opt ) == 'table' then
			text = opt.text
		else
			text = opt
		end

		return newCallbackParserValue(
			function ()
				return self:preprocess( text )
			end
			)
	end

	function frame:newTemplateParserValue( opt )
		checkSelf( self, 'newTemplateParserValue' )

		if type( opt ) ~= 'table' then
			error( "frame:newTemplateParserValue: the first parameter must be a table" )
		end
		if opt.title == nil then
			error( "frame:newTemplateParserValue: a title is required" )
		end
		return newCallbackParserValue(
			function ()
				return self:expandTemplate( opt )
			end
		)
	end

	function frame:getTitle()
		checkSelf( self, 'getTitle' )
		return php.getFrameTitle( frameId )
	end

	-- For backwards compat
	function frame:argumentPairs()
		checkSelf( self, 'argumentPairs' )
		return pairs( self.args )
	end

	return frame
end

--- Set up a cloned environment for execution of a module chunk, then execute
-- the module in that environment. This is called by the host to implement
-- {{#invoke}}.
--
-- @param chunk The module chunk
-- @param name The name of the function to be returned. Nil or false causes the entire export table to be returned
-- @param frame New frame to use; if nil, one will be created
-- @return boolean Whether the requested value was able to be returned
-- @return table|function|string The requested value, or if that was unable to be returned, the type of the value returned by the module
function mw.executeModule( chunk, name, frame )
	local env = mw.clone( _G )
	makePackageModule( env )

	-- These are unsafe
	env.mw.makeProtectedEnvFuncs = nil
	env.mw.executeModule = nil
	if name ~= false then -- console sets name to false when evaluating its code and nil when evaluating a module's
		env.mw.getLogBuffer = nil
		env.mw.clearLogBuffer = nil
	end

	if allowEnvFuncs then
		env.setfenv, env.getfenv = mw.makeProtectedEnvFuncs( {[_G] = true}, {} )
	else
		env.setfenv = nil
		env.getfenv = nil
	end

	env.os.date = ttlDate
	env.os.time = ttlTime

	frame = frame or newFrame( 'current', 'parent' )
	env.mw.getCurrentFrame = function ()
		return frame
	end

	setfenv( chunk, env )

	local res = chunk()

	if not name then -- catch console whether it's evaluating its own code or a module's
		return true, res
	end
	if type(res) ~= 'table' then
		return false, type(res)
	end
	return true, res[name]
end

function mw.executeFunction( chunk )
	local getCurrentFrame = getfenv( chunk ).mw.getCurrentFrame
	local frame
	if getCurrentFrame then
		-- Normal case
		frame = getCurrentFrame()
	else
		-- If someone assigns a built-in method to the module's return table,
		-- its env won't have mw.getCurrentFrame()
		frame = newFrame( 'current', 'parent' )
	end

	if executeFunctionDepth == 0 then
		-- math.random is defined as using C's rand(), and C's rand() uses 1 as
		-- a seed if not explicitly seeded. So reseed with 1 for each top-level
		-- #invoke to avoid people passing state via the RNG.
		math.randomseed( 1 )
	end
	executeFunctionDepth = executeFunctionDepth + 1

	local results = { chunk( frame ) }

	local stringResults = {}
	for i, result in ipairs( results ) do
		stringResults[i] = tostring( result )
	end

	executeFunctionDepth = executeFunctionDepth - 1

	return table.concat( stringResults )
end

function mw.allToString( ... )
	local t = { ... }
	for i = 1, select( '#', ... ) do
		t[i] = tostring( t[i] )
	end
	return table.concat( t, '\t' )
end

function mw.log( ... )
	logBuffer = logBuffer .. mw.allToString( ... ) .. '\n'
end

function mw.dumpObject( object )
	local doneTable = {}
	local doneObj = {}
	local ct = {}
	local function sorter( a, b )
		local ta, tb = type( a ), type( b )
		if ta ~= tb then
			return ta < tb
		end
		if ta == 'string' or ta == 'number' then
			return a < b
		end
		if ta == 'boolean' then
			return tostring( a ) < tostring( b )
		end
		return false -- Incomparable
	end
	local function _dumpObject( object, indent, expandTable )
		local tp = type( object )
		if tp == 'number' or tp == 'nil' or tp == 'boolean' then
			return tostring( object )
		elseif tp == 'string' then
			return string.format( "%q", object )
		elseif tp == 'table' then
			if not doneObj[object] then
				local s = tostring( object )
				if s == 'table' then
					ct[tp] = ( ct[tp] or 0 ) + 1
					doneObj[object] = 'table#' .. ct[tp]
				else
					doneObj[object] = s
					doneTable[object] = true
				end
			end
			if doneTable[object] or not expandTable then
				return doneObj[object]
			end
			doneTable[object] = true

			local ret = { doneObj[object], ' {\n' }
			local mt = getmetatable( object )
			if mt then
				ret[#ret + 1] = string.rep( " ", indent + 2 )
				ret[#ret + 1] = 'metatable = '
				ret[#ret + 1] = _dumpObject( mt, indent + 2, false )
				ret[#ret + 1] = "\n"
			end

			local doneKeys = {}
			for key, value in ipairs( object ) do
				doneKeys[key] = true
				ret[#ret + 1] = string.rep( " ", indent + 2 )
				ret[#ret + 1] = _dumpObject( value, indent + 2, true )
				ret[#ret + 1] = ',\n'
			end
			local keys = {}
			for key in pairs( object ) do
				if not doneKeys[key] then
					keys[#keys + 1] = key
				end
			end
			table.sort( keys, sorter )
			for i = 1, #keys do
				local key = keys[i]
				ret[#ret + 1] = string.rep( " ", indent + 2 )
				ret[#ret + 1] = '['
				ret[#ret + 1] = _dumpObject( key, indent + 3, false )
				ret[#ret + 1] = '] = '
				ret[#ret + 1] = _dumpObject( object[key], indent + 2, true )
				ret[#ret + 1] = ",\n"
			end
			ret[#ret + 1] = string.rep( " ", indent )
			ret[#ret + 1] = '}'
			return table.concat( ret )
		else
			if not doneObj[object] then
				ct[tp] = ( ct[tp] or 0 ) + 1
				doneObj[object] = tostring( object ) .. '#' .. ct[tp]
			end
			return doneObj[object]
		end
	end
	return _dumpObject( object, 0, true )
end

function mw.logObject( object, prefix )
	if prefix and prefix ~= '' then
		logBuffer = logBuffer .. prefix .. ' = '
	end
	logBuffer = logBuffer .. mw.dumpObject( object ) .. '\n'
end

function mw.clearLogBuffer()
	logBuffer = ''
end

function mw.getLogBuffer()
	return logBuffer
end

function mw.isSubsting()
	return php.isSubsting()
end

function mw.incrementExpensiveFunctionCount()
	php.incrementExpensiveFunctionCount()
end

function mw.addWarning( text )
	php.addWarning( text )
end

---
-- Wrapper for mw.loadData. This creates the read-only dummy table for
-- accessing the real data.
--
-- @param data table Data to access
-- @param seen table|nil Table of already-seen tables.
-- @return table
local function dataWrapper( data, seen )
	local t = {}
	seen = seen or { [data] = t }

	local function pairsfunc( s, k )
		k = next( data, k )
		if k ~= nil then
			return k, t[k]
		end
		return nil
	end

	local function ipairsfunc( s, i )
		i = i + 1
		if data[i] ~= nil then
			return i, t[i]
		end
		return -- no nil to match default ipairs()
	end

	local mt = {
		mw_loadData = true,
		__index = function ( tt, k )
			assert( t == tt )
			local v = data[k]
			if type( v ) == 'table' then
				seen[v] = seen[v] or dataWrapper( v, seen )
				return seen[v]
			end
			return v
		end,
		__newindex = function ( t, k, v )
			error( "table from mw.loadData is read-only", 2 )
		end,
		__pairs = function ( tt )
			assert( t == tt )
			return pairsfunc, t, nil
		end,
		__ipairs = function ( tt )
			assert( t == tt )
			return ipairsfunc, t, 0
		end,
	}
	-- This is just to make setmetatable() fail
	mt.__metatable = mt

	return setmetatable( t, mt )
end

---
-- Validator for mw.loadData. This scans through the data looking for things
-- that are not supported, e.g. functions (which may be closures).
--
-- @param d table Data to access.
-- @param seen table|nil Table of already-seen tables.
-- @return string|nil Error message, if any
local function validateData( d, seen )
	seen = seen or {}
	local tp = type( d )
	if tp == 'nil' or tp == 'boolean' or tp == 'number' or tp == 'string' then
		return nil
	elseif tp == 'table' then
		if seen[d] then
			return nil
		end
		seen[d] = true
		if getmetatable( d ) ~= nil then
			return "data for mw.loadData contains a table with a metatable"
		end
		for k, v in pairs( d ) do
			if type( k ) == 'table' then
				return "data for mw.loadData contains a table as a key"
			end
			local err = validateData( k, seen ) or validateData( v, seen )
			if err then
				return err
			end
		end
		return nil
	else
		return "data for mw.loadData contains unsupported data type '" .. tp .. "'"
	end
end

function mw.loadData( module )
	local data = loadedData[module]
	if type( data ) == 'string' then
		-- No point in re-validating
		error( data, 2 )
	end
	if not data then
		-- The point of this is to load big data, so don't save it in package.loaded
		-- where it will have to be copied for all future modules.
		local l = package.loaded[module]
		local _

		_, data = mw.executeModule( function() return require( module ) end, nil, newFrame( 'empty' ) )

		package.loaded[module] = l

		-- Validate data
		local err
		if type( data ) == 'table' then
			err = validateData( data )
		else
			err = module .. ' returned ' .. type( data ) .. ', table expected'
		end
		if err then
			loadedData[module] = err
			error( err, 2 )
		end
		loadedData[module] = data
	end

	return dataWrapper( data )
end

return mw
