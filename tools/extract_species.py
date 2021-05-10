# This script extracts wiktextract/taxondata.py from a wikispecies dump.
# This should be done periodically (maybe once per year) to update the data
# from a fresh dump.  Note that the dump file path must be manually updated
# below.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import json
import collections
from nltk.corpus import brown
from wikitextprocessor import Wtp

english_words = set(x.lower() for x in brown.words())

dumpfile = "data/specieswiki-20210501-pages-articles.xml.bz2"

skip = [
    "{{Taxa authored}}",
    "[[Category:Agrostologists",
    "[[Category:Anthoropologists",
    "[[Category:Bacteriologists",
    "[[Category:Biochemists",
    "[[Category:Biologists",
    "[[Category:Biospeleologists",
    "[[Category:Botanists",
    "[[Category:Bryologists",
    "[[Category:Carcinologists",
    "[[Category:Cetologists",
    "[[Category:Cirripedologists",
    "[[Category:Conchologists",
    "[[Category:Ecologists",
    "[[Category:Entomologists",
    "[[Category:Geneticists",
    "[[Category:Geobiologists",
    "[[Category:Geologists",
    "[[Category:Herpetologists",
    "[[Category:Hydrobiologists",
    "[[Category:Ichthyologists",
    "[[Category:Lepidopterists",
    "[[Category:Lichenologists",
    "[[Category:Malacologists",
    "[[Category:Marine biologists",
    "[[Category:Marine zoologists",
    "[[Category:Microbiologists",
    "[[Category:Mycologists",
    "[[Category:Naturalists",
    "[[Category:Nematologists",
    "[[Category:Ornithologists",
    "[[Category:Ostracodologists",
    "[[Category:Palaeontologists",
    "[[Category:Paleobotanists",
    "[[Category:Parasitologists",
    "[[Category:Pathologists",
    "[[Category:Pedologists",
    "[[Category:People",
    "[[Category:Phycologists",
    "[[Category:Protistologists",
    "[[Category:Pteridologists",
    "[[Category:Researchers",
    "[[Category:Spongiologists",
    "[[Category:Teuthologists",
    "[[Category:Zoologists",
    "[[Category:Virologists",
    "[[Category:Databases",
    "[[Category:ISSN",
    "[[Category:Private collections",
    "[[Category:Repositories",
    "[[Category:Series identifiers",
    "[[Category:Sources",
    "[[Category:Taxon authorities",
    "[[Category:Wikispecies",
    "[[Category:Babel",
    "[[Category:People disambiguation pages",
    "[[Category:Missing or unresolved author names",
    "[[Category:Publishers",
    "[[Category:Publications",
    "[[Category:Publications by topic",
    "[[Category:Zootaxa special volumes",
    "[[Category:Biogeographic zonation",
    "[[Category:Date of publication articles",
    "[[Category:Lizard Island biodiversity projects",
    "[[Category:Lizard Island Polychaete project",
    "[[Category:Taiwan eel biodiversity",
    "[[Category:Taxonomic theory",
    "[[Category:Controversial taxon authorities",
    "[[Category:Disambiguation pages",
    "[[Category:Taxon disambiguation pages",
    "[[Category:Categories",
    "[[Category:Taxa by rank",
    "{{noref}}",
    "{{disambig}}",
    "{{disambiguation}}",
    "{{int disambig",
    "{{Authority control}}",
    "{{Refer|",
    "==Works include==",
    "== Works include ==",
    "== Later editions ==",
    "==Later editions==",
    "{{invalid taxon}}",
    "{{stub}}",
    "{{Herbarium|",
]
skip_re = re.compile("(?i)" +
                     "|".join(re.sub(r":", r"\\s*:\\s*",
                                     re.escape(x.lower()))
                              for x in skip))

def page_handler(model, title, text):
    if model != "wikitext":
        return
    title = title.strip()
    if title.find(":") >= 0:
        # Skip pages from non-main namespace
        return
    if title.find("(") >= 0:
        # Skip titles with parenthesized parts
        return
    if re.search(skip_re, text):
        # Skip pages that have any of the skip indications.  These primarily
        # skip people, institutions, publications, publishers and certain
        # special pages such as disambiguation pages.
        return

    if title.startswith("†"):
        # We don't differentiate between existing and extinct species
        title = title[1:].strip()

    # Certain titles will be skipped
    lst = title.split()
    if lst[0] in ("Unassigned", "Unallied", "Unspecified", "Unclassified",
                  "Unasssigned", "Unplaced", "Coll.",
                  "×", "X", "+", "Forschungsstation", "World", "List"):
        return

    # Determine if we should truncate the title.  Some titles have names of
    # persons or publications attached, presumably to distinguish a particular
    # version or origin of the name or several species with the same name.
    truncate_title = True
    if title.endswith("virus"):
        truncate_title = False
    if len(lst) > 1 and lst[-2].endswith("virus"):
        truncate_title = False
    if lst[-1] in ("A", "B", "C", "D", "E", "F", "I", "II", "III", "IV", "V"):
        truncate_title = False
    if not (len(lst) > 1 and any(x[0].isupper() for x in lst[1:]) and
            (len(lst[-1]) != 1 or lst[-1] not in ("virus",))):
        truncate_title = False

    if truncate_title:
        for i in range(1, len(lst)):
            if lst[i][0].isupper():
                title = " ".join(lst[:i])
                break

    return title

ctx = Wtp(cache_file="species-cache")
# Disable this for later runs to avoid recreating the cache.  Makes developing
# the code MUCH faster.  Remove the cache file before reading the dump.
# Read pages from the dump file into the cache file (Phase 1)
#list(ctx.process(dumpfile, page_handler, phase1_only=True))

# Process the pages in the dump file.
ret = list(ctx.reprocess(page_handler))

print("Count distinct titles:", len(set(ret)))
firsts = set(x.split()[0] for x in ret
             if x.find("virus") < 0 and x.find("satellite") < 0 and
             x.find("viroid") < 0)
print("Count distinct first words:", len(firsts))
words = set(x for title in ret for x in title.lower().split())
print("Count distinct latter:", len(words))

english_firsts = set(x.lower() for x in firsts if x.lower() in english_words)
print("First words shared with English:", english_firsts)
print("Count first words shared with english:", len(english_firsts))

cnts = collections.defaultdict(int)
for x in ret:
    if x.find("virus") >= 0:
        continue
    if x.find("satellite") >= 0:
        continue
    if x.find("viroid") >= 0:
        continue
    if x.find(".") >= 0:
        continue
    lst = x.split()
    length = len(lst)
    if length >= 4:
        print(x)
    cnts[length] += 1
for length, cnt in sorted(cnts.items(), key=lambda x: x[1], reverse=True):
    print("Length {}: {}".format(length, cnt))

if len(firsts) < 100000 or len(words) < 200000:
    raise RuntimeError("Too few results.  Make sure that you have enabled "
                       "Phase 1 processing (reading the dump into the cache "
                       "file).")

# Save the data in wiktextract/taxondata.py
known = list(x for x in ret if len(x.split()) > 1)
with open("wiktextract/taxondata.py", "w") as f:
    f.write("""# -*- fundamental -*-
# Information about taxonomic names extracted from wikispecies.  See
# tools/extract_species.py for the tool.
#
# This file is distributed under the same license as wikispecies, i.e.,
# Creative Commons Attribution-ShareAlike 3.0 Unported License or
# the GNU Free Documentation License.  For more information, see:
# https://species.wikimedia.org/wiki/Wikispecies:Copyrights
#
# The original specieswiki dump can be downloaded from
# https://dumps.wikimedia.org.

""")
    f.write("known_species = set({});\n".format(json.dumps(list(known))))
    f.write("\n")
    f.write("known_firsts = set({});\n".format(json.dumps(list(firsts))))
