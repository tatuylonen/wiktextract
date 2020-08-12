package.path = arg[1] .. '/engines/LuaStandalone/?.lua;' ..
	arg[1] .. '/engines/LuaCommon/lualib/?.lua'

require('MWServer')
require('mwInit')
server = MWServer:new( arg[2], arg[3] )
server:execute()

