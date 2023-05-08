local export = {}

function export.languages()
    local ret = {}

    -- https://sk.wiktionary.org/wiki/Modul:Languages
    local allData = mw.loadData("Modul:Languages")
    for code, data in pairs(allData) do
        -- "zxx" has name "—", don't include it 
        if data.name ~= "—" then
            ret[code] = {data.name}
        end
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export