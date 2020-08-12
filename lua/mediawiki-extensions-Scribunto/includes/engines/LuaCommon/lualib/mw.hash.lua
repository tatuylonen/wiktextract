local hash = {}
local php

local util = require 'libraryUtil'
local checkType = util.checkType

function hash.listAlgorithms()
	return php.listAlgorithms()
end

function hash.hashValue( algo, value )
	checkType( 'hashValue', 1, algo, 'string' )
	checkType( 'hashValue', 2, value, 'string' )

	return php.hashValue( algo, value )
end

function hash.setupInterface()
	-- Boilerplate
	php = mw_interface
	mw_interface = nil

	-- Register this library in the "mw" global
	mw = mw or {}
	mw.hash = hash

	package.loaded['mw.hash'] = hash
end

return hash
