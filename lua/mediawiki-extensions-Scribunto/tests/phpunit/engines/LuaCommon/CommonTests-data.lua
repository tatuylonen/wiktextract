-- This data is valid
local t = {
	["true"] = true,
	["false"] = false,
	NaN = 0/0,
	inf = 1/0,
	num = 12.5,
	str = "foo bar",
	table = {
		"one", "two", "three", foo = "bar"
	}
}

-- Duplicate values
t.table2 = t.table

-- Make sure recursion is correctly handled, too
t.t = t

return t
