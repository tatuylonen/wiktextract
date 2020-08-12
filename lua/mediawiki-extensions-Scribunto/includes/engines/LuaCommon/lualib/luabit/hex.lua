--[[---------------
Hex v0.4
-------------------
Hex conversion lib for lua.

How to use:
 hex.to_hex(n) -- convert a number to a hex string
 hex.to_dec(hex) -- convert a hex string(prefix with '0x' or '0X') to number
 
Part of LuaBit(http://luaforge.net/projects/bit/).

Under the MIT license.

copyright(c) 2006~2007 hanzhao (abrash_han@hotmail.com)

2013-02-20: Brad Jorsch: Fix to not try messing with globals, doesn't work in Scribunto
--]]---------------

local bit = require 'bit'

do 

local function to_hex(n)
 if(type(n) ~= "number") then
  error("non-number type passed in.")
 end

 -- checking not float
 if(n - math.floor(n) > 0) then
  error("trying to apply bitwise operation on non-integer!")
 end

 if(n < 0) then
  -- negative
  n = bit.tobits(bit.bnot(math.abs(n)) + 1)
  n = bit.tonumb(n)
 end

 hex_tbl = {'A', 'B', 'C', 'D', 'E', 'F'}
 hex_str = ""

 while(n ~= 0) do
  last = math.mod(n, 16)
  if(last < 10) then
   hex_str = tostring(last) .. hex_str
  else
   hex_str = hex_tbl[last-10+1] .. hex_str
  end
  n = math.floor(n/16)
 end
 if(hex_str == "") then
  hex_str = "0"
 end
 return "0x" .. hex_str
end

local function to_dec(hex)
 if(type(hex) ~= "string") then
  error("non-string type passed in.")
 end

 head = string.sub(hex, 1, 2)
 
 if( head ~= "0x" and head ~= "0X") then
  error("wrong hex format, should lead by 0x or 0X.")
 end

 v = tonumber(string.sub(hex, 3), 16)

 return v;
end

--------------------
-- hex lib interface
local hex = {
 to_dec = to_dec,
 to_hex = to_hex,
}

return hex

end

--[[
-- test
d = 4341688
h = to_hex(d)
print(h)
print(to_dec(h))


for i = 1, 100000 do
 h = hex.to_hex(i)
 d = hex.to_dec(h)
 if(d ~= i) then 
  error("failed " .. i .. ", " .. h)
 end
end
--]]
