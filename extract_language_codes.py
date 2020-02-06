# This script extracts the current list of language codes from English
# Wiktionary.  This generates wiktextract/languages.py
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import json
import time
import requests

lang_url = "https://en.wiktionary.org/wiki/Wiktionary:List_of_languages"
fam_url = "https://en.wiktionary.org/wiki/Wiktionary:List_of_families"
url_prefix = "https://en.wiktionary.org"

######################################################################
# Fetch information about languages and language codes
######################################################################

print("Fetching", lang_url)
resp = requests.get(lang_url)
if resp.status_code != 200:
    print("Fetching language code list failed")
    sys.exit(1)
text = resp.text

all_languages = []

for m in re.finditer(r"(?s)<tr[^>]*>(.*?)</tr>", text):
    row = m.group(1)
    row = re.sub(r"</?code>", "", row)
    row = re.sub(r'<a\b.*?\bhref="([^"]*?)".*?>([^<]*?)</a>', r'\1|\2', row)
    cols = list(mm.group(1).strip() for mm in
                re.finditer(r"(?s)<td>(.*?)</td>", row))
    if len(cols) == 0:
        continue
    if len(cols) != 7:
        print("Unexpected #cols: {}".format(cols))
        continue
    code, lang, family, scripts, other_names, has_sort, has_diacr = cols
    if not family:
        family = "|"
    try:
        lang_url, lang_name = lang.split("|")
        family_url, family_name = family.split("|")
    except ValueError:
        print("Unexpected col format: {}".format(cols))
        continue
    scripts = list(x.strip().split("|")[1] for x in
                   scripts.split(",")
                   if x.find("|") >= 0)
    has_sort = has_sort.strip() == "Yes"
    has_diacr = has_diacr.strip() == "Yes"
    family_code = ""
    if family_url.find("#") >= 0:
        family_code = family_url.split("#")[1]
    other_names = list(x.strip() for x in other_names.split(",")
                       if x.strip() and x.strip() != "&#160;")
    ht = { "code": code,
           "name": lang_name,
           "other_names": other_names,
           "family_name": family_name,
           "family_code": family_code,
           "scripts": scripts,
    }
    if has_sort:
        ht["has_sort"] = has_sort
    if has_diacr:
        ht["has_diacr"] = has_diacr

    if lang_url.find(";redlink=1") < 0:
        language_url = url_prefix + lang_url
        ht["language_url"] = language_url

        # Fetch the language page and process it
        if language_url:
            time.sleep(0.3)   # Limit rate of fetching
            url = language_url
            #print("Fetching", url)
            resp = requests.get(url)
            if resp.status_code != 200:
                print("Failed with status {}".format(resp.status_code))
                continue
            text = resp.text
            for m in re.finditer(r'(?s)<table\b[^>]*?>(.*?)</table>',
                                 text):
                for mm in re.finditer(r'(?s)<tr>(.*?)</tr>', m.group(0)):
                    row = mm.group(1)
                    row = re.sub(r"<(/?)th>", r"<\1td>", row)
                    row = re.sub(r"<a\b[^>]*>([^<]*)</a>", r"\1", row)
                    cols = list(x.group(1).strip() for x in
                                re.finditer(r"<td>(.*?)</td>", row))
                    if len(cols) != 2:
                        continue
                    label, value = cols
                    if label == "Wikidata":
                        ht["wikidata"] = value
                    elif label == "Aliases":
                        for m in re.finditer(r"<li>(.*?)</li>", value):
                            alias = m.group(1)
                            if "aliases" in ht:
                                ht["aliases"].append(alias)
                            else:
                                ht["aliases"] = [alias]
    print("Language", lang_name)
    all_languages.append(ht)

print("GOT TOTAL {} LANGUAGES".format(len(all_languages)))

######################################################################
# Fetch information about language families
######################################################################

print("Fetching", fam_url)
resp = requests.get(fam_url)
if resp.status_code != 200:
    print("Fetching language family list failed")
    sys.exit(1)
text = resp.text

all_families = []

for m in re.finditer(r"(?s)<tr[^>]*>(.*?)</tr>", text):
    row = m.group(1)
    row = re.sub(r"</?code>", "", row)
    row = re.sub(r'<a\b.*?\bhref="([^"]*?)".*?>([^<]*?)</a>', r'\1|\2', row)
    cols = list(mm.group(1).strip() for mm in
                re.finditer(r"(?s)<td>(.*?)</td>", row))
    if len(cols) == 0:
        continue
    if len(cols) != 6:
        print("Unexpected #cols: {}".format(cols))
        continue
    code, family, parent, other_names, subfamilies, languages = cols
    try:
        family_url, family_name = family.split("|")
    except ValueError:
        print("Unexpected family col format: {}".format(cols))
        continue
    try:
        parent_url, parent_name = parent.split("|")
        parent_code = parent_url.split("#")[1]
    except ValueError:
        parent_url = ""
        parent_name = ""
        parent_code = ""
    other_names = list(x.strip() for x in other_names.split(",")
                       if x.strip() and x.strip() != "&#160;")
    ht = { "code": code,
           "name": family_name,
           "other_names": other_names,
           "url": url_prefix + family_url,
           "parent_code": parent_code,
           "parent_name": parent_name,
    }

    # Fetch the language family page and process it
    if family_url:
        time.sleep(0.3)   # Limit rate of fetching
        url = url_prefix + family_url
        #print("Fetching", url)
        resp = requests.get(url)
        if resp.status_code != 200:
            print("Failed with status {}".format(resp.status_code))
            continue
        text = resp.text
        for m in re.finditer(r'(?s)<table class="wikitable">(.*?)</table>',
                             text):
            for mm in re.finditer(r'(?s)<tr>(.*?)</tr>', m.group(0)):
                row = mm.group(1)
                row = re.sub(r"<(/?)th>", r"<\1td>", row)
                row = re.sub(r"<a\b[^>]*>([^<]*)</a>", r"\1", row)
                cols = list(x.group(1).strip() for x in
                            re.finditer(r"<td>(.*?)</td>", row))
                if len(cols) != 2:
                    continue
                label, value = cols
                if label == "Wikidata":
                    ht["wikidata"] = value
                elif label == "Aliases":
                    for m in re.finditer(r"<li>(.*?)</li>", value):
                        alias = m.group(1)
                        if "aliases" in ht:
                            ht["aliases"].append(alias)
                        else:
                            ht["aliases"] = [alias]
    print("Family", family_name)
    all_families.append(ht)

######################################################################
# Write information about languages and families to
# wiktextract/languages.py
######################################################################

with open("wiktextract/languages.py", "w") as f:
    f.write("# This file is autotically generated from Wiktionary by the\n")
    f.write("# extract_language_codes.py script.  DO NOT EDIT.\n")
    f.write("\n")
    f.write('all_languages = {}\n'
            ''.format(json.dumps(all_languages, sort_keys=True, indent=4)))
    f.write("\n")
    f.write('all_families = {}\n'
            ''.format(json.dumps(all_families, sort_keys=True, indent=4)))
