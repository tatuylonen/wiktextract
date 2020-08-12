local p = {}
local php
local options

function p.setupInterface( opts )
	-- Boilerplate
	p.setupInterface = nil
	php = mw_interface
	mw_interface = nil
	options = opts

	-- Loaded dynamically, don't mess with globals like 'mw' or
	-- 'package.loaded'
end

function p.test()
	return options.test, php.test()
end

function p.setVal( frame )
	options.val = frame.args[1]
end

function p.getVal( frame )
	return tostring( options.val )
end

p.foobar = { val = "nope" }

return p
