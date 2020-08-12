---
-- An implementation of the lua 5.2 bit32 library, in pure Lua

-- Note that in Lua, "x % n" is defined such that will always return a number
-- between 0 and n-1 for positive n. We take advantage of that a lot here.

local bit32 = {}

local function checkint( name, argidx, x, level )
	local n = tonumber( x )
	if not n then
		error( string.format(
			"bad argument #%d to '%s' (number expected, got %s)",
			argidx, name, type( x )
		), level + 1 )
	end
	return math.floor( n )
end

local function checkint32( name, argidx, x, level )
	local n = tonumber( x )
	if not n then
		error( string.format(
			"bad argument #%d to '%s' (number expected, got %s)",
			argidx, name, type( x )
		), level + 1 )
	end
	return math.floor( n ) % 0x100000000
end


function bit32.bnot( x )
	x = checkint32( 'bnot', 1, x, 2 )

	-- In two's complement, -x = not(x) + 1
	-- So not(x) = -x - 1
	return ( -x - 1 ) % 0x100000000
end


---
-- Logic tables for and/or/xor. We do pairs of bits here as a tradeoff between
-- table space and speed. If you change the number of bits, also change the
-- constants 2 and 4 in comb() below, and the initial value in bit32.band and
-- bit32.btest
local logic_and = {
	[0] = { [0] = 0, 0, 0, 0},
	[1] = { [0] = 0, 1, 0, 1},
	[2] = { [0] = 0, 0, 2, 2},
	[3] = { [0] = 0, 1, 2, 3},
}
local logic_or = {
	[0] = { [0] = 0, 1, 2, 3},
	[1] = { [0] = 1, 1, 3, 3},
	[2] = { [0] = 2, 3, 2, 3},
	[3] = { [0] = 3, 3, 3, 3},
}
local logic_xor = {
	[0] = { [0] = 0, 1, 2, 3},
	[1] = { [0] = 1, 0, 3, 2},
	[2] = { [0] = 2, 3, 0, 1},
	[3] = { [0] = 3, 2, 1, 0},
}

---
-- @param name string Function name
-- @param args table Function args
-- @param nargs number Arg count
-- @param s number Start value, 0-3
-- @param t table Logic table
-- @return number result
local function comb( name, args, nargs, s, t )
	for i = 1, nargs do
		args[i] = checkint32( name, i, args[i], 3 )
	end

	local pow = 1
	local ret = 0
	for b = 0, 31, 2 do
		local c = s
		for i = 1, nargs do
			c = t[c][args[i] % 4]
			args[i] = math.floor( args[i] / 4 )
		end
		ret = ret + c * pow
		pow = pow * 4
	end
	return ret
end

function bit32.band( ... )
	return comb( 'band', { ... }, select( '#', ... ), 3, logic_and )
end

function bit32.bor( ... )
	return comb( 'bor', { ... }, select( '#', ... ), 0, logic_or )
end

function bit32.bxor( ... )
	return comb( 'bxor', { ... }, select( '#', ... ), 0, logic_xor )
end

function bit32.btest( ... )
	return comb( 'btest', { ... }, select( '#', ... ), 3, logic_and ) ~= 0
end


function bit32.extract( n, field, width )
	n = checkint32( 'extract', 1, n, 2 )
	field = checkint( 'extract', 2, field, 2 )
	width = checkint( 'extract', 3, width or 1, 2 )
	if field < 0 then
		error( "bad argument #2 to 'extract' (field cannot be negative)", 2 )
	end
	if width <= 0 then
		error( "bad argument #3 to 'extract' (width must be positive)", 2 )
	end
	if field + width > 32 then
		error( 'trying to access non-existent bits', 2 )
	end

	return math.floor( n / 2^field ) % 2^width
end

function bit32.replace( n, v, field, width )
	n = checkint32( 'replace', 1, n, 2 )
	v = checkint32( 'replace', 2, v, 2 )
	field = checkint( 'replace', 3, field, 2 )
	width = checkint( 'replace', 4, width or 1, 2 )
	if field < 0 then
		error( "bad argument #3 to 'replace' (field cannot be negative)", 2 )
	end
	if width <= 0 then
		error( "bad argument #4 to 'replace' (width must be positive)", 2 )
	end
	if field + width > 32 then
		error( 'trying to access non-existent bits', 2 )
	end

	local f = 2^field
	local w = 2^width
	local fw = f * w
	return ( n % f ) + ( v % w ) * f + math.floor( n / fw ) * fw
end


-- For the shifting functions, anything over 32 is the same as 32
-- and limiting to 32 prevents overflow/underflow
local function checkdisp( name, x )
	x = checkint( name, 2, x, 3 )
	return math.min( math.max( -32, x ), 32 )
end

function bit32.lshift( x, disp )
	x = checkint32( 'lshift', 1, x, 2 )
	disp = checkdisp( 'lshift', disp )

	return math.floor( x * 2^disp ) % 0x100000000
end

function bit32.rshift( x, disp )
	x = checkint32( 'rshift', 1, x, 2 )
	disp = checkdisp( 'rshift', disp )

	return math.floor( x / 2^disp ) % 0x100000000
end

function bit32.arshift( x, disp )
	x = checkint32( 'arshift', 1, x, 2 )
	disp = checkdisp( 'arshift', disp )

	if disp <= 0 then
		-- Non-positive displacement == left shift
		-- (since exponent is non-negative, the multipication can never result
		-- in a fractional part)
		return ( x * 2^-disp ) % 0x100000000
	elseif x < 0x80000000 then
		-- High bit is 0 == right shift
		-- (since exponent is positive, the division will never increase x)
		return math.floor( x / 2^disp )
	elseif disp > 31 then
		-- Shifting off all bits
		return 0xffffffff
	else
		-- 0x100000000 - 2 ^ ( 32 - disp ) creates a number with the high disp
		-- bits set. So shift right then add that number.
		return math.floor( x / 2^disp ) + ( 0x100000000 - 2 ^ ( 32 - disp ) )
	end
end

-- For the rotation functions, disp works mod 32.
-- Note that lrotate( x, disp ) == rrotate( x, -disp ).
function bit32.lrotate( x, disp )
	x = checkint32( 'lrotate', 1, x, 2 )
	disp = checkint( 'lrotate', 2, disp, 2 ) % 32

	local x = x * 2^disp
	return ( x % 0x100000000 ) + math.floor( x / 0x100000000 )
end

function bit32.rrotate( x, disp )
	x = checkint32( 'rrotate', 1, x, 2 )
	disp = -checkint( 'rrotate', 2, disp, 2 ) % 32

	local x = x * 2^disp
	return ( x % 0x100000000 ) + math.floor( x / 0x100000000 )
end

return bit32
