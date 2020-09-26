-- Simplified implementation of mw.site for running WikiMedia Scribunto
-- code under Python
--
-- Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

local Namespace = {
   hasGenderDistinction = true,
   isCapitalized = false,
   isMovable = false,
   defaultContentModel = "wikitext",
   aliases = {},
   associated = {},
}
Namespace.__index = Namespace

function Namespace:new(obj)
   obj = obj or {}
   setmetatable(obj, self)
   obj.canonicalName = obj.name
   obj.displayName = obj.name
   obj.hasSubpages = obj.name == "Main" or obj.name == "Module"
   return obj
end

-- These duplicate definitions in wikiparserfns.py
local media_ns = Namespace:new{id=-2, name="Media", isSubject=true}
local special_ns = Namespace:new{id=-1, name="Special", isSubject=true}
local main_ns = Namespace:new{id=0, name="Main", isContent=true, isSubject=true}
local talk_ns = Namespace:new{id=1, name="Talk", isTalk=true, subject=main_ns}
local user_ns = Namespace:new{id=2, name="User", isSubject=true}
local user_talk_ns = Namespace:new{id=3, name="User_talk", isTalk=true,
                                   subject=user_ns}
local project_ns = Namespace:new{id=4, name="Project", isSubject=true}
local project_talk_ns = Namespace:new{id=5, name="Project_talk", isTalk=true,
                                      subject=project_ns}
local image_ns = Namespace:new{id=6, name="File", aliases={"Image"},
                               isSubject=true}
local image_talk_ns = Namespace:new{id=7, name="File_talk",
                                    aliases={"Image_talk"},
                                    isTalk=true, subject=image_ns}
local mediawiki_ns = Namespace:new{id=8, name="MediaWiki", isSubject=true}
local mediawiki_talk_ns = Namespace:new{id=9, name="MediaWiki_talk",
                                        isTalk=true, subject=mediawiki_ns}
local template_ns = Namespace:new{id=10, name="Template", isSubject=true}
local template_talk_ns = Namespace:new{id=11, name="Template_talk", isTalk=true,
                                       subject=template_ns}
local help_ns = Namespace:new{id=12, name="Help", isSubject=true}
local help_talk_ns = Namespace:new{id=13, name="Help_talk", isTalk=true,
                                   subject=help_ns}
local category_ns = Namespace:new{id=14, name="Category", isSubject=true}
local category_talk_ns = Namespace:new{id=15, name="Category_talk", isTalk=true,
                                       subject=category_ns}
local module_ns = Namespace:new{id=828, name="Module", isIncludable=true,
                                isSubject=true}
local module_talk_ns = Namespace:new{id=829, name="Module_talk", isTalk=true,
                                     subject=module_ns}
main_ns.talk = talk_ns
user_ns.talk = user_talk_ns
project_ns.talk = project_talk_ns
mediawiki_ns.talk = mediawiki_talk_ns
template_ns.talk = template_talk_ns
help_ns.talk = help_talk_ns
category_ns.talk = category_talk_ns
module_ns.talk = module_talk_ns

function add_ns(t, ns)
   assert(ns.name ~= nil)
   assert(ns.id ~= nil)
   t[ns.id] = ns
   t[ns.name] = ns
end

local mw_site_namespaces = {}
add_ns(mw_site_namespaces, media_ns)
add_ns(mw_site_namespaces, special_ns)
add_ns(mw_site_namespaces, main_ns)
add_ns(mw_site_namespaces, talk_ns)
add_ns(mw_site_namespaces, user_ns)
add_ns(mw_site_namespaces, user_talk_ns)
add_ns(mw_site_namespaces, project_ns)
add_ns(mw_site_namespaces, project_talk_ns)
add_ns(mw_site_namespaces, image_ns)
add_ns(mw_site_namespaces, image_talk_ns)
add_ns(mw_site_namespaces, mediawiki_ns)
add_ns(mw_site_namespaces, mediawiki_talk_ns)
add_ns(mw_site_namespaces, template_ns)
add_ns(mw_site_namespaces, template_talk_ns)
add_ns(mw_site_namespaces, help_ns)
add_ns(mw_site_namespaces, help_talk_ns)
add_ns(mw_site_namespaces, category_ns)
add_ns(mw_site_namespaces, category_talk_ns)
add_ns(mw_site_namespaces, module_ns)
add_ns(mw_site_namespaces, module_talk_ns)

local mw_site_contentNamespaces = {}
add_ns(mw_site_contentNamespaces, main_ns)

local mw_site_subjectNamespaces = {}
add_ns(mw_site_subjectNamespaces, media_ns)
add_ns(mw_site_subjectNamespaces, special_ns)
add_ns(mw_site_subjectNamespaces, main_ns)
add_ns(mw_site_subjectNamespaces, user_ns)
add_ns(mw_site_subjectNamespaces, project_ns)
add_ns(mw_site_subjectNamespaces, image_ns)
add_ns(mw_site_subjectNamespaces, mediawiki_ns)
add_ns(mw_site_subjectNamespaces, template_ns)
add_ns(mw_site_subjectNamespaces, help_ns)
add_ns(mw_site_subjectNamespaces, category_ns)
add_ns(mw_site_subjectNamespaces, module_ns)

local mw_site_talkNamespaces = {}
add_ns(mw_site_talkNamespaces, talk_ns)
add_ns(mw_site_talkNamespaces, user_talk_ns)
add_ns(mw_site_talkNamespaces, project_talk_ns)
add_ns(mw_site_talkNamespaces, image_talk_ns)
add_ns(mw_site_talkNamespaces, mediawiki_talk_ns)
add_ns(mw_site_talkNamespaces, template_talk_ns)
add_ns(mw_site_talkNamespaces, help_talk_ns)
add_ns(mw_site_talkNamespaces, category_talk_ns)
add_ns(mw_site_talkNamespaces, module_talk_ns)

function mw_site_index(x, ns)
   return mw.site.findNamespace(ns)
end

local mw_site = {
   __index = mw_site_index,
   server = "server.dummy",
   siteName = "Dummy Site",
   namespaces = mw_site_namespaces,
   contentNamespaces = mw_site_contentNamespaces,
   subjectNamespaces = mw_site_subjectNamespaces,
   talkNamespaces = mw_site_talkNamespaces,
   stats = {
      pages = 0,
      articles = 0,
      files = 0,
      users = 0,
      activeUsers = 0,
      admins = 0
   }
}

function mw_site.matchNamespaceName(v, name)
   -- Internal function to match namespace against name
   -- namespace prefixes are case-insensitive
   if type(name) == "number" then
      if name == v.id then return true end
      return false
   end
   assert(type(name) == "string")
   name = string.upper(name)
   if name == string.upper(v.name) then return true end
   if name == string.upper(v.canonicalName) then return true end
   for i, alias in ipairs(v.aliases) do
      if name == string.upper(alias) then return true end
   end
   return false
end

function mw_site.findNamespace(name)
   -- Internal function to find the namespace object corresponding to a name
   if type(name) == "string" then
      -- strip surrounding whitespaces
      name = name:gsub("^%s(.-)%s*$", "%1")
   end
   for k, v in pairs(mw.site.namespaces) do
      if mw.site.matchNamespaceName(v, name) then
         return v
      end
   end
   return nil
end

function mw_site.stats.pagesInCategory(category, which)
   if which == "*" or which == nil then
      return {
         all = 0,
         subcats = 0,
         files = 0,
         pages = 0
      }
   end
   return 0
end

function mw_site.stats.pagesInNamespace(ns)
   return 0
end

function mw_site.stats.usersInGroup(filter)
   return 0
end

function mw_site.interwikiMap(filter)
   print("mw.site.interwikiMap called", filter)
   return {}
end

return mw_site
