# Export English Wiktionary language and family data to JSON.
#
# Usage:
#
# python language_data.py enwiktionary_dump_file [--languages languages_output_file] [--families families_output_file]

import argparse
from wikitextprocessor import Wtp
from wikitextprocessor.dumpparser import process_dump
import json

lua_mod = r"""
local export = {}

function export.languages()
    -- https://en.wiktionary.org/wiki/Module:languages
    local m_languages = require("Module:languages")

    local function getData(code, data, kind)
        local lang = m_languages.getByCode(code, nil, true)
        local ancestors = {}
        for _, ancestor in ipairs(lang:getAncestorChain()) do
            table.insert(ancestors, ancestor:getCode())
        end
        local ret = {
            code = lang:getCode(),
            canonicalName = lang:getCanonicalName(),
            family = lang:getFamilyCode(),
            ---- To get other names, aliases and varieties in one list:
            -- otherNames = lang:getOtherNames(),
            otherNames = lang:getOtherNames(true),
            aliases = lang:getAliases(),
            varieties = lang:getVarieties(),
            scripts = lang:getScriptCodes(),
            -- The nearest language that is not an etymology-only language. E.g.
            -- for both "VL." (Vulgar Latin) and "ita-ola" (Old Latin) it is
            -- "la". For a regular language it is its own code.
            nonEtymologyOnly = lang:getNonEtymologicalCode(),
            wikidataItem = lang:getWikidataItem(),
            wikipediaArticle = lang:getWikipediaArticle(),
            -- The immediate parent(s) of the language. This will usually be
            -- one language code, but can be multiple in the case of mixture
            -- languages like creoles etc. When it is one code, it should
            -- correspond to the last item in "ancestors".
            parents = lang:getAncestorCodes(),
            -- A list of ancestor language codes from oldest to youngest,
            -- including proto-languages.
            ancestors = ancestors,
            -- regular, appendix-constructed, reconstructed, or etymology-only
            kind = data.type or kind,
        }
        return ret
    end

    local ret = {}

    -- https://en.wiktionary.org/wiki/Module:languages/data/2
    -- https://en.wiktionary.org/wiki/Module:languages/data/3/* where * is a-z
    -- https://en.wiktionary.org/wiki/Module:languages/data/exceptional
    local allData = mw.loadData("Module:languages/data/all")
    for code, data in pairs(allData) do
        ret[code] = getData(code, data, "regular")
    end

    -- https://en.wiktionary.org/wiki/Module:etymology_languages/data
    local etyData = mw.loadData("Module:etymology languages/data")
    for code, data in pairs(etyData) do
        ret[code] = getData(code, data, "etymology-only")
    end
    
    ret = require("Module:table").deepcopy(ret)

    return require("Module:JSON").toJSON(ret)

end

function export.families()
    -- https://en.wiktionary.org/wiki/Module:families
    local m_families = require("Module:families")

    -- https://en.wiktionary.org/wiki/Module:families/data
    local famData = mw.loadData("Module:families/data")
    
    local function getSuperfamilies(fam)
        -- We reverse the order of superfamilies to correspond with the ordering of
        -- lang ancestors, i.e. remotest to nearest (see above).
        local function rev(t)
            local ret = {}
            for i = #t, 1, -1 do
                table.insert(ret, t[i])
            end
            return ret
        end

        local superfamilies = {}
        local superfamily = fam:getFamily()
        while superfamily do
            code = superfamily:getCode()
            for _, a_fam in ipairs(superfamilies) do
                if a_fam == code then
                    return rev(superfamilies)
                end
            end 
            table.insert(superfamilies, code)
            superfamily = superfamily:getFamily()
        end
        return rev(superfamilies)
    end

    local ret = {}

    for code, data in pairs(famData) do
        local fam = m_families.getByCode(code)
        ret[code] = {
            code = fam:getCode(),
            canonicalName = fam:getCanonicalName(),
            protoLanguage = fam:getProtoLanguageCode(),
            superfamilies = getSuperfamilies(fam),
            otherNames = fam:getOtherNames(),
            wikidataItem = fam:getWikidataItem(),
            wikipediaArticle = fam:getWikipediaArticle(),
        }
    end
    
    ret = require("Module:table").deepcopy(ret)

    return require("Module:JSON").toJSON(ret)

end

return export
"""

def export_data(ctx, kind, path):
    ctx.start_page(f"{kind} data export")
    data = ctx.expand(f"{{{{#invoke:lang-data-export|{kind}}}}}")

    data = json.loads(data)
    with open(path, "w") as fout:
        json.dump(data, fout, indent=2, ensure_ascii=False, sort_keys=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description="Export Wiktionary language and family data to JSON")
    parser.add_argument("dump", type=str,
                        help="Wiktionary xml dump file path")
    parser.add_argument("--languages", type=str, default="languages.json",
                            help="Language data output file path")
    parser.add_argument("--families", type=str, default="families.json",
                            help="Family data output file path")
    args = parser.parse_args()

    ctx = Wtp()

    def page_handler(model, title, text):
        if title.startswith("Module:"):
            ctx.add_page(model, title, text)

    process_dump(ctx, args.dump, page_handler=page_handler)

    ctx.add_page("Scribunto", "Module:lang-data-export", lua_mod, transient=True)

    export_data(ctx, "languages", args.languages)
    export_data(ctx, "families", args.families)

