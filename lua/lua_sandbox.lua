-- Sandbox for executing WikiMedia Scribunto Lua code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local env = _ENV

unpack = table.unpack

mw = nil  -- assigned in lua_set_loader()
ustring = nil -- assigned in lua_set_fns()
python_loader = nil

-- This function loads new a new module, whether built-in or defined in the
-- data file.
function new_loader(modname)
  local content = nil
  if python_loader ~= nil then
    content = python_loader(modname)
  else
     error("PYTHON LOADER NOT SET - call lua_set_loader() first")
  end
  if content == nil then
     error("MODULE NOT FOUND: " .. modname)
  end

  -- Wikimedia uses an older version of Lua.  Make certain substitutions
  -- to make existing code run on more modern versions of Lua.
  content = string.gsub(content, "%%\\%[", "%%[")

  -- Load the content into the Lua interpreter.
  local ret = assert(load(content, modname, "bt", env))
  return ret
end

-- Register the new loader as the only package searcher in Lua.
package.searchers = {}
package.searchers[0] = nil
package.searchers[1] = new_loader

-- This should be called immediately after loading the sandbox to set the
-- Python function that will be used for loading Lua modules and various
-- other Python functions that implement some of the functionality needed
-- for executing Scribunto code (these functions are called from Lua code).
function lua_set_loader(loader, mw_text_decode, mw_text_encode,
                        get_page_info, fetch_language_name,
                        fetch_language_names)
  python_loader = loader
  mw = require("mw")
  mw.text.decode = mw_text_decode
  mw.text.encode = mw_text_encode
  mw.title.python_get_page_info = get_page_info
  mw.language.python_fetch_language_name = fetch_language_name
  mw.language.python_fetch_language_names = fetch_language_names
end

function frame_args_index(new_args, key)
   -- print("frame_args_index", key)
   local v = new_args._orig[key]
   if v == nil then return nil end
   if not new_args._preprocessed[key] then
      local frame = new_args._frame
      v = frame:preprocess(v)
      -- Cache preprocessed value so we only preprocess each argument once
      new_args._preprocessed[key] = true
      new_args._orig[key] = v
   end
   -- print("frame_args_index", key, "->", v)
   return v
end

function frame_args_pairs(new_args)
   -- print("frame_args_pairs")
   local frame = new_args._frame
   local function stateless_iter(new_args, key)
      if key == nil then key = "***nil***" end
      local nkey = new_args._next_key[key]
      if nkey == nil then return nil end
      local v = new_args[nkey]
      if v == nil then return nil end
      return nkey, v
   end
   return stateless_iter, new_args, nil
end

function frame_args_ipairs(new_args)
   -- print("frame_args_ipairs")
   local frame = new_args._frame
   local function stateless_iter(new_args, key)
      if key == nil then key = 1 else key = key + 1 end
      local v = new_args[key]
      if v == nil then return nil end
      return key, v
   end
   return stateless_iter, new_args, nil
end

function frame_args_len(new_args)
   return #new_args._orig
end

frame_args_meta = {
   __index = frame_args_index,
   __pairs = frame_args_pairs,
   __len = frame_args_len
}

function prepare_frame_args(frame)
  local next_key = {}
  local prev = "***nil***"
  for k, v in pairs(frame.args) do
     next_key[prev] = k
     prev = k
  end
  new_args = {_orig = frame.args, _frame = frame, _next_key = next_key,
              _preprocessed = {}}
  setmetatable(new_args, frame_args_meta)
  frame.args = new_args
  frame.argumentPairs = function (frame) return pairs(frame.args) end
  frame.getArgument = frame_get_argument
end

function frame_get_argument(frame, name)
   if type(name) == "table" then name = name.name end
   v = frame.args[name]
   if v == nil then return nil end
   return { expand = function() return v end }
end

-- This function implements the {{#invoke:...}} parser function.
-- XXX need better handling of parent frame and frame
-- This returns (true, value) if successful, (false, error) if exception.
function lua_invoke(mod_name, fn_name, frame)
  local mod = require(mod_name)
  local fn = mod[fn_name]
  local pframe = frame:getParent()
  -- print("lua_invoke", mod_name, fn_name)
  -- for k, v in pairs(frame.args) do
  --    print("", k, type(k), v, type(v))
  -- end
  -- if pframe ~= nil then
  --    print("parent")
  --    for k, v in pairs(pframe.args) do
  --       print("", k, type(k), v, type(v))
  --    end
  -- end
  io.flush()
  -- Convert frame.args into a metatable that preprocesses the values
  prepare_frame_args(frame)
  -- Implement some additional functions for frame
  if pframe ~= nil then
     prepare_frame_args(pframe)
  end
  mw.getCurrentFrame = function() return frame end
  if fn == nil then
     return {false, "\tNo function '" .. fn_name .. "' in module " .. mod_name}
  end
  return xpcall(function() return fn(frame) end, debug.traceback)
end

-- math.log10 seems to be sometimes missing???
function math.log10(x)
   return math.log(x, 10)
end

-- Limit access to traceback in the debug module
local new_debug = { traceback = debug.traceback }

-- Limit access to a few safe functions in the os module
local new_os = {
   clock = os.clock,
   date = os.date,
   difftime = os.difftime,
   time = os.time,
}

env = {}
env["_G"] = env
env["_VERSION"] = _VERSION
env["assert"] = assert
env["debug"] = new_debug
env["error"] = error
env["getmetatable"] = getmetatable  -- MODIFY
env["ipairs"] = ipairs
env["lua_invoke"] = lua_invoke
env["lua_set_loader"] = lua_set_loader
env["math"] = math
env["mw"] = mw
env["next"] = next
env["os"] = new_os
env["pairs"] = pairs
env["pcall"] = pcall
env["print"] = print
env["rawequal"] = rawequal
env["rawget"] = rawget
env["rawset"] = rawset
env["require"] = require
env["select"] = select
env["setmetatable"] = setmetatable
env["string"] = string
env["table"] = table
env["tonumber"] = tonumber
env["tostring"] = tostring
env["type"] = type
env["unpack"] = table.unpack
env["xpcall"] = xpcall   -- MODIFY

local _ENV = env

-- built-in modules:
    -- bit32
    -- libraryUtil
    -- luabit
