local export = {}

function export.languages()
    local ret = {}

    -- https://fr.wiktionary.org/wiki/Module:bases
    local b = require('Module:bases')
    -- https://fr.wiktionary.org/wiki/Module:langues
    local lang = require('Module:langues')
    -- https://fr.wiktionary.org/wiki/Module:langues/data
    local allData = mw.loadData("Module:langues/data")

    for code, data in pairs(allData) do
        titleCaseName = b.ucfirst(data.nom)
        ret[code] = {titleCaseName}
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export