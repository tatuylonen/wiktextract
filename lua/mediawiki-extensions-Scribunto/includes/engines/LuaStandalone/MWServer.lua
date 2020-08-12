MWServer = {}

--- Create a new MWServer object
function MWServer:new( interpreterId, intSize )
	interpreterId = tonumber( interpreterId )
	if not interpreterId then
		error( "bad argument #1 to 'MWServer:new' (must be a number or convertible to a number)", 2 )
	end
	intSize = tonumber( intSize )
	if intSize ~= 4 and intSize ~= 8 then
		error( "bad argument #2 to 'MWServer:new' (must be 4 or 8)", 2 )
	end

	obj = {
		interpreterId = interpreterId,
		nextChunkId = 1,
		chunks = {},
		xchunks = {},
		protectedFunctions = {},
		protectedEnvironments = {},
		baseEnv = {}
	}
	if intSize == 4 then
		obj.intMax = 2147483648
		obj.intKeyMax = 2147483648
	else
		-- Lua can't represent most larger integers, so they may as well be sent to PHP as floats.
		obj.intMax = 9007199254740992
		obj.intKeyMax = 9223372036854775807
	end
	setmetatable( obj, self )
	self.__index = self

	obj:init()

	return obj
end

--- Initialise a new MWServer object
function MWServer:init()
	self.baseEnv = self:newEnvironment()
	for funcName, func in pairs( self ) do
		if type(func) == 'function' then
			self.protectedFunctions[func] = true
		end
	end
	self.protectedEnvironments[_G] = true
end

--- Serve requests until exit is requested
function MWServer:execute()
	self:dispatch( nil )
	self:debug( 'MWServer:execute: returning' )
end

-- Convert a multiple-return-value or a ... into a count and a table
function MWServer:listToCountAndTable( ... )
	return select( '#', ... ), { ... }
end

--- Call a PHP function
-- Raise an error if the PHP handler requests it. May return any number
-- of values.
--
-- @param id The function ID, specified by a registerLibrary message
-- @param nargs Count of function arguments
-- @param args The function arguments
-- @return The return values from the PHP function
function MWServer:call( id, nargs, args )
	local result = self:dispatch( {
		op = 'call',
		id = id,
		nargs = nargs,
		args = args
	} )
	if result.op == 'return' then
		return unpack( result.values, 1, result.nvalues )
	elseif result.op == 'error' then
		-- Raise an error in the actual user code that called the function
		-- The level is 3 since our immediate caller is a closure
		error( result.value, 3 )
	else
		self:internalError( 'MWServer:call: unexpected result op' )
	end
end

--- Handle a "call" message from PHP. Call the relevant function.
--
-- @param message The message from PHP
-- @return A response message to send back to PHP
function MWServer:handleCall( message )
	if not self.chunks[message.id] then
		return {
			op = 'error',
			value = 'function id ' .. message.id .. ' does not exist'
		}
	end

	local n, result = self:listToCountAndTable( xpcall(
		function ()
			return self.chunks[message.id]( unpack( message.args, 1, message.nargs ) )
		end,
		function ( err )
			return MWServer:attachTrace( err )
		end
	) )

	if result[1] then
		-- table.remove( result, 1 ) renumbers from 2 to #result. But #result
		-- is not necessarily "right" if result contains nils.
		result = { unpack( result, 2, n ) }
		return {
			op = 'return',
			nvalues = n - 1,
			values = result
		}
	else
		if result[2].value and result[2].trace then
			return {
				op = 'error',
				value = result[2].value,
				trace = result[2].trace,
			}
		else
			return {
				op = 'error',
				value = result[2]
			}
		end
	end
end

--- The xpcall() error handler for handleCall(). Modifies the error object
-- to include a structured backtrace
--
-- @param err The error object
-- @return The new error object
function MWServer:attachTrace( err )
	return {
		value = err,
		trace = self:getStructuredTrace( 2 )
	}
end

--- Handle a "loadString" message from PHP.
-- Load the function and return a chunk ID.
--
-- @param message The message from PHP
-- @return A response message to send back to PHP
function MWServer:handleLoadString( message )
	if string.find( message.text, '\27Lua', 1, true ) then
		return {
			op = 'error',
			value = 'cannot load code with a Lua binary chunk marker escape sequence in it'
		}
	end
	local chunk, errorMsg = loadstring( message.text, message.chunkName )
	if chunk then
		setfenv( chunk, self.baseEnv )
		local id = self:addChunk( chunk )
		return {
			op = 'return',
			nvalues = 1,
			values = {id}
		}
	else
		return {
			op = 'error',
			value = errorMsg
		}
	end
end

--- Add a function value to the list of tracked chunks and return its associated ID.
-- Adding a chunk allows it to be referred to in messages from PHP.
--
-- @param chunk The function value
-- @return The chunk ID
function MWServer:addChunk( chunk )
	local id = self.nextChunkId
	self.nextChunkId = id + 1
	self.chunks[id] = chunk
	self.xchunks[chunk] = id
	return id
end

--- Handle a "cleanupChunks" message from PHP.
-- Remove any chunks no longer referenced by PHP code.
--
-- @param message The message from PHP
-- @return A response message to send back to PHP
function MWServer:handleCleanupChunks( message )
	for id, chunk in pairs( self.chunks ) do
		if not message.ids[id] then
			self.chunks[id] = nil
			self.xchunks[chunk] = nil
		end
	end

	return {
		op = 'return',
		nvalues = 0,
		values = {}
	}
end

--- Handle a "registerLibrary" message from PHP.
-- Add the relevant functions to the base environment.
--
-- @param message The message from PHP
-- @return The response message
function MWServer:handleRegisterLibrary( message )
	local startPos = 1
	local component
	if not self.baseEnv[message.name] then
		self.baseEnv[message.name] = {}
	end
	local t = self.baseEnv[message.name]

	for name, id in pairs( message.functions ) do
		t[name] = function( ... )
			return self:call( id, self:listToCountAndTable( ... ) )
		end
		-- Protect the function against setfenv()
		self.protectedFunctions[t[name]] = true
	end

	return {
		op = 'return',
		nvalues = 0,
		values = {}
	}
end

--- Handle a "wrapPhpFunction" message from PHP.
-- Create an anonymous function
--
-- @param message The message from PHP
-- @return The response message
function MWServer:handleWrapPhpFunction( message )
	local id = message.id
	local func = function( ... )
		return self:call( id, self:listToCountAndTable( ... ) )
	end
	-- Protect the function against setfenv()
	self.protectedFunctions[func] = true

	return {
		op = 'return',
		nvalues = 1,
		values = { func }
	}
end

--- Handle a "getStatus" message from PHP
--
-- @param message The request message
-- @return The response message
function MWServer:handleGetStatus( message )
	local nullRet = {
		op = 'return',
		nvalues = 0,
		values = {}
	}
	local file = io.open( '/proc/self/stat' )
	if not file then
		return nullRet
	end
	local s = file:read('*a')
	file:close()
	local t = {}
	for token in string.gmatch(s, '[^ ]+') do
		t[#t + 1] = token
	end
	if #t < 22 then
		return nullRet
	end
	return {
		op = 'return',
		nvalues = 1,
		values = {{
			pid = tonumber(t[1]),
			time = tonumber(t[14]) + tonumber(t[15]) + tonumber(t[16]) + tonumber(t[17]),
			vsize = tonumber(t[23]),
		}}
	}
end

--- The main request/response loop
--
-- Send a request message and return its matching reply message. Handle any
-- intervening requests (i.e. re-entrant calls) by dispatching them to the
-- relevant handler function.
--
-- The request message may optionally be omitted, to listen for request messages
-- without first sending a request of its own. Such a dispatch() call will
-- continue running until termination is requested by PHP. Typically, PHP does
-- this with a SIGTERM signal.
--
-- @param msgToPhp The message to send to PHP. Optional.
-- @return The matching response message
function MWServer:dispatch( msgToPhp )
	if msgToPhp then
		self:sendMessage( msgToPhp, 'call' )
	end
	while true do
		local msgFromPhp = self:receiveMessage()
		local msgToPhp
		local op = msgFromPhp.op
		if op == 'return' or op == 'error' then
			return msgFromPhp
		elseif op == 'call' then
			msgToPhp = self:handleCall( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'loadString' then
			msgToPhp = self:handleLoadString( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'registerLibrary' then
			msgToPhp = self:handleRegisterLibrary( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'wrapPhpFunction' then
			msgToPhp = self:handleWrapPhpFunction( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'cleanupChunks' then
			msgToPhp = self:handleCleanupChunks( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'getStatus' then
			msgToPhp = self:handleGetStatus( msgFromPhp )
			self:sendMessage( msgToPhp, 'reply' )
		elseif op == 'quit' then
			self:debug( 'MWServer:dispatch: quit message received' )
			os.exit(0)
		elseif op == 'testquit' then
			self:debug( 'MWServer:dispatch: testquit message received' )
			os.exit(42)
		else
			self:internalError( "Invalid message operation" )
		end
	end
end

--- Write a message to the debug output stream.
-- Some day this may be configurable, currently it just unconditionally writes
-- the message to stderr. The PHP host will redirect those errors to /dev/null
-- by default, but it can be configured to send them to a file.
--
-- @param s The message
function MWServer:debug( s )
	if ( type(s) == 'string' ) then
		io.stderr:write( s .. '\n' )
	else
		io.stderr:write( self:serialize( s ) .. '\n' )
	end
end

--- Raise an internal error
-- Write a message to stderr and then exit with a failure status. This should
-- be called for errors which cannot be allowed to be caught with pcall().
--
-- This must be used for protocol errors, or indeed any error from a context
-- where a dispatch() call lies between the error source and a possible pcall()
-- handler. If dispatch() were terminated by a regular error() call, the
-- resulting protocol violation could lead to a deadlock.
--
-- @param msg The error message
function MWServer:internalError( msg )
	io.stderr:write( debug.traceback( msg ) .. '\n' )
	os.exit( 1 )
end

--- Raise an I/O error
-- Helper function for errors from the io and file modules, which may optionally
-- return an informative error message as their second return value.
function MWServer:ioError( header, info )
	if type( info) == 'string' then
		self:internalError( header .. ': ' .. info )
	else
		self:internalError( header )
	end
end

--- Send a message to PHP
-- @param msg The message table
-- @param direction 'call' or 'reply'
function MWServer:sendMessage( msg, direction )
	if not msg.op then
		self:internalError( "MWServer:sendMessage: invalid message", 2 )
	end
	self:debug('TX ==> ' .. msg.op)

	-- If we're making an outgoing call, let errors go to our caller. If we're
	-- replying to a call from PHP, catch serialization errors and return them
	-- to PHP.
	local encMsg;
	if direction == 'reply' then
		local ok
		ok, encMsg = pcall( self.encodeMessage, self, msg )
		if not ok then
			self:debug('Serialization failed: ' .. encMsg)
			self:debug('TX ==> error')
			encMsg = self:encodeMessage( { op = 'error', value = encMsg } )
		end
	else
		encMsg = self:encodeMessage( msg )
	end

	local success, errorMsg = io.stdout:write( encMsg )
	if not success then
		self:ioError( 'Write error', errorMsg )
	end
	io.stdout:flush()
end

--- Wait for a message from PHP and then decode and return it as a table
-- @return The received message
function MWServer:receiveMessage()
	-- Read the header
	local header, errorMsg = io.stdin:read( 16 )
	if header == nil and errorMsg == nil then
		-- End of file on stdin, exit gracefully
		os.exit(0)
	end

	if not header or #header ~= 16 then
		self:ioError( 'Read error', errorMsg )
	end
	local length = self:decodeHeader( header )

	-- Read the body
	local body, errorMsg = io.stdin:read( length )
	if not body then
		self:ioError( 'Read error', errorMsg )
	end
	if #body ~= length then
		self:ioError( 'Read error', errorMsg )
	end

	-- Unserialize it
	msg = self:unserialize( body )
	self:debug('RX <== ' .. msg.op)
	if msg.op == 'error' then
		self:debug( 'Error: ' .. tostring( msg.value ) )
	end
	return msg
end

--- Encode a message for sending to PHP
function MWServer:encodeMessage( message )
	local serialized = self:serialize( message )
	local length = #serialized
	local check = length * 2 - 1
	return string.format( '%08x%08x', length, check ) .. serialized
end

-- Faster to create the table once than for each call to MWServer:serialize()
local serialize_replacements = {
	['\r'] = '\\r',
	['\n'] = '\\n',
	['\\'] = '\\\\',
}

--- Convert a value to a string suitable for passing to PHP's unserialize().
-- Note that the following replacements must be performed before calling
-- unserialize:
--   "\\r" => "\r"
--   "\\n" => "\n"
--   "\\\\" => "\\"
--
-- @param var The value.
function MWServer:serialize( var )
	local done = {}

	local function isInteger( var, max )
		return type(var) == 'number'
			and math.floor( var ) == var
			and var >= -max
			and var < max
	end

	local function recursiveEncode( var, level )
		local t = type( var )
		if t == 'nil' then
			return 'N;'
		elseif t == 'number' then
			if isInteger( var, self.intMax ) then
				return 'i:' .. string.format( '%d', var ) .. ';'
			elseif var < math.huge and var > -math.huge then
				return 'd:' .. string.format( '%.17g', var ) .. ';'
			elseif var == math.huge then
				return 'd:INF;'
			elseif var == -math.huge then
				return 'd:-INF;'
			else
				return 'd:NAN;'
			end
		elseif t == 'string' then
			return 's:' .. string.len( var ) .. ':"' .. var .. '";'
		elseif t == 'boolean' then
			if var then
				return 'b:1;'
			else
				return 'b:0;'
			end
		elseif t == 'table' then
			if done[var] then
				error("Cannot pass circular reference to PHP")
			end
			done[var] = true
			local buf = { '' }
			local numElements = 0
			local seen = {}
			for key, value in pairs(var) do
				local k = key
				local t = type( k )

				-- Convert integers in range to look like standard integers.
				-- Use tostring() for the rest. Reject all other non-strings.
				if isInteger( k, self.intKeyMax ) then
					k = string.format( '%d', k )
				elseif t == 'number' then
					k = tostring( k );
				elseif t ~= 'string' then
					error("Cannot use " .. t .. " as an array key when passing data from Lua to PHP");
				end

				-- Zend PHP doesn't really care whether integer keys are serialized
				-- as ints or strings, it converts them correctly on unserialize.
				-- But HHVM does depend on it, so keep doing it for now.
				local n = nil
				if k == '0' or k:match( '^-?[1-9]%d*$' ) then
					n = tonumber( k )
					if n == -9223372036854775808 and k ~= '-9223372036854775808' then
						-- Bad edge rounding
						n = nil
					end
				end
				if isInteger( n, self.intKeyMax ) then
					buf[#buf + 1] = 'i:' .. k .. ';'
				else
					buf[#buf + 1] = recursiveEncode( k, level + 1 )
				end

				-- Detect collisions, e.g. { [0] = 'foo', ["0"] = 'bar' }
				if seen[k] then
					error( 'Collision for array key ' .. k .. ' when passing data from Lua to PHP' );
				end
				seen[k] = true

				buf[#buf + 1] = recursiveEncode( value, level + 1 )
				numElements = numElements + 1
			end
			buf[1] = 'a:' .. numElements .. ':{'
			buf[#buf + 1] = '}'
			return table.concat(buf)
		elseif t == 'function' then
			local id
			if self.xchunks[var] then
				id = self.xchunks[var]
			else
				id = self:addChunk(var)
			end
			return 'O:42:"Scribunto_LuaStandaloneInterpreterFunction":2:{s:13:"interpreterId";i:' ..
				self.interpreterId .. ';s:2:"id";i:' .. id .. ';}'
		elseif t == 'thread' then
			error("Cannot pass thread to PHP")
		elseif t == 'userdata' then
			error("Cannot pass userdata to PHP")
		else
			error("Cannot pass unrecognised type to PHP")
		end
	end

	return recursiveEncode( var, 0 ):gsub( '[\r\n\\]', serialize_replacements )
end

--- Convert a Lua expression string to its corresponding value.
-- Convert any references of the form chunk[id] to the corresponding function
-- values.
function MWServer:unserialize( text )
	local func = loadstring( 'return ' .. text )
	if not func then
		self:internalError( "MWServer:unserialize: invalid chunk" )
	end
	-- Don't waste JIT cache space by storing every message in it
	if jit then
		jit.off( func )
	end
	setfenv( func, { chunks = self.chunks } )
	return func()
end

--- Decode a message header.
-- @param header The header string
-- @return The body length
function MWServer:decodeHeader( header )
	local length = string.sub( header, 1, 8 )
	local check = string.sub( header, 9, 16 )
	if not string.match( length, '^%x+$' ) or not string.match( check, '^%x+$' ) then
		self:internalError( "Error decoding message header: " .. length .. '/' .. check )
	end
	length = tonumber( length, 16 )
	check = tonumber( check, 16 )
	if length * 2 - 1 ~= check then
		self:internalError( "Error decoding message header" )
	end
	return length
end

--- Get a traceback similar to the one from debug.traceback(), but as a table
-- rather than formatted as a string
--
-- @param The level to start at: 1 for the function that called getStructuredTrace()
-- @return A table with the backtrace information
function MWServer:getStructuredTrace( level )
	level = level + 1
	local trace = {}
	while true do
		local rawInfo = debug.getinfo( level, 'nSl' )
		if rawInfo == nil then
			break
		end
		local info = {}
		for i, key in ipairs({'short_src', 'what', 'currentline', 'name', 'namewhat', 'linedefined'}) do
			info[key] = rawInfo[key]
		end
		if string.match( info['short_src'], '/MWServer.lua$' ) then
			info['short_src'] = 'MWServer.lua'
		end
		if string.match( rawInfo['short_src'], '/mw_main.lua$' ) then
			info['short_src'] = 'mw_main.lua'
		end
		table.insert( trace, info )
		level = level + 1
	end
	return trace
end

--- Create a table to be used as a restricted environment, based on the current
-- global environment.
--
-- @return The environment table
function MWServer:newEnvironment()
	local allowedGlobals = {
		-- base
		"assert",
		"error",
		"getmetatable",
		"ipairs",
		"next",
		"pairs",
		"pcall",
		"rawequal",
		"rawget",
		"rawset",
		"select",
		"setmetatable",
		"tonumber",
		"type",
		"unpack",
		"xpcall",
		"_VERSION",
		-- libs
		"table",
		"math"
	}

	local env = {}
	for i = 1, #allowedGlobals do
		env[allowedGlobals[i]] = mw.clone( _G[allowedGlobals[i]] )
	end

	-- Cloning 'string' doesn't work right, because strings still use the old
	-- 'string' as the metatable. So just copy it.
	env.string = string

	env._G = env
	env.tostring = function( val )
		return self:tostring( val )
	end
	env.string.dump = nil
	env.setfenv, env.getfenv = mw.makeProtectedEnvFuncs(
		self.protectedEnvironments, self.protectedFunctions )
	env.debug = {
		traceback = debug.traceback
	}
	env.os = {
		date = os.date,
		difftime = os.difftime,
		time = os.time,
		clock = os.clock
	}
	return env
end

--- An implementation of tostring() which does not expose pointers.
function MWServer:tostring(val)
	local mt = getmetatable( val )
	if mt and mt.__tostring then
		return mt.__tostring(val)
	end
	local typeName = type(val)
	local nonPointerTypes = {number = true, string = true, boolean = true, ['nil'] = true}
	if nonPointerTypes[typeName] then
		return tostring(val)
	else
		return typeName
	end
end

return MWServer
