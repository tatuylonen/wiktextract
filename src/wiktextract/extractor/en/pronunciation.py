import hashlib
import re
import urllib
from copy import deepcopy
from dataclasses import dataclass
from typing import Iterator

from wikitextprocessor import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...clean import clean_value
from ...datautils import data_append, data_extend, split_at_comma_semi
from ...page import LEVEL_KINDS, clean_node, is_panel_template
from ...tags import valid_tags
from ...wxr_context import WiktextractContext
from ..share import create_audio_url_dict
from .form_descriptions import (
    classify_desc,
    decode_tags,
    parse_pronunciation_tags,
)
from .parts_of_speech import part_of_speech_map
from .type_utils import Hyphenation, SoundData, TemplateArgs, WordData
from .zh_pron_tags import ZH_PRON_TAGS

# Prefixes, tags, and regexp for finding romanizations from the pronuncation
# section
pron_romanizations = {
    " Revised Romanization ": "romanization revised",
    " Revised Romanization (translit.) ": "romanization revised transliteration",
    " McCune-Reischauer ": "McCune-Reischauer romanization",
    " McCune–Reischauer ": "McCune-Reischauer romanization",
    " Yale Romanization ": "Yale romanization",
}
pron_romanization_re = re.compile(
    "(?m)^("
    + "|".join(
        re.escape(x)
        for x in sorted(pron_romanizations.keys(), key=len, reverse=True)
    )
    + ")([^\n]+)"
)

IPA_EXTRACT = r"^(\((.+)\) )?(IPA⁽ᵏᵉʸ⁾|enPR): ((.+?)( \(([^(]+)\))?\s*)$"
IPA_EXTRACT_RE = re.compile(IPA_EXTRACT)


def extract_pron_template(
    wxr: WiktextractContext, tname: str, targs: TemplateArgs, expanded: str
) -> tuple[SoundData, list[SoundData]] | None:
    """In post_template_fn, this is used to handle all enPR and IPA templates
    so that we can leave breadcrumbs in the text that can later be handled
    there. We return a `base_data`  so that if there are two
    or more templates on the same line, like this:
    (Tags for the whole line, really) enPR: foo, IPA(keys): /foo/
    then we can apply base_data fields to other templates, too, if needed.
    """
    cleaned = clean_value(wxr, expanded)
    # print(f"extract_pron_template input: {tname=} {expanded=}-> {cleaned=}")
    m = IPA_EXTRACT_RE.match(cleaned)
    if not m:
        wxr.wtp.error(
            f"Text cannot match IPA_EXTRACT_RE regex: "
            f"{cleaned=}, {tname=}, {targs=}",
            sortid="en/pronunciation/54",
        )
        return None
    # for i, group in enumerate(m.groups()):
    #     print(i + 1, repr(group))
    main_qual = m.group(2) or ""
    if "qq" in targs:
        # If the template has been given a qualifier that applies to
        # every entry, but which also happens to appear at the end
        # which can be confused with the post-qualifier of a single
        # entry in the style of "... /ipa3/ (foo) (bar)", where foo
        # might not be present so the bar looks like it only might
        # apply to `/ipa3/`
        pron_body = m.group(5)
        post_qual = m.group(7)
    else:
        pron_body = m.group(4)
        post_qual = ""

    if not pron_body:
        wxr.wtp.error(
            f"Regex failed to find 'body' from {cleaned=}",
            sortid="en/pronunciation/81",
        )
        return None

    base_data: SoundData = {}
    if main_qual:
        parse_pronunciation_tags(wxr, main_qual, base_data)
    if post_qual:
        parse_pronunciation_tags(wxr, post_qual, base_data)
    # This base_data is used as the base copy for all entries from this
    # template, but it is also returned so that its contents may be applied
    # to other templates on the same line.
    # print(f"{base_data=}")

    sound_datas: list[SoundData] = []

    parts: list[list[str]] = [[]]
    inside = 0
    current: list[str] = []
    for i, p in enumerate(re.split(r"(\s*,|;|\(|\)\s*)", pron_body)):
        # Split the line on commas and semicolons outside of parens. This
        # gives us lines with "(main-qualifier) /phon/ (post-qualifier, maybe)"
        # print(f"   {i=}, {p=}")
        comp = p.strip()
        if not p:
            continue
        if comp == "(":
            if not inside and i > 0:
                if stripped := "".join(current).strip():
                    parts[-1].append("".join(current).strip())  # type:ignore[arg-type]
            current = [p]
            inside += 1
            continue
        if comp == ")":
            inside -= 1
            if not inside:
                if stripped := "".join(current).strip():
                    current.append(p)
                    parts[-1].append("".join(current).strip())  # type:ignore[arg-type]
                    current = []
            continue
        if not inside and comp in (",", ";"):
            if stripped := "".join(current).strip():
                parts[-1].append(stripped)  # type:ignore[arg-type]
                current = []
            parts.append([])
            continue
        current.append(p)
    if current:
        parts[-1].append("".join(current).strip())

    # print(f">>>>>> {parts=}")
    new_parts: list[list[str]] = []
    for entry in parts:
        if not entry:
            continue
        new_entry: list[str] = []
        i1: int = entry[0].startswith("(") and entry[0].endswith(")")
        if i1:
            new_entry.append(entry[0][1:-1].strip())
        else:
            new_entry.append("")
        i2: int = (
            entry[-1].startswith("(")
            and entry[-1].endswith(")")
            and len(entry) > 1
        )
        if i2 == 0:
            i2 = len(entry)
        else:
            i2 = -1
        new_entry.append("".join(entry[i1:i2]).strip())
        if not new_entry[-1]:
            wxr.wtp.error(
                f"Missing IPA/enPRO sound data between qualifiers?{entry=}",
                sortid="en/pronunciation/153",
            )
        if i2 == -1:
            new_entry.append(entry[-1][1:-1].strip())
        else:
            new_entry.append("")
        new_parts.append(new_entry)

    # print(f">>>>> {new_parts=}")

    for part in new_parts:
        sd = deepcopy(base_data)
        if part[0]:
            parse_pronunciation_tags(wxr, part[0], sd)
        if part[2]:
            parse_pronunciation_tags(wxr, part[2], sd)
        if tname == "enPR":
            sd["enpr"] = part[1]
        else:
            sd["ipa"] = part[1]
        sound_datas.append(sd)

    # print(f"BASE_DATA: {base_data}")
    # print(f"SOUND_DATAS: {sound_datas=}")

    return base_data, sound_datas


def parse_pronunciation(
    wxr: WiktextractContext,
    level_node: LevelNode,
    data: WordData,
    etym_data: WordData,
    have_etym: bool,
    base_data: WordData,
    lang_code: str,
) -> None:
    """Parses the pronunciation section from a language section on a
    page."""
    if level_node.kind in LEVEL_KINDS:
        contents = []
        for node in level_node.children:
            if isinstance(node, TemplateNode):
                if node.template_name == "th-pron":
                    extract_th_pron_template(wxr, data, node)
                else:
                    contents.append(node)
            else:
                contents.append(node)
    else:
        contents = [level_node]
    # Remove subsections, such as Usage notes.  They may contain IPAchar
    # templates in running text, and we do not want to extract IPAs from
    # those.
    # Filter out only LEVEL_KINDS; 'or' is doing heavy lifting here
    # Slip through not-WikiNodes, then slip through WikiNodes that
    # are not LEVEL_KINDS.
    contents = [
        x
        for x in contents
        if not isinstance(x, WikiNode) or x.kind not in LEVEL_KINDS
    ]
    if not any(
        isinstance(x, WikiNode) and x.kind == NodeKind.LIST for x in contents
    ):
        # expand all templates
        new_contents: list[str | WikiNode] = []
        for lst in contents:
            if isinstance(lst, TemplateNode) and lst.template_name != "zh-pron":
                temp = wxr.wtp.node_to_wikitext(lst)
                temp = wxr.wtp.expand(temp)
                temp_parsed = wxr.wtp.parse(temp)
                new_contents.extend(temp_parsed.children)
            else:
                new_contents.append(lst)
        contents = new_contents

    if have_etym and data is base_data:
        data = etym_data
    pron_templates: list[tuple[SoundData, list[SoundData]]] = []
    hyphenations: list[Hyphenation] = []
    audios = []
    have_panel_templates = False

    def parse_pronunciation_template_fn(
        name: str, ht: TemplateArgs
    ) -> str | None:
        """Handle pronunciation and hyphenation templates"""
        # _template_fn handles templates *before* they are expanded;
        # this allows for special handling before all the work needed
        # for expansion is done.
        nonlocal have_panel_templates
        if is_panel_template(wxr, name):
            have_panel_templates = True
            return ""
        if name == "audio":
            filename = ht.get(2) or ""
            desc = ht.get(3) or ""
            desc = clean_node(wxr, None, [desc])
            audio: SoundData = {"audio": filename.strip()}
            if desc:
                audio["text"] = desc
            m = re.search(r"\((([^()]|\([^()]*\))*)\)", desc)
            skip = False
            if m:
                par = m.group(1)
                cls = classify_desc(par)
                if cls == "tags":
                    parse_pronunciation_tags(wxr, par, audio)
                else:
                    skip = True
            if skip:
                return ""
            audios.append(audio)
            return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
        if name == "audio-IPA":
            filename = ht.get(2) or ""
            ipa = ht.get(3) or ""
            dial = ht.get("dial")
            audio = {"audio": filename.strip()}
            if dial:
                dial = clean_node(wxr, None, [dial])
                audio["text"] = dial
            if ipa:
                audio["audio-ipa"] = ipa
            audios.append(audio)
            # The problem with these IPAs is that they often just describe
            # what's in the sound file, rather than giving the pronunciation
            # of the word alone.  It is common for audio files to contain
            # multiple pronunciations or articles in the same file, and then
            # this IPA often describes what is in the file.
            return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
        if name == "audio-pron":
            filename = ht.get(2) or ""
            ipa = ht.get("ipa") or ""
            dial = ht.get("dial")
            country = ht.get("country")
            audio = {"audio": filename.strip()}
            if dial:
                dial = clean_node(wxr, None, [dial])
                audio["text"] = dial
                parse_pronunciation_tags(wxr, dial, audio)
            if country:
                parse_pronunciation_tags(wxr, country, audio)
            if ipa:
                audio["audio-ipa"] = ipa
            audios.append(audio)
            # XXX do we really want to extract pronunciations from these?
            # Or are they spurious / just describing what is in the
            # audio file?
            # if ipa:
            #     pron = {"ipa": ipa}
            #     if dial:
            #         parse_pronunciation_tags(wxr, dial, pron)
            #     if country:
            #         parse_pronunciation_tags(wxr, country, pron)
            #     data_append(data, "sounds", pron)
            return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
        if name in ("hyph", "hyphenation"):
            # {{hyph|en|re|late|caption="Hyphenation UK:"}}
            # {{hyphenation|it|quiè|to||qui|è|to||quié|to||qui|é|to}}
            # and also nocaption=1
            caption = clean_node(wxr, None, ht.get("caption", ""))
            tagsets, _ = decode_tags(caption)
            # flatten the tagsets into one; it would be really weird to have
            # several tagsets for a hyphenation caption
            tags = list(set(tag for tagset in tagsets for tag in tagset))
            # We'll just ignore any errors from tags, it's not very important
            # for hyphenation
            tags = [tag for tag in tags if not tag.startswith("error")]
            hyph_sequences: list[list[str]] = [[]]
            for text in [
                t for (k, t) in ht.items() if (isinstance(k, int) and k >= 2)
            ]:
                if not text:
                    hyph_sequences.append([])
                else:
                    hyph_sequences[-1].append(clean_node(wxr, None, text))
            for seq in hyph_sequences:
                hyphenations.append(Hyphenation(parts=seq, tags=tags))
            return ""
        return None

    def parse_pron_post_template_fn(
        name: str, ht: TemplateArgs, text: str
    ) -> str | None:
        # _post_template_fn handles templates *after* the work to expand
        # them has been done; this is exactly the same as _template_fn,
        # except with the additional expanded text as an input, and
        # possible side-effects from the expansion and recursion (like
        # calling other subtemplates that are handled in _template_fn.
        if is_panel_template(wxr, name):
            return ""
        if name in {
            "q",
            "qualifier",
            "sense",
            "a",
            "accent",
            "l",
            "link",
            "lb",
            "lbl",
            "label",
        }:
            # Kludge: when these templates expand to /.../ or [...],
            # replace the expansion by something safe.  This is used
            # to filter spurious IPA-looking expansions that aren't really
            # IPAs.  We probably don't care about these templates in the
            # contexts where they expand to something containing these.
            v = re.sub(r'href="[^"]*"', "", text)  # Ignore URLs
            v = re.sub(r'src="[^"]*"', "", v)
            if re.search(r"/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", v):
                # Note: replacing by empty results in Lua errors that we
                # would rather not have.  For example, voi/Middle Vietnamese
                # uses {{a|{{l{{vi|...}}}}, and the {{a|...}} will fail
                # if {{l|...}} returns empty.
                return "stripped-by-parse_pron_post_template_fn"
        if name in ("IPA", "enPR"):
            # Extract the data from IPA and enPR templates (same underlying
            # template) and replace them in-text with magical cookie that
            # can be later used to refer to the data's index inside
            # pron_templates.
            if pron_t := extract_pron_template(wxr, name, ht, text):
                pron_templates.append(pron_t)
                return f"__PRON_TEMPLATE_{len(pron_templates) - 1}__"
        return text

    def parse_expanded_zh_pron(
        node: WikiNode,
        parent_hdrs: list[str],
        specific_hdrs: list[str],
        unknown_header_tags: set[str],
    ) -> None:
        def generate_pron(
            v, new_parent_hdrs: list[str], new_specific_hdrs: list[str]
        ) -> SoundData | None:
            pron: SoundData = {}
            pron["tags"] = []
            pron["zh-pron"] = v.strip()
            for hdr in new_parent_hdrs + new_specific_hdrs:
                hdr = hdr.strip()
                valid_hdr = re.sub(r"\s+", "-", hdr)
                if hdr in ZH_PRON_TAGS:
                    for tag in ZH_PRON_TAGS[hdr]:
                        if tag not in pron["tags"]:
                            pron["tags"].append(tag)
                elif valid_hdr in valid_tags:
                    if valid_hdr not in pron["tags"]:
                        pron["tags"].append(valid_hdr)
                else:
                    unknown_header_tags.add(hdr)
            # convert into normal IPA format if has the IPA flag
            if "IPA" in pron["tags"]:
                pron["ipa"] = v
                del pron["zh-pron"]
                pron["tags"].remove("IPA")
            # convert into IPA but retain the Sinological-IPA tag
            elif "Sinological-IPA" in pron["tags"]:
                pron["ipa"] = v
                del pron["zh-pron"]

            if not (pron.get("zh-pron") or pron.get("ipa")):
                return None
            return pron

        if isinstance(node, list):
            for item in node:
                parse_expanded_zh_pron(
                    item, parent_hdrs, specific_hdrs, unknown_header_tags
                )
            return
        if not isinstance(node, WikiNode):
            return
        if node.kind != NodeKind.LIST:
            for item in node.children:
                parse_expanded_zh_pron(
                    item, parent_hdrs, specific_hdrs, unknown_header_tags
                )
            return
        for item in node.children:
            assert isinstance(item, WikiNode)
            assert item.kind == NodeKind.LIST_ITEM
            base_item = list(
                x
                for x in item.children
                if not isinstance(x, WikiNode) or x.kind != NodeKind.LIST
            )
            text = clean_node(wxr, None, base_item)
            # print(f"{parent_hdrs}  zhpron: {text}")  # XXX remove me
            text = re.sub(r"(?s)\(Note:.*?\)", "", text)
            # Kludge to clean up text like
            # '(Standard Chinese, erhua-ed) (旋兒／旋儿)' where
            # the hanzi are examples
            hanzi_m = re.match(r"\s*(\([^()]*\))\s*\(([^()]*)\)\s*$", text)
            if hanzi_m:
                if re.search("[\u4e00-\u9fff]", hanzi_m.group(2)):
                    text = hanzi_m.group(1)
            new_parent_hdrs = list(parent_hdrs)
            new_specific_hdrs = list(specific_hdrs)
            # look no further, here be dragons...

            if ": " in text or "：" in text:
                parts = re.split(r": |：", text)
                m = re.match(
                    r"\s*\((([^():]+)\s*(:|：)?\s*([^():]*))\)\s*$", text
                )
                # Matches lines with stuff like "(Hokkien: Xiamen, Quanzhou)"
                # thrown into new_parent_hdrs
                if m:
                    new_parent_hdrs.append(m.group(2).strip())
                    for hdr in m.group(4).split(","):
                        new_specific_hdrs.append(hdr.strip())
                else:
                    # if "Zhangzhou" in text:
                    #     print("\nFOUND IN:", text, "\n")
                    #     print("PARTS: ", repr(parts))
                    # print(f"    PARTS: {parts}")
                    extra_tags = parts[0]
                    # Kludge to handle how (Hokkien: Locations) and
                    # IPA (Specific Location) interact; this is why
                    # specific_hdrs was introduced to the soup, just
                    # to specify which are actual hierarchical higher
                    # level tags (Min'nan, Hokkien, etc.) which should
                    # always be present and then use specific_hdrs
                    # for that list of misc sublocations and subdialects
                    # that can be overridden by more specific stuff
                    # later.
                    m = re.match(r"\s*IPA\s*\((.*)\)\s*$", extra_tags)
                    if m:
                        new_parent_hdrs.append("IPA")
                        new_specific_hdrs = [
                            s.strip() for s in m.group(1).split(",")
                        ]
                        extra_tags = extra_tags[m.end() :]

                    m = re.match(r"\s*\([^()]*,[^()]*\)\s*$", extra_tags)
                    if m:
                        extra_tags = extra_tags.strip()[1:-1]  # remove parens
                        new_parent_hdrs.extend(
                            s.strip() for s in extra_tags.split(",")
                        )
                    elif extra_tags:
                        new_parent_hdrs.append(extra_tags)

                    v = ":".join(parts[1:])

                    #  check for phrases
                    if ("，" in (wxr.wtp.title or "")) and len(
                        v.split(" ")
                    ) + v.count(",") == len(wxr.wtp.title or ""):
                        # This just captures exact matches where you have
                        # the pronunciation of the whole phrase and nothing
                        # else. Split on spaces, then because we're not
                        # splitting next to a comma we need to add the
                        # count of commas so that it synchs up with the
                        # unicode string length of the original hanzi,
                        # where the comma is a separate character (unlike
                        # in the split list, where it's part of a space-
                        # separated string, like "teo⁴,".
                        vals = [v]
                        pron = generate_pron(
                            v, new_parent_hdrs, new_specific_hdrs
                        )

                        if pron:
                            pron["tags"] = list(sorted(pron["tags"]))
                            if pron not in data.get("sounds", ()):
                                data_append(data, "sounds", pron)
                    elif "→" in v:
                        vals = re.split("→", v)
                        for v in vals:
                            pron = generate_pron(
                                v, new_parent_hdrs, new_specific_hdrs
                            )
                            if pron:
                                m = re.match(
                                    r"([^()]+)\s*\(toneless"
                                    r" final syllable variant\)\s*",
                                    v,
                                )
                                if m:
                                    pron["zh-pron"] = m.group(1).strip()
                                    pron["tags"].append(
                                        "toneless-final-syllable-variant"
                                    )

                                pron["tags"] = list(sorted(pron["tags"]))
                                if pron not in data.get("sounds", ()):
                                    data_append(data, "sounds", pron)
                    else:
                        # split alternative pronunciations split
                        # with "," or " / "
                        vals = re.split(r"\s*,\s*|\s+/\s+", v)
                        new_vals = []
                        for v2 in vals:
                            if v2.startswith("/") and v2.endswith("/"):
                                # items like /kɛiŋ²¹³⁻⁵³ ^((Ø-))ŋuaŋ³³/
                                new_vals.append(v2)
                            else:
                                # split in parentheses otherwise
                                new_vals.extend(re.split(r"[()]", v2))
                        vals = new_vals
                        for v in vals:
                            pron = generate_pron(
                                v, new_parent_hdrs, new_specific_hdrs
                            )
                            if pron:
                                pron["tags"] = list(sorted(pron["tags"]))
                                if pron not in data.get("sounds", ()):
                                    data_append(data, "sounds", pron)
            else:
                new_parent_hdrs.append(text)

            for x in item.children:
                if isinstance(x, WikiNode) and x.kind == NodeKind.LIST:
                    parse_expanded_zh_pron(
                        x, new_parent_hdrs, specific_hdrs, unknown_header_tags
                    )

    def parse_chinese_pron(
        contents: list[WikiNode | str] | WikiNode | str,
        unknown_header_tags: set[str],
    ) -> None:
        if isinstance(contents, list):
            for item in contents:
                parse_chinese_pron(item, unknown_header_tags)
            return
        if not isinstance(contents, WikiNode):
            return
        if contents.kind != NodeKind.TEMPLATE:
            for item in contents.children:
                parse_chinese_pron(item, unknown_header_tags)
            return
        if (
            len(contents.largs[0]) == 1
            and isinstance(contents.largs[0][0], str)
            and contents.largs[0][0].strip() == "zh-pron"
        ):
            src = wxr.wtp.node_to_wikitext(contents)
            expanded = wxr.wtp.expand(src, templates_to_expand={"zh-pron"})
            parsed = wxr.wtp.parse(expanded)
            parse_expanded_zh_pron(parsed, [], [], unknown_header_tags)
        else:
            for item in contents.children:
                parse_chinese_pron(item, unknown_header_tags)
            return

    if lang_code == "zh":
        unknown_header_tags: set[str] = set()
        parse_chinese_pron(contents, unknown_header_tags)
        for hdr in unknown_header_tags:
            wxr.wtp.debug(
                f"Zh-pron header not found in zh_pron_tags or tags: "
                f"{repr(hdr)}",
                sortid="pronunciations/296/20230324",
            )

    def flattened_tree(lines: list[WikiNode | str]) -> Iterator[WikiNode | str]:
        assert isinstance(lines, list)
        for line in lines:
            yield from flattened_tree1(line)

    def flattened_tree1(node: WikiNode | str) -> Iterator[WikiNode | str]:
        assert isinstance(node, (WikiNode, str))
        if isinstance(node, str):
            yield node
            return
        elif node.kind == NodeKind.LIST:
            for item in node.children:
                yield from flattened_tree1(item)
        elif node.kind == NodeKind.LIST_ITEM:
            new_children = []
            sublist = None
            for child in node.children:
                if isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
                    sublist = child
                else:
                    new_children.append(child)
            node.children = new_children
            node.sarg = "*"
            yield node
            if sublist:
                yield from flattened_tree1(sublist)
        else:
            yield node

    # XXX Do not use flattened_tree more than once here, for example for
    # debug printing... The underlying data is changed, and the separated
    # sublists disappear.

    # Kludge for templates that generate several lines, but haven't
    # been caught by earlier kludges...
    def split_cleaned_node_on_newlines(
        contents: list[WikiNode | str],
    ) -> Iterator[str]:
        for litem in flattened_tree(contents):
            ipa_text = clean_node(
                wxr,
                data,
                litem,
                template_fn=parse_pronunciation_template_fn,
                post_template_fn=parse_pron_post_template_fn,
            )
            for line in ipa_text.splitlines():
                yield line

    # have_pronunciations = False
    active_pos: str | None = None

    for line in split_cleaned_node_on_newlines(contents):
        # print(f"{line=}")
        prefix: str | None = None
        earlier_base_data: SoundData | None = None
        if not line:
            continue

        split_templates = re.split(r"__PRON_TEMPLATE_(\d+)__", line)
        for i, text in enumerate(split_templates):
            if not text:
                continue
            # clean up starts at the start of the line
            text = re.sub(r"^\**\s*", "", text).strip()
            if i == 0:
                # At the start of a line, check for stuff like "Noun:"
                # for active_pos; active_pos is a temporary data field
                # given to each saved SoundData entry which is later
                # used to sort the entries into their respective PoSes.
                m = re.match(r"\s*(\w+\s?\w*)\s*:?\s*", text)
                if m:
                    if (m_lower := m.group(1).lower()) in part_of_speech_map:
                        active_pos = part_of_speech_map[m_lower]["pos"]
                        text = text[m.end() :].strip()
            if not text:
                continue
            if i % 2 == 1:
                # re.split (with capture groups) splits the lines so that
                # every even entry is a captured splitter; odd lines are either
                # empty strings or stuff around the splitters.
                base_pron_data, first_prons = pron_templates[int(text)]
                if base_pron_data:
                    earlier_base_data = base_pron_data
                    # print(f"Set {earlier_base_data=}")
                elif earlier_base_data is not None:
                    # merge data from an earlier iteration of this loop
                    for pr in first_prons:
                        if "note" in pr and "note" in earlier_base_data:
                            pr["note"] += ";" + earlier_base_data.get(
                                "note", ""
                            )
                        elif "note" in earlier_base_data:
                            pr["note"] = earlier_base_data["note"]
                        if "topics" in earlier_base_data:
                            data_extend(
                                pr, "topics", earlier_base_data["topics"]
                            )
                        if "tags" in pr and "tags" in earlier_base_data:
                            pr["tags"].extend(earlier_base_data["tags"])
                        elif "tags" in earlier_base_data:
                            pr["tags"] = sorted(set(earlier_base_data["tags"]))
                for pr in first_prons:
                    if active_pos:
                        pr["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                    if pr not in data.get("sounds", ()):
                        data_append(data, "sounds", pr)
                # This bit is handled
                continue

            if "IPA" in text:
                field = "ipa"
            else:
                # This is used for Rhymes, Homophones, etc
                field = "other"

            # Check if it contains Japanese "Tokyo" pronunciation with
            # special syntax
            m = re.search(r"(?m)\(Tokyo\) +([^ ]+) +\[", text)
            if m:
                pron: SoundData = {field: m.group(1)}  # type: ignore[misc]
                if active_pos:
                    pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                data_append(data, "sounds", pron)
                # have_pronunciations = True
                continue

            # Check if it contains Rhymes
            m = re.match(r"\s*Rhymes?: (.*)", text)
            if m:
                for ending in split_at_comma_semi(m.group(1)):
                    ending = ending.strip()
                    if ending:
                        pron = {"rhymes": ending}
                        if active_pos:
                            pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                        data_append(data, "sounds", pron)
                        # have_pronunciations = True
                continue

            # Check if it contains homophones
            m = re.search(r"(?m)\bHomophones?: (.*)", text)
            if m:
                for w in split_at_comma_semi(m.group(1)):
                    w = w.strip()
                    if w:
                        pron = {"homophone": w}
                        if active_pos:
                            pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                        data_append(data, "sounds", pron)
                        # have_pronunciations = True
                continue

            # Check if it contains Phonetic hangeul
            m = re.search(r"(?m)\bPhonetic hange?ul: \[([^]]+)\]", text)
            if m:
                seen = set()
                for w in m.group(1).split("/"):
                    w = w.strip()
                    if w and w not in seen:
                        seen.add(w)
                        pron = {"hangeul": w}
                        if active_pos:
                            pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                        data_append(data, "sounds", pron)
                        # have_pronunciations = True

            # This regex-based hyphenation detection left as backup
            m = re.search(r"\b(Syllabification|Hyphenation): *([^\n.]*)", text)
            if m:
                data_append(data, "hyphenation", m.group(2))
                commaseparated = m.group(2).split(",")
                if len(commaseparated) > 1:
                    for h in commaseparated:
                        # That second characters looks like a dash but it's
                        # actually unicode decimal code 8231, hyphenation dash
                        # Add more delimiters here if needed.
                        parts = re.split(r"-|‧", h.strip())
                        data_append(
                            data, "hyphenations", Hyphenation(parts=parts)
                        )
                    ...
                else:
                    data_append(
                        data,
                        "hyphenations",
                        Hyphenation(parts=m.group(2).split(sep="-")),
                    )
            # have_pronunciations = True

            # See if it contains a word prefix restricting which forms the
            # pronunciation applies to (see amica/Latin) and/or parenthesized
            # tags.
            m = re.match(
                r"^[*#\s]*(([-\w]+):\s+)?\((([^()]|\([^()]*\))*?)\)", text
            )
            if m:
                prefix = m.group(2) or ""
                tagstext = m.group(3)
                text = text[m.end() :]
            else:
                m = re.match(r"^[*#\s]*([-\w]+):\s+", text)
                if m:
                    prefix = m.group(1)
                    tagstext = ""
                    text = text[m.end() :]
                else:
                    # Spanish has tags before pronunciations, eg. aceite/Spanish
                    m = re.match(r".*:\s+\(([^)]*)\)\s+(.*)", text)
                    if m:
                        tagstext = m.group(1)
                        text = m.group(2)
                    else:
                        # No prefix.  In this case, we inherit prefix
                        # from previous entry.  This particularly
                        # applies for nested Audio files.
                        tagstext = ""
            if tagstext:
                earlier_base_data = {}
                parse_pronunciation_tags(wxr, tagstext, earlier_base_data)

            # Find romanizations from the pronunciation section (routinely
            # produced for Korean by {{ko-IPA}})
            for m in re.finditer(pron_romanization_re, text):
                prefix = m.group(1)
                w = m.group(2).strip()
                tag = pron_romanizations[prefix]
                form = {"form": w, "tags": tag.split()}
                data_append(data, "forms", form)

            # Find IPA pronunciations
            for m in re.finditer(
                r"(?m)/[^][\n/,]+?/" r"|" r"\[[^]\n0-9,/][^],/]*?\]", text
            ):
                v = m.group(0)
                # The regexp above can match file links.  Skip them.
                if v.startswith("[[File:"):
                    continue
                if v == "/wiki.local/":
                    continue
                if field == "ipa" and "__AUDIO_IGNORE_THIS__" in text:
                    m = re.search(r"__AUDIO_IGNORE_THIS__(\d+)__", text)
                    assert m
                    idx = int(m.group(1))
                    if idx >= len(audios):
                        continue
                    if not audios[idx].get("audio-ipa"):
                        audios[idx]["audio-ipa"] = v
                    if prefix:
                        audios[idx]["form"] = prefix
                else:
                    if earlier_base_data:
                        pron = deepcopy(earlier_base_data)
                        pron[field] = v
                    else:
                        pron = {field: v}  # type: ignore[misc]
                    if active_pos:
                        pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                    if prefix:
                        pron["form"] = prefix
                    if active_pos:
                        pron["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
                    data_append(data, "sounds", pron)
                # have_pronunciations = True

        # XXX what about {{hyphenation|...}}, {{hyph|...}}
        # and those used to be stored under "hyphenation"

        # Add data that was collected in template_fn
        for audio in audios:
            if "audio" in audio:
                # Compute audio file URLs
                fn = audio["audio"]
                # Strip certain characters, e.g., left-to-right mark
                fn = re.sub(r"[\u200f\u200e]", "", fn)
                fn = fn.strip()
                fn = urllib.parse.unquote(fn)
                # First character is usually uppercased
                if re.match(r"^[a-z][a-z]+", fn):
                    fn = fn[0].upper() + fn[1:]
                if fn in wxr.config.redirects:
                    fn = wxr.config.redirects[fn]
                # File extension is lowercased
                # XXX some words seem to need this, some don't seem to
                # have this??? what is the exact rule?
                # fn = re.sub(r"\.[^.]*$", lambda m: m.group(0).lower(), fn)
                # Spaces are converted to underscores
                fn = re.sub(r"\s+", "_", fn)
                # Compute hash digest part
                h = hashlib.md5()
                hname = fn.encode("utf-8")
                h.update(hname)
                digest = h.hexdigest()
                # Quote filename for URL
                qfn = urllib.parse.quote(fn)
                # For safety when writing files
                qfn = qfn.replace("/", "__slash__")
                if re.search(r"(?i)\.(ogg|oga)$", fn):
                    ogg = (
                        "https://upload.wikimedia.org/wikipedia/"
                        "commons/{}/{}/{}".format(digest[:1], digest[:2], qfn)
                    )
                else:
                    ogg = (
                        "https://upload.wikimedia.org/wikipedia/"
                        "commons/transcoded/"
                        "{}/{}/{}/{}.ogg".format(
                            digest[:1], digest[:2], qfn, qfn
                        )
                    )
                if re.search(r"(?i)\.(mp3)$", fn):
                    mp3 = (
                        "https://upload.wikimedia.org/wikipedia/"
                        "commons/{}/{}/{}".format(digest[:1], digest[:2], qfn)
                    )
                else:
                    mp3 = (
                        "https://upload.wikimedia.org/wikipedia/"
                        "commons/transcoded/"
                        "{}/{}/{}/{}.mp3".format(
                            digest[:1], digest[:2], qfn, qfn
                        )
                    )
                audio["ogg_url"] = ogg
                audio["mp3_url"] = mp3
                if active_pos:
                    audio["pos"] = active_pos  # type: ignore[typeddict-unknown-key]
            if audio not in data.get("sounds", ()):
                data_append(data, "sounds", audio)

        # if audios:
        #     have_pronunciations = True
        audios = []

        data_extend(data, "hyphenations", hyphenations)
        hyphenations = []

    ## I have commented out the otherwise unused have_pronunciation
    ## toggles; uncomment them to use this debug print
    # if not have_pronunciations and not have_panel_templates:
    #     wxr.wtp.debug("no pronunciations found from pronunciation section",
    #               sortid="pronunciations/533")


@dataclass
class TableHeader:
    text: str
    rowspan: int


def extract_th_pron_template(
    wxr: WiktextractContext, word_entry: WordData, t_node: TemplateNode
):
    # https://en.wiktionary.org/wiki/Template:th-pron
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    sounds = []
    for table_tag in expanded_node.find_html("table"):
        row_headers = []
        for tr_tag in table_tag.find_html("tr"):
            field = "other"
            new_headers = []
            for header in row_headers:
                if header.rowspan > 1:
                    header.rowspan -= 1
                    new_headers.append(header)
            row_headers = new_headers
            for th_tag in tr_tag.find_html("th"):
                header_str = clean_node(wxr, None, th_tag)
                if header_str.startswith("(standard) IPA"):
                    field = "ipa"
                elif header_str.startswith("Homophones"):
                    field = "homophone"
                elif header_str == "Audio":
                    field = "audio"
                elif header_str != "":
                    rowspan = 1
                    rowspan_str = th_tag.attrs.get("rowspan", "1")
                    if re.fullmatch(r"\d+", rowspan_str):
                        rowspan = int(rowspan_str)
                    row_headers.append(TableHeader(header_str, rowspan))

            for td_tag in tr_tag.find_html("td"):
                if field == "audio":
                    for link_node in td_tag.find_child(NodeKind.LINK):
                        filename = clean_node(wxr, None, link_node.largs[0])
                        if filename != "":
                            sound = create_audio_url_dict(filename)
                            sounds.append(sound)
                elif field == "homophone":
                    for span_tag in td_tag.find_html_recursively(
                        "span", attr_name="lang", attr_value="th"
                    ):
                        word = clean_node(wxr, None, span_tag)
                        if word != "":
                            sounds.append({"homophone": word})
                else:
                    raw_tag = ""
                    for html_node in td_tag.find_child_recursively(
                        NodeKind.HTML
                    ):
                        if html_node.tag == "small":
                            node_str = clean_node(wxr, None, html_node)
                            if node_str.startswith("[") and node_str.endswith(
                                "]"
                            ):
                                raw_tag = node_str.strip("[]")
                            elif len(sounds) > 0:
                                sounds[-1]["roman"] = node_str
                        elif html_node.tag == "span":
                            node_str = clean_node(wxr, None, html_node)
                            span_lang = html_node.attrs.get("lang", "")
                            span_class = html_node.attrs.get("class", "")
                            if node_str != "" and (
                                span_lang == "th" or span_class in ["IPA", "tr"]
                            ):
                                sound = {field: node_str}
                                if raw_tag != "":
                                    if raw_tag in valid_tags:
                                        data_append(sound, "tags", raw_tag)
                                    else:
                                        data_append(sound, "raw_tags", raw_tag)
                                for header in row_headers:
                                    if header.text.lower() in valid_tags:
                                        data_append(
                                            sound, "tags", header.text.lower()
                                        )
                                    else:
                                        data_append(
                                            sound, "raw_tags", header.text
                                        )
                                sounds.append(sound)

    clean_node(wxr, word_entry, expanded_node)
    data_extend(word_entry, "sounds", sounds)
