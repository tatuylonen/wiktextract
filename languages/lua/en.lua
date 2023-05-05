local export = {}

function export.languages()
    local ret = {}

    -- https://en.wiktionary.org/wiki/Module:languages
    local m_languages = require("Module:languages")
    -- https://en.wiktionary.org/wiki/Module:languages/data/all
    local allData = mw.loadData("Module:languages/data/all")

    local function addNames(allNames, names)
        for _, name in ipairs(names) do
            table.insert(allNames, name)
        end
    end

    for code, _ in pairs(allData) do
        names = {}
        local lang = m_languages.getByCode(code)
        local canonicalName = lang:getCanonicalName()
        addNames(names, {canonicalName})
        -- the true arg gets ONLY otherNames, not including aliases/varieties
        local otherNames = lang:getOtherNames(true)
        addNames(names, otherNames)
        local aliases = lang:getAliases()
        addNames(names, aliases)
        ret[code] = names
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export