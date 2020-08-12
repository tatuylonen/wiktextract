local testframework = require 'Module:TestFramework'

local function test_new( arg )
	-- Skip the functions
	local ret = {}
	for k, v in pairs( mw.uri.new( arg ) ) do
		if type( v ) ~= 'function' then
			ret[k] = v
		end
	end
	return ret
end

-- Tests
local tests = {
	{ name = 'uri.encode', func = mw.uri.encode,
	  args = { '__foo b\195\161r + baz__' },
	  expect = { '__foo+b%C3%A1r+%2B+baz__' }
	},
	{ name = 'uri.encode QUERY', func = mw.uri.encode,
	  args = { '__foo b\195\161r + /baz/__', 'QUERY' },
	  expect = { '__foo+b%C3%A1r+%2B+%2Fbaz%2F__' }
	},
	{ name = 'uri.encode PATH', func = mw.uri.encode,
	  args = { '__foo b\195\161r + /baz/__', 'PATH' },
	  expect = { '__foo%20b%C3%A1r%20%2B%20%2Fbaz%2F__' }
	},
	{ name = 'uri.encode WIKI', func = mw.uri.encode,
	  args = { '__foo b\195\161r + /baz/__', 'WIKI' },
	  expect = { '__foo_b%C3%A1r_%2B_/baz/__' }
	},

	{ name = 'uri.decode', func = mw.uri.decode,
	  args = { '__foo+b%C3%A1r+%2B+baz__' },
	  expect = { '__foo b\195\161r + baz__' }
	},
	{ name = 'uri.decode QUERY', func = mw.uri.decode,
	  args = { '__foo+b%C3%A1r+%2B+baz__', 'QUERY' },
	  expect = { '__foo b\195\161r + baz__' }
	},
	{ name = 'uri.decode PATH', func = mw.uri.decode,
	  args = { '__foo+b%C3%A1r+%2B+baz__', 'PATH' },
	  expect = { '__foo+b\195\161r+++baz__' }
	},
	{ name = 'uri.decode WIKI', func = mw.uri.decode,
	  args = { '__foo+b%C3%A1r+%2B+baz__', 'WIKI' },
	  expect = { '  foo+b\195\161r+++baz  ' }
	},

	{ name = 'uri.anchorEncode', func = mw.uri.anchorEncode,
	  args = { '__foo b\195\161r__' },
	  expect = { 'foo_b.C3.A1r' }
	},

	{ name = 'uri.new', func = test_new,
	  args = { 'http://www.example.com/test?foo=1&bar&baz=1&baz=2#fragment' },
	  expect = {
		  {
			  protocol = 'http',
			  host = 'www.example.com',
			  hostPort = 'www.example.com',
			  authority = 'www.example.com',
			  path = '/test',
			  query = {
				  foo = '1',
				  bar = false,
				  baz = { '1', '2' },
			  },
			  queryString = 'foo=1&bar&baz=1&baz=2',
			  fragment = 'fragment',
			  relativePath = '/test?foo=1&bar&baz=1&baz=2#fragment',
		  },
	  },
	},

	{ name = 'uri.new', func = mw.uri.new, type = 'ToString',
	  args = { 'http://www.example.com/test?foo=1&bar&baz=1&baz=2#fragment' },
	  expect = { 'http://www.example.com/test?foo=1&bar&baz=1&baz=2#fragment' },
	},

	{ name = 'uri.localUrl( Example )', func = mw.uri.localUrl, type = 'ToString',
	  args = { 'Example' },
	  expect = { '/wiki/Example' },
	},
	{ name = 'uri.localUrl( Example, string )', func = mw.uri.localUrl, type = 'ToString',
	  args = { 'Example', 'action=edit' },
	  expect = { '/w/index.php?title=Example&action=edit' },
	},
	{ name = 'uri.localUrl( Example, table )', func = mw.uri.localUrl, type = 'ToString',
	  args = { 'Example', { action = 'edit' } },
	  expect = { '/w/index.php?title=Example&action=edit' },
	},

	{ name = 'uri.fullUrl( Example )', func = mw.uri.fullUrl, type = 'ToString',
	  args = { 'Example' },
	  expect = { '//wiki.local/wiki/Example' },
	},
	{ name = 'uri.fullUrl( Example, string )', func = mw.uri.fullUrl, type = 'ToString',
	  args = { 'Example', 'action=edit' },
	  expect = { '//wiki.local/w/index.php?title=Example&action=edit' },
	},
	{ name = 'uri.fullUrl( Example, table )', func = mw.uri.fullUrl, type = 'ToString',
	  args = { 'Example', { action = 'edit' } },
	  expect = { '//wiki.local/w/index.php?title=Example&action=edit' },
	},

	{ name = 'uri.canonicalUrl( Example )', func = mw.uri.canonicalUrl, type = 'ToString',
	  args = { 'Example' },
	  expect = { 'http://wiki.local/wiki/Example' },
	},
	{ name = 'uri.canonicalUrl( Example, string )', func = mw.uri.canonicalUrl, type = 'ToString',
	  args = { 'Example', 'action=edit' },
	  expect = { 'http://wiki.local/w/index.php?title=Example&action=edit' },
	},
	{ name = 'uri.canonicalUrl( Example, table )', func = mw.uri.canonicalUrl, type = 'ToString',
	  args = { 'Example', { action = 'edit' } },
	  expect = { 'http://wiki.local/w/index.php?title=Example&action=edit' },
	},

	{ name = 'uri.new with empty query string', func = mw.uri.new, type = 'ToString',
	  args = { 'http://wiki.local/w/index.php?' },
	  expect = { 'http://wiki.local/w/index.php?' },
	},

	{ name = 'uri.new with empty fragment', func = mw.uri.new, type = 'ToString',
	  args = { 'http://wiki.local/w/index.php#' },
	  expect = { 'http://wiki.local/w/index.php#' },
	},

	{ name = 'uri.new with IPv6', func = mw.uri.new, type = 'ToString',
	  args = { 'http://[2001:db8::]' },
	  expect = { 'http://[2001:db8::]' },
	},
	{ name = 'uri.new with IPv6 and port', func = mw.uri.new, type = 'ToString',
	  args = { 'http://[2001:db8::]:80' },
	  expect = { 'http://[2001:db8::]:80' },
	},
}

-- Add tests to test round-tripping for every combination of parameters
local bits = { [0] = false, false, false, false, false, false, false, false, false }
local ct = 0
while not bits[8] do
	local url = {}
	if bits[0] then
		url[#url+1] = 'http:'
	end
	if bits[1] or bits[2] or bits[3] or bits[4] then
		url[#url+1] = '//'
	end
	if bits[1] then
		url[#url+1] = 'user'
	end
	if bits[2] then
		url[#url+1] = ':password'
	end
	if bits[1] or bits[2] then
		url[#url+1] = '@'
	end
	if bits[3] then
		url[#url+1] = 'host.example.com'
	end
	if bits[4] then
		url[#url+1] = ':123'
	end
	if bits[5] then
		url[#url+1] = '/path'
	end
	if bits[6] then
		url[#url+1] = '?query=1'
	end
	if bits[7] then
		url[#url+1] = '#fragment'
	end

	url = table.concat( url, '' )
	tests[#tests+1] = { name = 'uri.new (' .. ct .. ')', func = mw.uri.new, type = 'ToString',
	  args = { url },
	  expect = { url },
	}
	ct = ct + 1

	for i = 0, 8 do
		bits[i] = not bits[i]
		if bits[i] then
			break
		end
	end
end

return testframework.getTestProvider( tests )
