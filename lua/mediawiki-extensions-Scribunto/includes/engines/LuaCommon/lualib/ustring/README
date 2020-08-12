This is ustring, a pure-Lua library to handle UTF-8 strings.

It implements generally the same interface as the standard string library, with
the following differences:
* Most functions work on codepoints rather than bytes or characters. Yes, this
  means that even though "á" and "á" should appear identical and represent the
  same character, the former is one codepoint (U+00E1) while the latter is two
  (U+0061 U+0301).
* Added functions isutf8, byteoffset, codepoint, gcodepoint, toNFC, toNFD.
* No workalike for string.reverse is provided.

Contents:
* README - This file.
* ustring.lua - The main file for the library.
* string.lua - Extend the string metatable with methods from this library.
* upper.lua - Data table for ustring.upper.
* lower.lua - Data table for ustring.lower.
* charsets.lua - Data tables for pattern matching functions.
* make-tables.php - Regenerate upper.lua and lower.lua using PHP's multibyte
  string library, and charsets.lua using PCRE.
* normalization-data.lua - Data tables for toNFC and toNFD.
* make-normalization-table.php - Regenerate normalization-data.lua based on the
  file includes/libs/normal/UtfNormalData.inc from MediaWiki core.


This library (consisting of the files described above) is released under the MIT
License:

Copyright (C) 2012 Brad Jorsch <bjorsch@wikimedia.org>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

