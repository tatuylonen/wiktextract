local function tohex( s )
	local t = { s }
	for c in mw.ustring.gcodepoint( s ) do
		t[#t + 1] = string.format( "%x", c )
	end
	return table.concat( t, '\t' )
end

return {
	run = function ( c1, c2, c3, c4, c5 )
		return
			tohex( mw.ustring.toNFC( c1 ) ),
			tohex( mw.ustring.toNFC( c2 ) ),
			tohex( mw.ustring.toNFC( c3 ) ),
			tohex( mw.ustring.toNFC( c4 ) ),
			tohex( mw.ustring.toNFC( c5 ) ),
			tohex( mw.ustring.toNFD( c1 ) ),
			tohex( mw.ustring.toNFD( c2 ) ),
			tohex( mw.ustring.toNFD( c3 ) ),
			tohex( mw.ustring.toNFD( c4 ) ),
			tohex( mw.ustring.toNFD( c5 ) ),
			tohex( mw.ustring.toNFKC( c1 ) ),
			tohex( mw.ustring.toNFKC( c2 ) ),
			tohex( mw.ustring.toNFKC( c3 ) ),
			tohex( mw.ustring.toNFKC( c4 ) ),
			tohex( mw.ustring.toNFKC( c5 ) ),
			tohex( mw.ustring.toNFKD( c1 ) ),
			tohex( mw.ustring.toNFKD( c2 ) ),
			tohex( mw.ustring.toNFKD( c3 ) ),
			tohex( mw.ustring.toNFKD( c4 ) ),
			tohex( mw.ustring.toNFKD( c5 ) )
	end
}
