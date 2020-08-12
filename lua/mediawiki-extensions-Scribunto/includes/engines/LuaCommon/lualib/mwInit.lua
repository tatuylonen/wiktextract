-- This file is for anything that needs to be set up before a Lua engine can
-- start. Things in this file may run more than once, so avoid putting anything
-- other than function definitions in it. Also, because this can run before
-- PHP can do anything, mw_interface is unavailable here.

mw = mw or {}

-- Extend pairs and ipairs to recognize __pairs and __ipairs, if they don't already
do
	local t = {}
	setmetatable( t, { __pairs = function() return 1, 2, 3 end } )
	local f = pairs( t )
	if f ~= 1 then
		local old_pairs = pairs
		pairs = function ( t )
			local mt = getmetatable( t )
			local f, s, var = ( mt and mt.__pairs or old_pairs )( t )
			return f, s, var
		end
		local old_ipairs = ipairs
		ipairs = function ( t )
			local mt = getmetatable( t )
			local f, s, var = ( mt and mt.__ipairs or old_ipairs )( t )
			return f, s, var
		end
	end
end

-- Reduce precision on os.clock to mitigate timing attacks
do
	local old_clock = os.clock
	os.clock = function ()
		local v = old_clock()
		return math.floor( v * 50000 + 0.5 ) / 50000
	end
end

--- Do a "deep copy" of a table or other value.
function mw.clone( val )
	local tableRefs = {}
	local function recursiveClone( val )
		if type( val ) == 'table' then
			-- Encode circular references correctly
			if tableRefs[val] ~= nil then
				return tableRefs[val]
			end

			local retVal
			retVal = {}
			tableRefs[val] = retVal

			-- Copy metatable
			if getmetatable( val ) then
				setmetatable( retVal, recursiveClone( getmetatable( val ) ) )
			end

			for key, elt in pairs( val ) do
				retVal[key] = recursiveClone( elt )
			end
			return retVal
		else
			return val
		end
	end
	return recursiveClone( val )
end

--- Make isolation-safe setfenv and getfenv functions
--
-- @param protectedEnvironments A table where the keys are protected environment
--    tables. These environments cannot be accessed with getfenv(), and
--    functions with these environments cannot be modified or accessed using
--    integer indexes to setfenv(). However, functions with these environments
--    can have their environment set with setfenv() with a function value
--    argument.
--
-- @param protectedFunctions A table where the keys are protected functions,
--    which cannot have their environments set by setfenv() with a function
--    value argument.
--
-- @return setfenv
-- @return getfenv
function mw.makeProtectedEnvFuncs( protectedEnvironments, protectedFunctions )
	local old_setfenv = setfenv
	local old_getfenv = getfenv

	local function my_setfenv( func, newEnv )
		if type( func ) == 'number' then
			local stackIndex = math.floor( func )
			if stackIndex <= 0 then
				error( "'setfenv' cannot set the global environment, it is protected", 2 )
			end
			if stackIndex > 10 then
				error( "'setfenv' cannot set an environment at a level greater than 10", 2 )
			end

			-- Add one because we are still in Lua and 1 is right here
			stackIndex = stackIndex + 1

			local env = old_getfenv( stackIndex )
			if env == nil or protectedEnvironments[ env ] then
				error( "'setfenv' cannot set the requested environment, it is protected", 2 )
			end
			func = old_setfenv( stackIndex, newEnv )
		elseif type( func ) == 'function' then
			if protectedFunctions[func] then
				error( "'setfenv' cannot be called on a protected function", 2 )
			end
			local env = old_getfenv( func )
			if env == nil or protectedEnvironments[ env ] then
				error( "'setfenv' cannot set the requested environment, it is protected", 2 )
			end
			old_setfenv( func, newEnv )
		else
			error( "'setfenv' can only be called with a function or integer as the first argument", 2 )
		end
		return func
	end

	local function my_getfenv( func )
		local env
		if type( func ) == 'number' then
			if func <= 0 then
				error( "'getfenv' cannot get the global environment" )
			end
			env = old_getfenv( func + 1 )
		elseif type( func ) == 'function' then
			env = old_getfenv( func )
		else
			error( "'getfenv' cannot get the global environment" )
		end

		if protectedEnvironments[env] then
			return nil
		else
			return env
		end
	end

	return my_setfenv, my_getfenv
end

return mw
