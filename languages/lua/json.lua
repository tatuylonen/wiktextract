-- Utility module for turning a lua table into a JSON string. The key export
-- here is the toJSON function. The code is taken from functionality in English
-- wiktionary modules, stored locally here so that it can be used with any other
-- language's wiktionary dump.

local export = {}

-- Function copied from https://en.wiktionary.org/wiki/Module:table
function export.deepcopy(orig, noMetatable, rawCopy, keepLoadedData)
	local already_seen = {}
	
	local function dc(orig, includeMetatable)
		if keepLoadedData then
			local mt = getmetatable(orig)
			if mt and mt.mw_loadData then
				return orig
			end
		end
		if type(orig) == "table" then
			if not already_seen[orig] then
				local copy = {}
				already_seen[orig] = copy
				for key, value in pairs(orig) do
					copy[dc(key, includeMetatable)] = dc(value, includeMetatable)
				end
				if includeMetatable then
					local mt = getmetatable(orig)
					if type(mt) == "table" and (
						(not mt.mw_loadData) or
						(mt.mw_loadData and rawCopy)
					) then 
						setmetatable(copy, dc(mt, includeMetatable))
					end
				end
			end
			return already_seen[orig]
		else
			return orig
		end
	end
	
	return dc(orig, not noMetatable)
end

-- The rest of this file is copied from
-- https://en.wiktionary.org/wiki/Module:JSON. The only change is that in
-- toJSON, val is preemptively deepcopied.

-- Given a finite real number x, returns a string containing its JSON
-- representation, with enough precision that it *should* round-trip correctly
-- (depending on the well-behavedness of the system on the other end).
function export.json_fromNumber(x)
	if type(x) ~= 'number' then
		error('Not of type "number": ' .. x .. ' (' .. type(x) .. ')')
	end
	if x ~= x or x == math.huge or x == -math.huge then
		error('Not a finite real number: ' .. x)
	end
	return string.format("%.17g", x)
end

-- This function makes an effort to convert an arbitrary Lua value to a string
-- containing a JSON representation of it. It's not intended to be very robust,
-- but may be useful for prototyping.
function export.toJSON(val, opts)
	opts = opts or {}
	
	val = export.deepcopy(val)

	local function converter(val)
		if type(val) == 'nil' then
			return 'null'
		elseif type(val) == 'boolean' then
			return val and 'true' or 'false'
		elseif type(val) == 'number' then
			return export.json_fromNumber(val)
		elseif type(val) == 'string' then
			return export.json_fromString(val)
		elseif type(val) == 'table' then
			-- If the table has a toJSON member function, call that.
			if val.toJSON then
				return val:toJSON()
			else
				return export.json_fromTable(val, converter)
			end
		else
			error('Unsupported type: ' .. type(val))
		end
	end
	
	return converter(val)
end

local escape_char_map = {
	["\\"] = "\\\\",
	["\""] = "\\\"",
	["\b"] = "\\b",
	["\f"] = "\\f",
	["\n"] = "\\n",
	["\r"] = "\\r",
	["\t"] = "\\t",
}

local function escape_char(c)
	return escape_char_map[c] or string.format("\\u%04X", mw.ustring.codepoint(c))
end

-- Given a string, escapes any illegal characters and wraps it in double-quotes.
-- Raises an error if the string is not valid UTF-8.
function export.json_fromString(s)
	if type(s) ~= 'string' or not mw.ustring.isutf8(s) then
		error('Not a valid UTF-8 string: ' .. s)
	end
	
	-- U+2029 (LINE SEPARATOR, \226\128\168 in UTF-8)
	-- and U+2028 (PARAGRAPH SEPARATOR, \226\128\169 in UTF-8) are allowed
	-- in JSON, but must be escaped for compatibility with JavaScript.
	s = mw.ustring.gsub(s, '[\\"%c\226\128\168\226\128\169]', escape_char)
	
	return '"' .. s .. '"'
end

-- Given a table, treats it as an array and assembles its values in the form
-- '[ v1, v2, v3 ]'. Optionally takes a function to JSONify the values before
-- assembly; if that function is omitted, then the values should already be
-- strings containing valid JSON data.
function export.json_arrayFromTable(val, converter)
	converter = converter or function (x) return x end
	
	-- If `val` comes from mw.loadData() then #val is always 0, so deep copy to avoid this.
	val = export.deepcopy(val)
	
	local ret = {}
	for i = 1, #val do
		elem = converter(val[i])
		if elem ~= nil then
			table.insert(ret, elem)
		end
	end
	
	if #ret == 0 then
		return '[]'
	end
	
	return '[ ' .. table.concat(ret, ", ") .. ' ]'
end

-- Given a table whose keys are all strings, assembles its keys and values in
-- the form '{ "k1": v1, "k2": v2, "k3": v3 }'. Optionally takes a function to
-- JSONify the values before assembly; if that function is omitted, then the
-- values should already be strings containing valid JSON data. (The keys, by
-- contrast, should just be regular Lua strings; they will be passed to this
-- module's jsonStringFromString.)
function export.json_fromTable(val, converter)
	converter = converter or function (x) return x end
	
	local as_object = {}
	local string_key = false
	
	for key, value in pairs(val) do
		value = converter(value)
		
		if type(key) ~= "number" then
			string_key = true
		end
		
		if value ~= nil then
			key = export.json_fromString(tostring(key))
			table.insert(as_object, key .. ' : ' .. value)
		end
	end
	
	if string_key then
		return '{' .. table.concat(as_object, ", ") .. '}'
	else
		return export.json_arrayFromTable(val, converter)
	end
end

return export
