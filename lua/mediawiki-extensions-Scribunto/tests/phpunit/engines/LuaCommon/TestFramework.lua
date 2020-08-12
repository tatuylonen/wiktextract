local testframework = testframework or {}

-- Return a string represetation of a value, including the deep structure of a table
local function deepToString( val, indent, done )
	done = done or {}
	indent = indent or 0

	local tp = type( val )
	if tp == 'string' then
		return string.format( "%q", val )
	elseif tp == 'table' then
		if done[val] then return '{ ... }' end
		done[val] = true
		local sb = { '{\n' }
		local donekeys = {}
		for key, value in ipairs( val ) do
			donekeys[key] = true
			sb[#sb + 1] = string.rep( " ", indent + 2 )
			sb[#sb + 1] = deepToString( value, indent + 2, done )
			sb[#sb + 1] = ",\n"
		end
		local keys = {}
		for key in pairs( val ) do
			if not donekeys[key] then
				keys[#keys + 1] = key
			end
		end
		table.sort( keys )
		for i = 1, #keys do
			local key = keys[i]
			sb[#sb + 1] = string.rep( " ", indent + 2 )
			if type( key ) == 'table' then
				sb[#sb + 1] = '[{ ... }] = '
			else
				sb[#sb + 1] = '['
				sb[#sb + 1] = deepToString( key, indent + 3, done )
				sb[#sb + 1] = '] = '
			end
			sb[#sb + 1] = deepToString( val[key], indent + 2, done )
			sb[#sb + 1] = ",\n"
		end
		sb[#sb + 1] = string.rep( " ", indent )
		sb[#sb + 1] = "}"
		return table.concat( sb )
	else
		return tostring( val )
	end
end
testframework.deepToString = deepToString

-- Test whether two objects are equal, including the deep structure of a table.
-- Returns 4 values:
--  boolean  equal?
--  list     key path to first inequality
--  mixed    value from 'a' for key path
--  mixed    value from 'b' for key path
local function deepEquals( a, b, keypath, done )
	-- Simple equality
	if a == b then
		return true
	end

	keypath = keypath or {}
	done = done or {}

	-- Must be equal types to be equal
	local tp = type( a )
	if type( b ) ~= tp then
		return false, keypath, a, b
	end

	-- Special tests for certain types

	if tp == 'number' then
		-- For test framework purposes, NaNs are equivalent. Lua has no
		-- standard "isNaN" function, but only NaN will return true for
		-- "x ~= x".
		if a ~= a and b ~= b then
			return true
		end

		return false, keypath, a, b
	end

	if tp == 'table' then
		-- To avoid recursion, see if we've seen this pair of tables before. If
		-- so, they must be equal or the test would have failed the first time we saw them.
		done[a] = done[a] or {}
		done[b] = done[b] or {}
		if done[a][b] or done[b][a] then
			return true
		end

		-- Not seen before, record them and compare key by key.
		done[a][b] = true

		local n = #keypath + 1
		-- First, check if the values for all keys in 'a' are equal in 'b'.
		for k in pairs( a ) do
			keypath[n] = k
			local ok, kp, aa, bb = deepEquals( a[k], b[k], keypath, done )
			if not ok then
				return false, kp, aa, bb
			end
		end
		keypath[n] = nil

		-- Then check if there are any keys in 'b' that don't exist in 'a'.
		for k, v in pairs( b ) do
			if a[k] == nil then
				keypath[n] = k
				return false, keypath, nil, v
			end
		end

		-- Ok, all keys equal so it must match.
		return true
	end

	-- Ok, they're not equal
	return false, keypath, a, b
end
testframework.deepEquals = deepEquals

-- Skip a test (throws an error)
function testframework.markTestSkipped( message )
	error( 'SKIP: ' .. message, 0 )
end

---- Test types available ---
-- Each type has a formatter and an executor:
--  Formatters take 1 arg: expected return value from the function.
--  Executors take 2 args: function and arguments.
--  Both return a string. The test passes if the two strings match.
testframework.types = testframework.types or {}

-- Execute a function and assert expected results
-- Expected value is a list of return values, or a string error message
testframework.types.Normal = {
	format = function ( expect )
		if type( expect ) == 'string' then
			return 'ERROR: ' .. expect
		else
			return deepToString( expect )
		end
	end,
	exec = function ( func, args )
		local got = { pcall( func, unpack( args ) ) }
		if table.remove( got, 1 ) then
			return deepToString( got )
		else
			if string.sub( got[1], 1, 6 ) == 'SKIP: ' then
				error( got[1], 0 )
			end
			got = string.gsub( got[1], '^%S+:%d+: ', '' )
			return 'ERROR: ' .. got
		end
	end
}

-- Execute an iterator-returning function and assert expected results from each
-- iteration.
-- Expected value is a list of return value lists.
testframework.types.Iterator = {
	format = function ( expect )
		local sb = {}
		for i = 1, #expect do
			sb[i] = '[iteration ' .. i .. ']:\n' .. deepToString( expect[i] )
		end
		return table.concat( sb, '\n\n' )
	end,
	exec = function ( func, args )
		local sb = {}
		local i = 0
		local f, s, var = func( unpack( args ) )
		while true do
			local got = { f( s, var ) }
			var = got[1]
			if var == nil then break end
			i = i + 1
			sb[i] = '[iteration ' .. i .. ']:\n' .. deepToString( got )
		end
		return table.concat( sb, '\n\n' )
	end
}

-- Execute a function and assert expected results
-- Expected value is a list of return values, or a string error message
testframework.types.ToString = {
	format = function ( expect )
		if type( expect ) == 'string' then
			return 'ERROR: ' .. expect
		else
			local ret = {}
			for k, v in pairs( expect ) do
				ret[k] = tostring( v )
			end
			return deepToString( ret )
		end
	end,
	exec = function ( func, args )
		local got = { pcall( func, unpack( args ) ) }
		if table.remove( got, 1 ) then
			for k, v in pairs( got ) do
				got[k] = tostring( v )
			end
			return deepToString( got )
		else
			if string.sub( got[1], 1, 6 ) == 'SKIP: ' then
				error( got[1], 0 )
			end
			got = string.gsub( got[1], '^%S+:%d+: ', '' )
			return 'ERROR: ' .. got
		end
	end
}

-- This takes a list of tests to run, and returns the object used by PHP to
-- call them.
--
-- Each test is a table with the following keys:
--  name: Name of the test
--  expect: Table of results expected
--  func: Function to execute
--  args: (optional) Table of args to be unpacked and passed to the function
--  type: (optional) Formatter/Executor name, default "Normal"
function testframework.getTestProvider( tests )
	return {
		count = #tests,

		provide = function ( n )
			local t = tests[n]
			return n, t.name, testframework.types[t.type or 'Normal'].format( t.expect )
		end,

		run = function ( n )
			local t = tests[n]
			if not t then
				return 'Test ' .. name .. ' does not exist'
			end
			return testframework.types[t.type or 'Normal'].exec( t.func, t.args or {} )
		end,
	}
end

return testframework
