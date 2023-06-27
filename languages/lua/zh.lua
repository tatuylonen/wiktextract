local export = {}

function export.languages()
    local ret = {}

    -- https://zh.wiktionary.org/wiki/Module:Zh
    local m_zh = require("Module:Zh")
    -- https://zh.wiktionary.org/wiki/Module:Languages
    local m_languages = require("Module:Languages")
    -- https://zh.wiktionary.org/wiki/Module:Languages/data/all
    local allData = mw.loadData("Module:Languages/data/all")

    local function addNames(allNames, names)
        for _, name in ipairs(names) do
            table.insert(allNames, name)
            local nameSimplified = m_zh.ts(name)
            if nameSimplified ~= name then
                table.insert(allNames, nameSimplified)
            end
        end
    end

    for code, _ in pairs(allData) do
        names = {}
        local lang = m_languages.getByCode(code)
        local canonicalName = lang:getCanonicalName()
        addNames(names, {canonicalName})

        -- There are methods getAliases() and getOtherNames(), but
        -- getOtherNames() doesn't work as of 2023-06-27.
        lang:loadInExtraData()
        local aliases = lang._rawData.aliases or (lang._extraData and lang._extraData.aliases) or {}
        addNames(names, aliases)
        local otherNames = lang._rawData.otherNames or (lang._extraData and lang._extraData.otherNames) or {}
        addNames(names, otherNames)

        ret[code] = names
    end
    
    return require("Module:wiktextract-json").toJSON(ret)

end

return export