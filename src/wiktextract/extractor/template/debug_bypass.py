import re

from wiktextract.wxr_context import WiktextractContext
from wiktextract.wxr_logging import logger

from .models import WordEntry
from .parse_utils import ADDITIONAL_EXPAND_TEMPLATES, PANEL_TEMPLATES

# Quick regex to find the template name in text
# TEMPLATE_NAME_RE = re.compile(r"{{\s*((w+\s+)*\w+)\s*(\||}})")

# (==) (Heading text) ==
# the `&` is for stuff like "Acronym & Initialism"
# HEADING_RE = re.compile(r"(?m)^(=+)\s*((\w+\s(&\s+)?)*\w+)\s*=+$")

# WHEN DOING BATCHES, PREFER LOGGER INSTEAD OF PRINT:
# print() is not multiprocessing-friendly and some stuff will eventually
# end up split, lost or mixed up with other prints.

def debug_bypass(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[WordEntry]:
    """Replacement function to handle text, print stuff out for debugging
    purposes"""
    # Handling a lot of pages can be pretty fast if you don't actually
    # process them. This function is handy when you want to do simple
    # text analysis, like searching for different kinds of headings or
    # keywords or templates.

    # For example, this would print out what the first heading (regardless
    # of depth) for each page is, and also when it encounters duplicate
    # headings.
    # found: set[str] = set()
    # for i, s in enumerate(HEADING_RE.findall(page_text)):
    #     s = s[0]
    #     if i == 0:
    #         print(f"=== First heading: '{s}'")
    #     if s in found:
    #         print(f"'{s}' duplicate")
    #         continue
    #     found.add(s)

    # Just print all the headings for sort | uniq later
    # for s in HEADING_RE.findall(page_text):
    #     print(s)

    # Check ==-headings; they should have a {{template}} on the next line:
    # lines = page_text.splitlines()
    # for i, line in enumerate(lines):
    #     if line.startswith("== "):
    #         for searchline in lines[i + 1 :]:
    #             if not searchline.startswith("{") and searchline.strip():
    #                 print()
    #                 print(f"////////////// {page_title}; on '{line}'")
    #                 print(page_text)
    #                 return []
    #             if searchline.startswith("{"):
    #                 break

    # What kind of level-4 headings are used
    # if "====" in page_text:
    #     print()
    #     print(f"///////// {page_title}")
    #     print(page_text)

    # If these targeted headings have a level 2 heading appear before them
    # print out the page; this is because stuff like "Word part" seems to
    # indicate that a new section has begun, because it appears (usually)
    # before the main POS section ("== Noun ==")
    # targets = ["Pronunc", "Etymol", "Word part"]
    # for target in ("= " + s for s in targets):
    #     found = False
    #     k = 0
    #     while True:
    #         if target in page_text[k:]:
    #             i = page_text[k:].find(target)
    #             if re.search(r"(?m)^==\s", page_text[k:k + i + 2]):
    #                 print()
    #                 print(f"//////// {page_title=}")
    #                 print(page_text)
    #                 found = True
    #                 break
    #             k = i + len(target)
    #         else:
    #             break
    #     if found:
    #         break

    # Find articles with pron or etym sections at the end after POS
    # targets = ["Pronunc", "Etymol", "Word part"]
    # for target in ("= " + s for s in targets):
    #     k = 0
    #     while (i := page_text[k:].find(target)) > 0:
    #         if not re.search(r"(?m)^==[^=]", page_text[k + i + 2:]):
    #             print()
    #             print(f"//////// {page_title=}")
    #             print(page_text)
    #             break
    #         k += i + len(target)

    # Find pages that have links inside headings
    # if re.search(r"(?m)^=+\s*[^\n]*\[[^\n]*\s*=+$", page_text):
    #     print()
    #     print(f"/////// {page_title}")
    #     print(page_text)

    # Investigate the structure of Pronunciation sections
    # lines = page_text.splitlines()
    # start = None
    # sections: list[tuple[int, int]] = []
    # for i, line in enumerate(lines):
    #     if line.startswith("=") and start is not None:
    #         sections.append((start, i))
    #         start = None
    #     if line.startswith("=") and "Pronu" in line:
    #         start = i
    # if start is not None:
    #     sections.append((start, i + 1))

    # if sections:
    #     print(f"////////  {page_title}")
    #     for a, b in sections:
    #         t = "\n".join(lines[a: min(b, len(lines)-1)])
    #         for dots in re.findall(r"(?m)^[*;#:]+", t):
    #             print(dots)
    #         for words in re.findall(r"(?m)^\s*[\(\[\w]+", t):
    #             # Found none, really
    #             print("@@ " + words)
    #         for tname in re.findall(r"{{\w+[\|}\s]", t):
    #             print(tname)



    return []

