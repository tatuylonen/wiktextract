--[[
-- A package library similar to the one that comes with Lua 5.1, but without
-- the local filesystem access. Based on Compat-5.1 which comes with the
-- following license notice:
--
-- Copyright © 2004-2006 The Kepler Project.
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy of
-- this software and associated documentation files (the "Software"), to deal in
-- the Software without restriction, including without limitation the rights to
-- use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
-- the Software, and to permit persons to whom the Software is furnished to do so,
-- subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
-- FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
-- COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
-- IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
-- CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
--]]


local assert, error, ipairs, setmetatable, type = assert, error, ipairs, setmetatable, type
local format = string.format

--
-- avoid overwriting the package table if it's already there
--
package = package or {}
local _PACKAGE = package

package.loaded = package.loaded or {}
package.loaded.debug = debug
package.loaded.string = string
package.loaded.math = math
package.loaded.io = io
package.loaded.os = os
package.loaded.table = table
package.loaded._G = _G
package.loaded.coroutine = coroutine
package.loaded.package = package
local _LOADED = package.loaded

--
-- avoid overwriting the package.preload table if it's already there
--
package.preload = package.preload or {}
local _PRELOAD = package.preload

--
-- check whether library is already loaded
--
local function loader_preload (name)
	assert (type(name) == "string", format (
		"bad argument #1 to 'require' (string expected, got %s)", type(name)))
	assert (type(_PRELOAD) == "table", "'package.preload' must be a table")
	return _PRELOAD[name]
end

-- create 'loaders' table
package.loaders = package.loaders or { loader_preload }
local _LOADERS = package.loaders

--
-- iterate over available loaders
--
local function load (name, loaders)
	-- iterate over available loaders
	assert (type (loaders) == "table", "'package.loaders' must be a table")
	for i, loader in ipairs (loaders) do
		local f = loader (name)
		if f then
			return f
		end
	end
	error (format ("module '%s' not found", name))
end

-- sentinel
local sentinel = function () end

--
-- require
--
function _G.require (modname)
	assert (type(modname) == "string", format (
		"bad argument #1 to 'require' (string expected, got %s)", type(modname)))
	local p = _LOADED[modname]
	if p then -- is it there?
		if p == sentinel then
			error (format ("loop or previous error loading module '%s'", modname))
		end
		return p -- package is already loaded
	end
	local init = load (modname, _LOADERS)
	_LOADED[modname] = sentinel
	local actual_arg = _G.arg
	_G.arg = { modname }
	local res = init (modname)
	if res then
		_LOADED[modname] = res
	end
	_G.arg = actual_arg
	if _LOADED[modname] == sentinel then
		_LOADED[modname] = true
	end
	return _LOADED[modname]
end


--
-- package.seeall function
--
function _PACKAGE.seeall (module)
	local t = type(module)
	assert (t == "table", "bad argument #1 to package.seeall (table expected, got "..t..")")
	local meta = getmetatable (module)
	if not meta then
		meta = {}
		setmetatable (module, meta)
	end
	meta.__index = _G
end
