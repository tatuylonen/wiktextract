local uri = {}
local urifuncs = {}
local urimt = {}
local php

local util = require 'libraryUtil'
local checkType = util.checkType
local checkTypeForIndex = util.checkTypeForIndex

function uri.setupInterface( options )
	-- Boilerplate
	uri.setupInterface = nil
	php = mw_interface
	mw_interface = nil

	-- Store options
	php.options = options

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.uri = uri

	package.loaded['mw.uri'] = uri
end

local function rawencode( s, space )
	space = space or '%20'
	local ret = string.gsub( s, '([^a-zA-Z0-9_.~-])', function ( c )
		if c == ' ' then
			return space
		else
			return string.format( '%%%02X', string.byte( c, 1, 1 ) )
		end
	end );
	return ret
end

local function wikiencode( s )
	local ret = string.gsub( s, '([^a-zA-Z0-9!$()*,./:;@~_-])', function ( c )
		if c == ' ' then
			return '_'
		else
			return string.format( '%%%02X', string.byte( c, 1, 1 ) )
		end
	end );
	return ret
end

local function rawdecode( s )
	local ret = string.gsub( s, '%%(%x%x)', function ( hex )
		return string.char( tonumber( hex, 16 ) )
	end );
	return ret
end

function uri.encode( s, enctype )
	checkType( 'encode', 1, s, 'string' )

	enctype = string.upper( enctype or 'QUERY' )
	if enctype == 'QUERY' then
		return rawencode( s, '+' )
	elseif enctype == 'PATH' then
		return rawencode( s, '%20' )
	elseif enctype == 'WIKI' then
		return wikiencode( s )
	else
		error( "bad argument #2 to 'encode' (expected QUERY, PATH, or WIKI)", 2 )
	end
end

function uri.decode( s, enctype )
	checkType( 'decode', 1, s, 'string' )

	enctype = string.upper( enctype or 'QUERY' )
	if enctype == 'QUERY' then
		return rawdecode( string.gsub( s, '%+', ' ' ) )
	elseif enctype == 'PATH' then
		return rawdecode( s )
	elseif enctype == 'WIKI' then
		return rawdecode( string.gsub( s, '_', ' ' ) )
	else
		error( "bad argument #2 to 'decode' (expected QUERY, PATH, or WIKI)", 2 )
	end
end

function uri.anchorEncode( s )
	checkType( 'anchorEncode', 1, s, 'string' )
	return php.anchorEncode( s )
end

function uri.localUrl( page, query )
	checkType( 'localurl', 1, page, 'string' )
	if query ~= nil and type( query ) ~= 'string' and type( query ) ~= 'table' then
		checkType( 'localurl', 2, query, 'string or table' )
	end
	local url = php.localUrl( page, query )
	if not url then
		return nil
	end
	return uri.new( url )
end

function uri.fullUrl( page, query )
	checkType( 'fullurl', 1, page, 'string' )
	if query ~= nil and type( query ) ~= 'string' and type( query ) ~= 'table' then
		checkType( 'fullurl', 2, query, 'string or table' )
	end
	local url = php.fullUrl( page, query )
	if not url then
		return nil
	end
	return uri.new( url )
end

function uri.canonicalUrl( page, query )
	checkType( 'canonicalurl', 1, page, 'string' )
	if query ~= nil and type( query ) ~= 'string' and type( query ) ~= 'table' then
		checkType( 'canonicalurl', 2, query, 'string or table' )
	end
	local url = php.canonicalUrl( page, query )
	if not url then
		return nil
	end
	return uri.new( url )
end


function uri.new( s )
	if s == nil or type( s ) == 'string' then
		local obj = {
			-- Yes, technically all this does nothing.
			protocol = nil,
			user = nil,
			password = nil,
			host = nil,
			port = nil,
			path = nil,
			query = nil,
			fragment = nil,
		}
		setmetatable( obj, urimt )
		obj:parse( s or php.options.defaultUrl )
		return obj
	elseif type( s ) == 'table' then
		local obj = {
			protocol = s.protocol,
			user = s.user,
			password = s.password,
			host = s.host,
			port = s.port,
			path = s.path,
			query = mw.clone( s.query ),
			fragment = s.fragment,
		}
		setmetatable( obj, urimt )
		return obj
	else
		checkType( 'new', 1, s, 'string or table or nil' )
	end
end

function uri.validate( obj )
	checkType( 'validate', 1, obj, 'table' )

	local err = {}

	if obj.protocol then
		if type( obj.protocol ) ~= 'string' then
			err[#err+1] = '.protocol must be a string, not ' .. type( obj.protocol )
		elseif not string.match( obj.protocol, '^[^:/?#]+$' ) then
			err[#err+1] = 'invalid .protocol'
		end
	end

	if obj.user then
		if type( obj.user ) ~= 'string' then
			err[#err+1] = '.user must be a string, not ' .. type( obj.user )
		elseif not string.match( obj.user, '^[^:@/?#]*$' ) then
			err[#err+1] = 'invalid .user'
		end
	end

	if obj.password then
		if type( obj.password ) ~= 'string' then
			err[#err+1] = '.password must be a string, not ' .. type( obj.password )
		elseif not string.match( obj.password, '^[^:@/?#]*$' ) then
			err[#err+1] = 'invalid .password'
		end
	end

	if obj.host then
		if type( obj.host ) ~= 'string' then
			err[#err+1] = '.host must be a string, not ' .. type( obj.host )
		elseif not (
			-- Normal syntax
			string.match( obj.host, '^[^:/?#]*$' ) or
			-- IP-literal syntax
			string.match( obj.host, '^%[[^/?#%[%]@]+%]$' )
		) then
			err[#err+1] = 'invalid .host'
		end
	end

	if obj.port then
		if type( obj.port ) ~= 'number' or math.floor( obj.port ) ~= obj.port then
			err[#err+1] = '.port must be an integer, not ' .. type( obj.port )
		elseif obj.port < 1 or obj.port > 65535 then
			err[#err+1] = 'invalid .port'
		end
	end

	local authority = obj.user or obj.password or obj.host or obj.port
	if not obj.path then
		err[#err+1] = 'missing .path'
	elseif type( obj.path ) ~= 'string' then
		err[#err+1] = '.path must be a string, not ' .. type( obj.path )
	elseif authority and not ( obj.path == '' or string.match( obj.path, '^/[^?#]*$' ) ) then
		err[#err+1] = 'invalid .path'
	elseif not authority and not (
		obj.path == '' or
		obj.path == '/' or
		string.match( obj.path, '^/[^?#/][^?#]*$' ) or
		obj.protocol and string.match( obj.path, '^[^?#/][^?#]*$' ) or
		not obj.protocol and string.match( obj.path, '^[^?#/:]+$' ) or
		not obj.protocol and string.match( obj.path, '^[^?#/:]+/[^?#]*$' )
	) then
		err[#err+1] = 'invalid .path'
	end

	if obj.query and type( obj.query ) ~= 'table' then
		err[#err+1] = '.query must be a table, not ' .. type( obj.query )
	end

	if obj.fragment and type( obj.fragment ) ~= 'string' then
		err[#err+1] = '.fragment must be a string, not ' .. type( obj.fragment )
	end

	return #err == 0, table.concat( err, '; ' )
end

-- Lua tables are unsorted, but we want to preserve the insertion order.
-- So, track the insertion order explicitly.
local function makeQueryTable()
	local ret = {}
	local keys = {}
	local seenkeys = {}

	setmetatable( ret, {
		__newindex = function ( t, k, v )
			if seenkeys[k] and not t[k] then
				for i = 1, #keys do
					if keys[i] == k then
						table.remove( keys, i )
						break
					end
				end
			end
			seenkeys[k] = 1
			keys[#keys+1] = k
			rawset( t, k, v )
		end,
		__pairs = function ( t )
			local i, l = 0, #keys
			return function ()
				while i < l do
					i = i + 1
					local k = keys[i]
					if t[k] ~= nil then
						return k, t[k]
					end
				end
				return nil
			end
		end
	} )

	return ret
end

function uri.parseQueryString( s, i, j )
	checkType( 'parseQueryString', 1, s, 'string' )
	checkType( 'parseQueryString', 2, i, 'number', true )
	checkType( 'parseQueryString', 3, j, 'number', true )

	s = string.gsub( string.sub( s, i or 1, j or -1 ), '%+', ' ' )
	i = 1
	j = string.len( s )

	local qs = makeQueryTable()
	if string.sub( s, i, 1 ) == '?' then
		i = i + 1
	end
	while i <= j do
		local amp = string.find( s, '&', i, true )
		if not amp or amp > j then
			amp = j + 1
		end
		local eq = string.find( s, '=', i, true )
		local k, v
		if not eq or eq > amp then
			k = rawdecode( string.sub( s, i, amp - 1 ) )
			v = false
		else
			k = rawdecode( string.sub( s, i, eq - 1 ) )
			v = rawdecode( string.sub( s, eq + 1, amp - 1 ) )
		end
		if qs[k] then
			if type( qs[k] ) ~= 'table' then
				qs[k] = { qs[k], v }
			else
				table.insert( qs[k], v )
			end
		else
			qs[k] = v
		end
		i = amp + 1
	end
	return qs
end

function uri.buildQueryString( qs )
	checkType( 'buildQueryString', 1, qs, 'table' )

	local t = {}
	for k, v in pairs( qs ) do
		if type( v ) ~= 'table' then
			v = { v }
		end
		for i = 1, #v do
			t[#t+1] = '&'
			t[#t+1] = rawencode( k, '+' )
			if v[i] then
				t[#t+1] = '='
				t[#t+1] = rawencode( v[i], '+' )
			end
		end
	end
	return table.concat( t, '', 2 )
end

-- Fields mapped to whether they're handled by __index
local knownFields = {
	protocol = false,
	user = false,
	password = false,
	host = false,
	port = false,
	path = false,
	query = false,
	fragment = false,
	userInfo = true,
	hostPort = true,
	authority = true,
	queryString = true,
	relativePath = true,
}

local function pairsfunc( t, k )
	local v, f
	repeat
		k, f = next( knownFields, k )
		if k == nil then
			return nil
		end
		if f then
			v = t[k]
		else
			v = rawget( t, k )
		end
	until v ~= nil
	return k, v
end
function urimt:__pairs()
	return pairsfunc, self, nil
end

function urimt:__index( key )
	if urifuncs[key] then
		return urifuncs[key]
	end

	if key == 'userInfo' then
		local user = rawget( self, 'user' )
		local password = rawget( self, 'password' )
		if user and password then
			return user .. ':' .. password
		else
			return user
		end
	end

	if key == 'hostPort' then
		local host = rawget( self, 'host' )
		local port = rawget( self, 'port' )
		if port then
			return ( host or '' ) .. ':' .. port
		else
			return host
		end
	end

	if key == 'authority' then
		local info = self.userInfo
		local hostPort = self.hostPort
		if info then
			return info .. '@' .. ( hostPort or '' )
		else
			return hostPort
		end
	end

	if key == 'queryString' then
		local query = rawget( self, 'query' )
		if not query then
			return nil
		end
		return uri.buildQueryString( query )
	end

	if key == 'relativePath' then
		local ret = rawget( self, 'path' ) or ''
		local qs = self.queryString
		if qs then
			ret = ret .. '?' .. qs
		end
		local fragment = rawget( self, 'fragment' )
		if fragment then
			ret = ret .. '#' .. fragment
		end
		return ret
	end

	return nil
end

function urimt:__newindex( key, value )
	if key == 'userInfo' then
		local user, password = nil, nil
		if value then
			checkTypeForIndex( key, value, 'string' )
			local i = string.find( value, ':', 1, true )
			if i then
				user = string.sub( value, 1, i - 1 )
				password = string.sub( value, i + 1 )
			else
				user = value
			end
		end
		rawset( self, 'user', user )
		rawset( self, 'password', password )
		return
	end

	if key == 'hostPort' then
		local host, port = nil, nil
		if value then
			checkTypeForIndex( key, value, 'string' )

			-- IP-literal syntax, with and without a port
			host, port = string.match( value, '^(%[[^/?#%[%]@]+%]):(%d+)$' )
			if port then
				port = tonumber( port )
			end
			if not host then
				host = string.match( value, '^(%[[^/?#%[%]@]+%])$' )
			end
			-- Normal syntax
			if not host then
				local i = string.find( value, ':', 1, true )
				if i then
					host = string.sub( value, 1, i - 1 )
					port = tonumber( string.sub( value, i + 1 ) )
					if not port then
						error( string.format( "Invalid port in '%s'", value ), 2 )
					end
				else
					host = value
				end
			end
		end
		rawset( self, 'host', host )
		rawset( self, 'port', port )
		return
	end

	if key == 'authority' then
		if value then
			checkTypeForIndex( key, value, 'string' )
			local i = string.find( value, '@', 1, true )
			if i then
				self.userInfo = string.sub( value, 1, i - 1 )
				self.hostPort = string.sub( value, i + 1 )
			else
				self.userInfo = nil
				self.hostPort = value
			end
		else
			self.userInfo = nil
			self.hostPort = nil
		end
		return
	end

	if key == 'queryString' then
		if value then
			checkTypeForIndex( key, value, 'string' )
			rawset( self, 'query', uri.parseQueryString( value ) )
		else
			rawset( self, 'query', nil )
		end
		return
	end

	if key == 'relativePath' then
		local path, query, fragment = nil, nil, nil
		if value then
			checkTypeForIndex( key, value, 'string' )
			local i, j = nil, string.len( value )
			i = string.find( value, '#', 1, true )
			if i and i <= j then
				fragment = string.sub( value, i + 1, j )
				j = i - 1
			end
			i = string.find( value, '?', 1, true )
			if i and i <= j then
				query = uri.parseQueryString( string.sub( value, i + 1, j ) )
				j = i - 1
			end
			path = string.sub( value, 1, j )
		end
		rawset( self, 'path', path )
		rawset( self, 'query', query )
		rawset( self, 'fragment', fragment )
		return
	end

	if knownFields[key] then
		error( "index '" .. key .. "' is read only", 2 )
	end

	-- Default behavior
	knownFields[key] = false
	rawset( self, key, value )
end

function urimt:__tostring()
	local ret = ''
	local protocol = self.protocol
	local authority = self.authority
	if protocol then
		ret = protocol .. ':'
	end
	if authority then
		ret = ret .. '//' .. authority
	end
	return ret .. self.relativePath
end

urifuncs.validate = uri.validate

function urifuncs:parse( s )
	checkType( 'uri:parse', 1, s, 'string' )

	-- Since Lua's patterns can't do (...)?, we have to try with and without each part.
	local protocol, authority, relativePath = string.match( s, '^([^:/?#]+)://([^/?#]*)(.*)$' )
	if not ( protocol or authority or relativePath ) then
		authority, relativePath = string.match( s, '^//([^/?#]*)(.*)$' )
	end
	if not ( protocol or authority or relativePath ) then
		protocol, relativePath = string.match( s, '^([^:/?#]+):(.*)$' )
	end
	if not ( protocol or authority or relativePath ) then
		relativePath = s
	end

	-- Parse it into a temporary object, so if there's an error we didn't break the real one
	local tmp = { protocol = protocol }
	setmetatable( tmp, urimt )
	if not pcall( urimt.__newindex, tmp, 'authority', authority ) then
		error( 'Invalid port number in string', 2 )
	end
	tmp.relativePath = relativePath

	-- Check for validity
	local ok, err = uri.validate( tmp )
	if not ok then
		error( err, 2 )
	end

	-- Merge in fields
	if tmp.protocol then
		self.protocol = tmp.protocol
	end
	if tmp.user or tmp.password then
		self.user, self.password = tmp.user, tmp.password
	end
	if tmp.host then
		self.host = tmp.host
	end
	if tmp.port then
		self.port = tmp.port
	end
	if tmp.path then
		self.path = tmp.path
	end
	if tmp.query then
		self.query = tmp.query
	end
	if tmp.fragment then
		self.fragment = tmp.fragment
	end

	return self
end

function urifuncs:clone()
	return uri.new( self )
end

function urifuncs:extend( parameters )
	checkType( 'uri:extend', 1, parameters, 'table' )

	local query = self.query
	if not query then
		query = makeQueryTable()
		self.query = query
	end
	for k, v in pairs( parameters ) do
		query[k] = v
	end

	return self
end

-- Add all urifuncs as known fields
for k in pairs( urifuncs ) do
	knownFields[k] = true
end

return uri
