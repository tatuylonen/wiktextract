LuaBit
------
LuaBit is a bitwise operation lib completely written in Lua. It's
written in the belief that Lua is self-contained.

The supported operations are: not, and, or, xor, right shift, logic
right shift and left shift.

Several utilities are designed to leverage the power of bit operation:
 1. hex: a dec <-> hex number converter
 2. utf8: convert utf8 string to ucs2
 3. noki: convert nokia pc suite backuped SMS file to .txt

Under the MIT license.

Visit http://luaforge.net/projects/bit/ to get latest version.

Status
------
Now LuaBit is in v0.4. 
Release date: Mar 18, 2007

Content
-------
3 files are there for LuaBit:
 1) bit.lua
    is the bitwise operation lib, all operations are implemented here.

 2) hex.lua
    is a helper lib for ease of using hex numbers with bitwise 
    operation.

 3) noki.lua
    a utility(based on bit and hex) to convert Nokia PC Suite backuped 
    SMS to a unicode .txt file, which is more accessible than the 
    original .nfb or .nfc file.
    
 4) utf8.lua
    convert utf8 string to ucs2 string

How to use
----------
Bit
---
Just require 'bit' in your project and the bit lib will be 
available:
 bit.bnot(n) -- bitwise not (~n)
 bit.band(m, n) -- bitwise and (m & n)
 bit.bor(m, n) -- bitwise or (m | n)
 bit.bxor(m, n) -- bitwise xor (m ^ n)
 bit.brshift(n, bits) -- right shift (n >> bits)
 bit.blshift(n, bits) -- left shift (n << bits)
 bit.blogic_rshift(n, bits) -- logic right shift(zero fill >>>)

Please note that bit.brshift and bit.blshift only support number within
32 bits.

2 utility functions are provided too:
 bit.tobits(n) -- convert n into a bit table(which is a 1/0 sequence)
               -- high bits first
 bit.tonumb(bit_tbl) -- convert a bit table into a number 

Hex
---
For ease of using hex numbers, a utility hex lib is also included in 
LuaBit. You can require 'hex' to use them:
 hex.to_hex(n) -- convert a number to a hex string
 hex.to_dec(hex) -- convert a hex string(prefix with '0x' or '0X') to number

With hex, you can write code like:
 bit.band(258, hex.to_dec('0xFF'))
to get the lower 8 bits of 258, that's 2.

Noki
----
require 'noki', to save your sms to .txt file:
 noki.save_sms('nokia.nfb', 'sms.txt')
and you can view the output sms.txt in notepad or other editor which
support unicode.

Utf8
----
require 'utf8', to convert a utf8 string:
 ucs2_string = utf8.utf_to_uni(utf8_string)

History
-------
v0.4
* utf8 to ucs2 converter(utf8.lua).
* clean up for compatible with Lua5.1 and 5.0.
* add 'How to use' section for bit.lua and hex.lua.

v0.3
* noki added as an application of bit.
* typo correction.

v0.2
* add logic right shift(>>>) support: bit.blogic_rshift.
* add 2 utility functions: bit.tobits and bit.tonumb.
* update hex.to_hex(in hex.lua) to support negative number.

v0.1
LuaBit is written when I do my own game project(Fio at http://fio.edithis.info). 
When loading resources, I have to do some bit operation. And I do not
like the embedded way of bit operation. So I decide to implement those
ops in lua. And that's LuaBit. It's not as fast as the embedded one, but
it works. And Lua is self-contained :-)

To-Do List
---------
v0.1
It'll be useful if LuaBit support those bitwise op like:
 bit.band(258, '0xFF')
ease to type and use. This will be supported in next release.

v0.2
I decide to delay this feature to later version for it'll mess up the 
interface of LuaBit.

v0.3
May more utility functions add to Noki - phonebook might be a nice candidate.

v0.4
There's no UCS2 -> UTF8 convertion now, this feature may add in next release
or when the project need.

Noki'll be be exluded from LuaBit in next release; I decide to let Noki grow
into a powerful tool to support more Nokia PC Suite backup format(.nfb, 
.nfc and .nbu). 

Trial Noki demo at http://nokisms.googlepages.com/(in Chinese)

Known issues
------------
LuaBit doesn't play very well with negative number. The return value of the
bitwise operations might change to positive when applied on negative numbers 
though the bit sequence is correct. So if you want do some arithmetic with
the result of bit operation, be careful.

Feedback
--------
Please send your comments, bugs, patches or change request to 
hanzhao(abrash_han@hotmail.com).
