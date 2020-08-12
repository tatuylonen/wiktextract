--[[
	Tests for the libraryUtil module

	@license GNU GPL v2+
	@author Mr. Stradivarius < misterstrad@gmail.com >
]]

local testframework = require 'Module:TestFramework'

local util = require( 'libraryUtil' )
local checkType = util.checkType
local checkTypeMulti = util.checkTypeMulti
local checkTypeForIndex = util.checkTypeForIndex
local checkTypeForNamedArg = util.checkTypeForNamedArg
local makeCheckSelfFunction = util.makeCheckSelfFunction

local function testExpectTypes( arg, expectTypes )
	pcall( checkTypeMulti, 'myFunc', 1, arg, expectTypes )
	return unpack( expectTypes )
end

local function testCheckSelf( self, method, ... )
	local checkSelf = makeCheckSelfFunction( ... )
	return checkSelf( self, method )
end

local testObject = {}

-- Tests
local tests = {
	-- checkType
	{ name = 'checkType, valid', func = checkType, type='ToString',
	  args = { 'myFunc', 1, 'foo', 'string' },
	  expect = { nil }
	},
	{ name = 'checkType, invalid', func = checkType, type='ToString',
	  args = { 'myFunc', 1, 9, 'string' },
	  expect = "bad argument #1 to 'myFunc' (string expected, got number)"
	},
	{ name = 'checkType, nil valid', func = checkType, type='ToString',
	  args = { 'myFunc', 1, nil, 'string', true },
	  expect = { nil }
	},
	{ name = 'checkType, nil invalid', func = checkType, type='ToString',
	  args = { 'myFunc', 1, nil, 'string', false },
	  expect = "bad argument #1 to 'myFunc' (string expected, got nil)"
	},
	{ name = 'checkType, boolean', func = checkType, type='ToString',
	  args = { 'myFunc', 1, true, 'boolean' },
	  expect = { nil }
	},
	{ name = 'checkType, table', func = checkType, type='ToString',
	  args = { 'myFunc', 1, {}, 'table' },
	  expect = { nil }
	},
	{ name = 'checkType, function', func = checkType, type='ToString',
	  args = { 'myFunc', 1, function () return end, 'function' },
	  expect = { nil }
	},
	{ name = 'checkType, argument #2', func = checkType, type='ToString',
	  args = { 'myFunc', 2, 9, 'string' },
	  expect = "bad argument #2 to 'myFunc' (string expected, got number)"
	},
	{ name = 'checkType, name', func = checkType, type='ToString',
	  args = { 'otherFunc', 1, 9, 'string' },
	  expect = "bad argument #1 to 'otherFunc' (string expected, got number)"
	},

	-- checkTypeMulti
	{ name = 'checkTypeMulti, single valid', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, 'foo', { 'string' } },
	  expect = { nil }
	},
	{ name = 'checkTypeMulti, single type invalid (1)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, 9, { 'string' } },
	  expect = "bad argument #1 to 'myFunc' (string expected, got number)"
	},
	{ name = 'checkTypeMulti, single type invalid (2)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, nil, { 'string' } },
	  expect = "bad argument #1 to 'myFunc' (string expected, got nil)"
	},
	{ name = 'checkTypeMulti, multiple types valid (1)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, 'foo', { 'string', 'number', 'table' } },
	  expect = { nil }
	},
	{ name = 'checkTypeMulti, multiple types valid (2)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, 9, { 'string', 'number', 'table' } },
	  expect = { nil }
	},
	{ name = 'checkTypeMulti, multiple types valid (3)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, {}, { 'string', 'number', 'table' } },
	  expect = { nil }
	},
	{ name = 'checkTypeMulti, multiple types invalid (1)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, true, { 'string', 'number', 'table' } },
	  expect = "bad argument #1 to 'myFunc' (string, number or table expected, got boolean)"
	},
	{ name = 'checkTypeMulti, multiple types invalid (2)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, nil, { 'string', 'number', 'table' } },
	  expect = "bad argument #1 to 'myFunc' (string, number or table expected, got nil)"
	},
	{ name = 'checkTypeMulti, multiple types invalid (3)', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, function () return end, { 'string', 'number', 'table' } },
	  expect = "bad argument #1 to 'myFunc' (string, number or table expected, got function)"
	},
	{ name = 'checkTypeMulti, two types invalid', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, {}, { 'string', 'number' } },
	  expect = "bad argument #1 to 'myFunc' (string or number expected, got table)"
	},
	{ name = 'checkTypeMulti, type order', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 1, true, { 'table', 'number', 'string' } },
	  expect = "bad argument #1 to 'myFunc' (table, number or string expected, got boolean)"
	},
	{ name = 'checkTypeMulti, argument #2', func = checkTypeMulti, type='ToString',
	  args = { 'myFunc', 2, 9, { 'string' } },
	  expect = "bad argument #2 to 'myFunc' (string expected, got number)"
	},
	{ name = 'checkTypeMulti, other name', func = checkTypeMulti, type='ToString',
	  args = { 'otherFunc', 1, 9, { 'string' } },
	  expect = "bad argument #1 to 'otherFunc' (string expected, got number)"
	},
	{ name = 'checkTypeMulti, expectTypes not altered (1)', func = testExpectTypes, type='ToString',
	  args = { 'foo', { 'string', 'number', 'table' } },
	  expect = { 'string', 'number', 'table' }
	},
	{ name = 'checkTypeMulti, expectTypes not altered (2)', func = testExpectTypes, type='ToString',
	  args = { true, { 'string', 'number', 'table' } },
	  expect = { 'string', 'number', 'table' }
	},
	{ name = 'checkTypeMulti, expectTypes not altered (3)', func = testExpectTypes, type='ToString',
	  args = { 'foo', { 'string' } },
	  expect = { 'string' }
	},
	{ name = 'checkTypeMulti, expectTypes not altered (4)', func = testExpectTypes, type='ToString',
	  args = { true, { 'string' } },
	  expect = { 'string' }
	},

	-- checkTypeForIndex
	{ name = 'checkTypeForIndex, valid', func = checkTypeForIndex, type='ToString',
	  args = { 'foo', 'bar', 'string' },
	  expect = { nil }
	},
	{ name = 'checkTypeForIndex, invalid (1)', func = checkTypeForIndex, type='ToString',
	  args = { 'foo', 9, 'string' },
	  expect = "value for index 'foo' must be string, number given"
	},
	{ name = 'checkTypeForIndex, invalid (2)', func = checkTypeForIndex, type='ToString',
	  args = { 'foo', 9, 'string' },
	  expect = "value for index 'foo' must be string, number given"
	},
	{ name = 'checkTypeForIndex, other index', func = checkTypeForIndex, type='ToString',
	  args = { 'bar', 9, 'string' },
	  expect = "value for index 'bar' must be string, number given"
	},

	-- checkTypeForNamedArg
	{ name = 'checkTypeForNamedArg, valid', func = checkTypeForNamedArg, type='ToString',
	  args = { 'myFunc', 'myArg', 'foo', 'string' },
	  expect = { nil }
	},
	{ name = 'checkTypeForNamedArg, invalid', func = checkTypeForNamedArg, type='ToString',
	  args = { 'myFunc', 'myArg', 9, 'string' },
	  expect = "bad named argument myArg to 'myFunc' (string expected, got number)"
	},
	{ name = 'checkTypeForNamedArg, nil valid', func = checkTypeForNamedArg, type='ToString',
	  args = { 'myFunc', 'myArg', nil, 'string', true },
	  expect = { nil }
	},
	{ name = 'checkTypeForNamedArg, nil invalid', func = checkTypeForNamedArg, type='ToString',
	  args = { 'myFunc', 'myArg', nil, 'string', false },
	  expect = "bad named argument myArg to 'myFunc' (string expected, got nil)"
	},
	{ name = 'checkTypeForNamedArg, other function', func = checkTypeForNamedArg, type='ToString',
	  args = { 'otherFunc', 'myArg', 9, 'string' },
	  expect = "bad named argument myArg to 'otherFunc' (string expected, got number)"
	},
	{ name = 'checkTypeForNamedArg, other argument', func = checkTypeForNamedArg, type='ToString',
	  args = { 'myFunc', 'otherArg', 9, 'string' },
	  expect = "bad named argument otherArg to 'myFunc' (string expected, got number)"
	},

	-- makeCheckSelfFunction
	{ name = 'makeCheckSelfFunction, valid', func = testCheckSelf, type='ToString',
	  args = { testObject, 'myMethod', 'myLibrary', 'myObject', testObject, 'test object' },
	  expect = { nil }
	},
	{ name = 'makeCheckSelfFunction, invalid (1)', func = testCheckSelf, type='ToString',
	  args = { {}, 'myMethod', 'myLibrary', 'myObject', testObject, 'test object' },
	  expect = 'myLibrary: invalid test object. Did you call myMethod with a dot instead ' ..
		'of a colon, i.e. myObject.myMethod() instead of myObject:myMethod()?'
	},
	{ name = 'makeCheckSelfFunction, invalid (2)', func = testCheckSelf, type='ToString',
	  args = { 'foo', 'myMethod', 'myLibrary', 'myObject', testObject, 'test object' },
	  expect = 'myLibrary: invalid test object. Did you call myMethod with a dot instead ' ..
		'of a colon, i.e. myObject.myMethod() instead of myObject:myMethod()?'
	},
	{ name = 'makeCheckSelfFunction, other method', func = testCheckSelf, type='ToString',
	  args = { {}, 'otherMethod', 'myLibrary', 'myObject', testObject, 'test object' },
	  expect = 'myLibrary: invalid test object. Did you call otherMethod with a dot instead ' ..
		'of a colon, i.e. myObject.otherMethod() instead of myObject:otherMethod()?'
	},
	{ name = 'makeCheckSelfFunction, other library', func = testCheckSelf, type='ToString',
	  args = { {}, 'myMethod', 'otherLibrary', 'myObject', testObject, 'test object' },
	  expect = 'otherLibrary: invalid test object. Did you call myMethod with a dot instead ' ..
		'of a colon, i.e. myObject.myMethod() instead of myObject:myMethod()?'
	},
	{ name = 'makeCheckSelfFunction, other object', func = testCheckSelf, type='ToString',
	  args = { {}, 'myMethod', 'otherLibrary', 'otherObject', testObject, 'test object' },
	  expect = 'otherLibrary: invalid test object. Did you call myMethod with a dot instead ' ..
		'of a colon, i.e. otherObject.myMethod() instead of otherObject:myMethod()?'
	},
	{ name = 'makeCheckSelfFunction, other description', func = testCheckSelf, type='ToString',
	  args = { {}, 'myMethod', 'myLibrary', 'myObject', testObject, 'test object' },
	  expect = 'myLibrary: invalid test object. Did you call myMethod with a dot instead ' ..
		'of a colon, i.e. myObject.myMethod() instead of myObject:myMethod()?'
	},
}

return testframework.getTestProvider( tests )
