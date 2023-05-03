local export = {}

function export.languages()
    local ret = {}

    -- https://zh.wiktionary.org/wiki/Module:Zh
    local m_zh = require("Module:Zh")
    -- https://zh.wiktionary.org/wiki/Module:Languages
    local m_languages = require("Module:Languages")
    -- https://zh.wiktionary.org/wiki/Module:Languages/alldata
    local allData = mw.loadData("Module:Languages/alldata")

    for code, _ in pairs(allData) do
        names = {}
        local lang = m_languages.getByCode(code)
        local canonicalName = lang:getCanonicalName()
        table.insert(names, canonicalName)
        local canonicalNameSimplified = m_zh.ts(canonicalName)
        if canonicalNameSimplified ~= canonicalName then
            table.insert(names, canonicalNameSimplified)
        end
        -- importantly, this returns all of `otherNames`, `aliases` and `varieties`
        local otherNames = lang:getOtherNames()
        for _, otherName in ipairs(otherNames) do
            table.insert(names, otherName)
            local otherNameSimplified = m_zh.ts(otherName)
            if otherNameSimplified ~= otherName then
                table.insert(names, otherNameSimplified)
            end
        end
        ret[code] = names
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export