-- Simplified implementation of mw.hash for running WikiMedia Scribunto code
-- under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

function mw_hash_hashValue(algo, value)
  print("MW_HASH_HASHVALUE")
end

function mw_hash_listAlgorithms()
  print("MW_HASH_LISTALGORITHMS")
  return {}
end

local mw_hash = {
  hashValue = mw_hash_hashValue,
  listAlgorithms = mw_hash_listAlgorithms,
}

return mw_hash
