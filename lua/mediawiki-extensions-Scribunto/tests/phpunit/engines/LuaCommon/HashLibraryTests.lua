--[[
	Tests for the mw.hash module

	@license GNU GPL v2+
	@author Marius Hoch < hoo@online.de >
]]

local testframework = require 'Module:TestFramework'

local function testListAlgorithms()
	local algos = mw.hash.listAlgorithms()

	if type( algos ) ~= 'table' then
		return 'algo list was expected to be a table'
	end

	for i, v in ipairs( algos ) do
		if v == 'md5' then
			return true
		end
	end

	return 'md5 was expected to be in the algo list'
end

-- Tests
local tests = {
	{ name = 'mw.hash.listAlgorithms', func = testListAlgorithms,
	  expect = { true }
	},
	{ name = 'mw.hash.hashValue sha1', func = mw.hash.hashValue,
	  args = { 'sha1', 'abc' },
	  expect = { 'a9993e364706816aba3e25717850c26c9cd0d89d' }
	},
	{ name = 'mw.hash.hashValue md5', func = mw.hash.hashValue,
	  args = { 'md5', 'abc' },
	  expect = { '900150983cd24fb0d6963f7d28e17f72' }
	},
	{ name = 'mw.hash.hashValue bad argument type #1', func = mw.hash.hashValue,
	  args = { nil, 'a-string' },
	  expect = "bad argument #1 to 'hashValue' (string expected, got nil)"
	},
	{ name = 'mw.hash.hashValue bad argument type #2', func = mw.hash.hashValue,
	  args = { 'abc', 2 },
	  expect = "bad argument #2 to 'hashValue' (string expected, got number)"
	},
	{ name = 'mw.hash.hashValue bad algorithm', func = mw.hash.hashValue,
	  args = { 'not-a-hashing-algorithm', 'abc' },
	  expect = "Unknown hashing algorithm: not-a-hashing-algorithm"
	}
}

return testframework.getTestProvider( tests )
