local testframework = require( 'Module:TestFramework' )

local function setfenv1()
	local ok, err = pcall( function()
		setfenv( 2, {} )
	end )
	if not ok then
		err = string.gsub( err, '^%S+:%d+: ', '' )
		error( err )
	end
end

local function getfenv1()
	local env
	pcall( function()
		env = getfenv( 2 )
	end )
	return env
end

return testframework.getTestProvider( {
	{ name = 'setfenv on a C function', func = setfenv1,
	  expect = "'setfenv' cannot set the requested environment, it is protected",
	},
	{ name = 'getfenv on a C function', func = getfenv1,
	  expect = { nil },
	},
	{ name = 'Invalid array key (table)', func = mw.var_export,
	  args = { { [{}] = 1 } },
	  expect = 'Cannot use table as an array key when passing data from Lua to PHP',
	},
	{ name = 'Invalid array key (boolean)', func = mw.var_export,
	  args = { { [true] = 1 } },
	  expect = 'Cannot use boolean as an array key when passing data from Lua to PHP',
	},
	{ name = 'Invalid array key (function)', func = mw.var_export,
	  args = { { [tostring] = 1 } },
	  expect = 'Cannot use function as an array key when passing data from Lua to PHP',
	},
	{ name = 'Unusual array key (float)', func = mw.var_export,
	  args = { { [1.5] = 1 } },
	  expect = { "array ( '1.5' => 1, )" }
	},
	{ name = 'Unusual array key (inf)', func = mw.var_export,
	  args = { { [math.huge] = 1 } },
	  expect = { "array ( 'inf' => 1, )" }
	},
	{ name = 'Unusual array key ("00")', func = mw.var_export,
	  args = { { ["00"] = "zero zero" } },
	  expect = { "array ( '00' => 'zero zero', )" }
	},
	{ name = 'Unusual array key ("0.0")', func = mw.var_export,
	  args = { { ["0.0"] = "zero . zero" } },
	  expect = { "array ( '0.0' => 'zero . zero', )" }
	},
	{ name = 'Unusual array key ("01")', func = mw.var_export,
	  args = { { ["01"] = "zero one" } },
	  expect = { "array ( '01' => 'zero one', )" }
	},
	{ name = 'Unusual array key ("-9223372036854775808")', func = mw.var_export,
	  args = { { ["-9223372036854775808"] = "min" } },
	  expect = { "array ( -9223372036854775808 => 'min', )" }
	},
	{ name = 'Unusual array key (-9223372036854775808)', func = mw.var_export,
	  args = { { [-9223372036854775808] = "min" } },
	  expect = { "array ( -9223372036854775808 => 'min', )" }
	},
	{ name = 'Unusual array key ("-9223372036854775809")', func = mw.var_export,
	  args = { { ["-9223372036854775809"] = "min - 1" } },
	  expect = { "array ( '-9223372036854775809' => 'min - 1', )" }
	},
} )
