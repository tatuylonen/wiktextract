local export = {}

function export.languages()
    local ret = {}

    -- https://en.wiktionary.org/wiki/Module:languages
    local m_languages = require("Module:languages")
    -- https://en.wiktionary.org/wiki/Module:languages/data/all
    local allData = mw.loadData("Module:languages/data/all")

    for code, _ in pairs(allData) do
        names = {}
        local lang = m_languages.getByCode(code)
        local canonicalName = lang:getCanonicalName()
        table.insert(names, canonicalName)
        -- importantly, this returns all of `otherNames`, `aliases` and `varieties`
        local otherNames = lang:getOtherNames()
        for _, otherName in ipairs(otherNames) do
            table.insert(names, otherName)
        end
        ret[code] = names
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export