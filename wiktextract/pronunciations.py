import re
import urllib
import hashlib

from .page import clean_node, is_panel_template
from wikitextprocessor import WikiNode, NodeKind
from .datautils import split_at_comma_semi, data_append
from .form_descriptions import parse_pronunciation_tags, classify_desc
from .tags import valid_tags
from .parts_of_speech import part_of_speech_map

LEVEL_KINDS = (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
               NodeKind.LEVEL5, NodeKind.LEVEL6)

# Prefixes, tags, and regexp for finding romanizations from the pronuncation
# section
pron_romanizations = {
    " Revised Romanization ": "romanization revised",
    " Revised Romanization (translit.) ":
    "romanization revised transliteration",
    " McCune-Reischauer ": "McCune-Reischauer romanization",
    " McCune–Reischauer ": "McCune-Reischauer romanization",
    " Yale Romanization ": "Yale romanization",
}
pron_romanization_re = re.compile(
    "(?m)^(" +
    "|".join(re.escape(x) for x in
             sorted(pron_romanizations.keys(), key=lambda x: len(x),
                    reverse=True)) +
    ")([^\n]+)")


def parse_pronunciation(ctx, config, node, data, etym_data,
                        have_etym, base_data, lang_code):
    """Parses the pronunciation section from a language section on a
    page."""
    assert isinstance(node, WikiNode)
    if node.kind in LEVEL_KINDS:
        contents = node.children
    else:
        contents = [node]
    # Remove subsections, such as Usage notes.  They may contain IPAchar
    # templates in running text, and we do not want to extract IPAs from
    # those.
    contents = [x for x in contents
                if not isinstance(x, WikiNode) or x.kind not in LEVEL_KINDS]
                # Filter out only LEVEL_KINDS; 'or' is doing heavy lifting here
                # Slip through not-WikiNodes, then slip through WikiNodes that
                # are not LEVEL_KINDS.
    if (not any(isinstance(x, WikiNode) and
                x.kind == NodeKind.LIST for x in contents)):
        # expand all templates
        new_contents = []
        for l in contents:
            if (isinstance(l, WikiNode) and
               l.kind == NodeKind.TEMPLATE and
               l.args[0][0].strip() != "zh-pron"):
                temp = ctx.node_to_wikitext(l)
                temp = ctx.expand(temp)
                temp = ctx.parse(temp)
                temp = temp.children
                new_contents.extend(temp)
            else:
                new_contents.append(l)
        contents = new_contents

    if have_etym and data is base_data:
        data = etym_data
    enprs = []
    audios = []
    have_panel_templates = False

    def parse_pronunciation_template_fn(name, ht):
        nonlocal have_panel_templates
        if is_panel_template(name):
            have_panel_templates = True
            return ""
        if name == "enPR":
            enpr = ht.get(1)
            if enpr:
                enprs.append(enpr)
            return ""
        if name == "audio":
            filename = ht.get(2) or ""
            desc = ht.get(3) or ""
            desc = clean_node(config, ctx, None, [desc])
            audio = {"audio": filename.strip()}
            if desc:
                audio["text"] = desc
            m = re.search(r"\((([^()]|\([^()]*\))*)\)", desc)
            skip = False
            if m:
                par = m.group(1)
                cls = classify_desc(par)
                if cls == "tags":
                    parse_pronunciation_tags(ctx, par, audio)
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
                dial = clean_node(config, ctx, None, [dial])
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
            ipa = ht.get("ipa")
            dial = ht.get("dial")
            country = ht.get("country")
            audio = {"audio": filename.strip()}
            if dial:
                dial = clean_node(config, ctx, None, [dial])
                audio["text"] = dial
                parse_pronunciation_tags(ctx, dial, audio)
            if country:
                parse_pronunciation_tags(ctx, country, audio)
            if ipa:
                audio["audio-ipa"] = ipa
            audios.append(audio)
            # XXX do we really want to extract pronunciations from these?
            # Or are they spurious / just describing what is in the
            # audio file?
            # if ipa:
            #     pron = {"ipa": ipa}
            #     if dial:
            #         parse_pronunciation_tags(ctx, dial, pron)
            #     if country:
            #         parse_pronunciation_tags(ctx, country, pron)
            #     data_append(ctx, data, "sounds", pron)
            return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
        return None

    def parse_pron_post_template_fn(name, ht, text):
        if is_panel_template(name):
            return ""
        if name in {"q", "qualifier", "sense", "a", "accent",
                    "l", "link", "lb", "lbl", "label"}:
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
        if name in ("enPR",):
            # Some enPR pronunciations include slashes.  Strip them so
            # they don't incorrectly get taken as IPA.
            return "stripped-by-parse_pron_post_template_fn"
        return text

    def parse_expanded_zh_pron(node, parent_hdrs, specific_hdrs,
                               unknown_header_tags):

        def generate_pron(v, new_parent_hdrs, new_specific_hdrs):
            pron = {}
            pron["tags"] = []
            pron["zh-pron"] = v.strip()
            for hdr in new_parent_hdrs + new_specific_hdrs:
                hdr = hdr.strip()
                valid_hdr = re.sub("\s+", "-", hdr)
                if hdr in config.ZH_PRON_TAGS:
                    for tag in config.ZH_PRON_TAGS[hdr]:
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
                parse_expanded_zh_pron(item, parent_hdrs, specific_hdrs,
                                       unknown_header_tags)
            return
        if not isinstance(node, WikiNode):
            return
        if node.kind != NodeKind.LIST:
            for item in node.children:
                parse_expanded_zh_pron(item, parent_hdrs, specific_hdrs,
                                       unknown_header_tags)
            return
        for item in node.children:
            assert isinstance(item, WikiNode)
            assert item.kind == NodeKind.LIST_ITEM
            base_item = list(x for x in item.children
                             if not isinstance(x, WikiNode) or
                                x.kind != NodeKind.LIST)
            text = clean_node(config, ctx, None, base_item)
            # print(f"{parent_hdrs}  zhpron: {text}")  # XXX remove me
            text = re.sub(r"(?s)\(Note:.*?\)", "", text)
            # Kludge to clean up text like
            # '(Standard Chinese, erhua-ed) (旋兒／旋儿)' where
            # the hanzi are examples
            hanzi_m = re.match(r"\s*(\([^()]*\))\s*\(([^()]*)\)\s*$", text)
            if hanzi_m:
                if re.search(u'[\u4e00-\u9fff]', hanzi_m.group(2)):
                    text = hanzi_m.group(1)
            new_parent_hdrs = list(parent_hdrs)
            new_specific_hdrs = list(specific_hdrs)
            # look no further, here be dragons...
            
            if ": " in text or "：" in text:
                parts = re.split(r": |：", text)
                m = re.match(r"\s*\((([^():]+)\s*(:|：)?\s*([^():]*))\)\s*$",
                             text)
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
                        new_specific_hdrs = [s.strip() for s
                                             in m.group(1).split(",")]
                        extra_tags = extra_tags[m.end():]

                    m = re.match(r"\s*\([^()]*,[^()]*\)\s*$", extra_tags)
                    if m:
                        extra_tags = extra_tags.strip()[1:-1]  # remove parens
                        new_parent_hdrs.extend(s.strip() for s in
                                               extra_tags.split(","))
                    elif extra_tags:
                        new_parent_hdrs.append(extra_tags)

                    v = ":".join(parts[1:])

                    #  check for phrases
                    if (("，" in ctx.title) and
                       len(v.split(" ")) + v.count(",") == len(ctx.title)):
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
                        pron = generate_pron(v,
                                             new_parent_hdrs,
                                             new_specific_hdrs)

                        if pron:
                            pron["tags"] = list(sorted(pron["tags"]))
                            if pron not in data.get("sounds", ()):
                                data_append(ctx, data, "sounds", pron)
                    elif "→" in v:
                        vals = re.split("→", v)
                        for v in vals:
                            pron = generate_pron(v,
                                                 new_parent_hdrs,
                                                 new_specific_hdrs)
                            if pron:
                                m = re.match(r"([^()]+)\s*\(toneless"
                                             r" final syllable variant\)\s*",
                                             v)
                                if m:
                                    pron ["zh-pron"] = m.group(1).strip()
                                    pron["tags"].append(
                                            "toneless-final-syllable-variant")

                                pron["tags"] = list(sorted(pron["tags"]))
                                if pron not in data.get("sounds", ()):
                                    data_append(ctx, data, "sounds", pron)
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
                            pron = generate_pron(v,
                                                 new_parent_hdrs,
                                                 new_specific_hdrs)
                            if pron:
                                pron["tags"] = list(sorted(pron["tags"]))
                                if pron not in data.get("sounds", ()):
                                    data_append(ctx, data, "sounds", pron)
            else:
                new_parent_hdrs.append(text)

            for x in item.children:
                if isinstance(x, WikiNode) and x.kind == NodeKind.LIST:
                    parse_expanded_zh_pron(x, new_parent_hdrs, specific_hdrs,
                                           unknown_header_tags)

    def parse_chinese_pron(contents, unknown_header_tags):
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
        if (len(contents.args[0]) == 1 and
           isinstance(contents.args[0][0], str) and
           contents.args[0][0].strip() == "zh-pron"):

            src = ctx.node_to_wikitext(contents)
            expanded = ctx.expand(src, templates_to_expand={"zh-pron"})
            parsed = ctx.parse(expanded)
            parse_expanded_zh_pron(parsed, [], [], unknown_header_tags)
        else:
            for item in contents.children:
                parse_chinese_pron(item, unknown_header_tags)
            return

    if lang_code == "zh":
        unknown_header_tags = set()
        parse_chinese_pron(contents, unknown_header_tags)
        for hdr in unknown_header_tags:
            ctx.debug(f"Zh-pron header not found in zh_pron_tags or tags: "
                      f"{repr(hdr)}", sortid="pronunciations/296/20230324")

    def flattened_tree(lines):
        assert isinstance(lines, list)
        for line in lines:
            yield from flattened_tree1(line)

    def flattened_tree1(node):
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
            node.args = "*"
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
    def split_cleaned_node_on_newlines(contents):
        for litem in flattened_tree(contents):
            text = clean_node(config, ctx, data, litem,
                          template_fn=parse_pronunciation_template_fn)
            ipa_text = clean_node(config, ctx, data, litem,
                              post_template_fn=parse_pron_post_template_fn)
            for line, ipaline in zip(text.splitlines(), ipa_text.splitlines()):
                yield line, ipaline


    # have_pronunciations = False
    active_pos = None

    for text, ipa_text in split_cleaned_node_on_newlines(contents):
        # print(text, ipa_text)
        prefix = None
        if not text:
            continue
        if not ipa_text:
            ipa_text = text

        # Check if the text is just a word or two long, and then
        # straight up compare it to the keys in part_of_speech_map,
        # which is the simplest non-`decode_tags()` method I could
        # think of roughly checking if a line is just something along
        # the line of "Noun".
        # active_pos is used to add a temporary "pos"-field to things
        # added to "sounds", which later are filtered in page/merge_base()
        # The "pos"-key is also removed at that point, resulting in
        # pronunciation-sections being divided up if they seem to be
        # divided along part-of-speech lines.
        # XXX if necessary, expand on this; either better ways to
        # detect POS-stuff, or more ways to filter sub-blocks of
        # Pronunciation-sections.

        # Cleaning up "* " at the start of text.
        text = re.sub(r"^\**\s*", "", text)

        m = re.match(r"\s*(\w+\s?\w*)", text)
        if m:
            if m.group(1).lower() in part_of_speech_map:
                active_pos = part_of_speech_map[m.group(1).lower()]["pos"]

        if "IPA" in text:
            field = "ipa"
        else:
            # This is used for Rhymes, Homophones, etc
            field = "other"

        # Check if it contains Japanese "Tokyo" pronunciation with
        # special syntax
        m = re.search(r"(?m)\(Tokyo\) +([^ ]+) +\[", text)
        if m:
            pron = {field: m.group(1)}
            if active_pos: pron["pos"] = active_pos
            data_append(ctx, data, "sounds", pron)
            # have_pronunciations = True
            continue

        # Check if it contains Rhymes
        m = re.match(r"\s*Rhymes: (.*)", text)
        if m:
            for ending in split_at_comma_semi(m.group(1)):
                ending = ending.strip()
                if ending:
                    pron = {"rhymes": ending}
                    if active_pos: pron["pos"] = active_pos
                    data_append(ctx, data, "sounds", pron)
                    # have_pronunciations = True
            continue

        # Check if it contains homophones
        m = re.search(r"(?m)\bHomophones?: (.*)", text)
        if m:
            for w in split_at_comma_semi(m.group(1)):
                w = w.strip()
                if w:
                    pron = {"homophone": w}
                    if active_pos: pron["pos"] = active_pos
                    data_append(ctx, data, "sounds", pron)
                    # have_pronunciations = True
            continue

        # Check if it contains Phonetic hangeul
        m = re.search(r"(?m)\bPhonetic hangeul: \[([^]]+)\]", text)
        if m:
            seen = set()
            for w in m.group(1).split("/"):
                w = w.strip()
                if w and w not in seen:
                    seen.add(w)
                    pron = {"hangeul": w}
                    if active_pos: pron["pos"] = active_pos
                    data_append(ctx, data, "sounds", pron)
                    # have_pronunciations = True

        m = re.search(r"\b(Syllabification|Hyphenation): ([^\s,]*)", text)
        if m:
            data_append(ctx, data, "hyphenation", m.group(2))
            # have_pronunciations = True

        # See if it contains a word prefix restricting which forms the
        # pronunciation applies to (see amica/Latin) and/or parenthesized
        # tags.
        m = re.match(r"^[*#\s]*(([-\w]+):\s+)?\((([^()]|\([^()]*\))*?)\)",
                     text)
        if m:
            prefix = m.group(2) or ""
            tagstext = m.group(3)
            text = text[m.end():]
        else:
            m = re.match(r"^[*#\s]*([-\w]+):\s+", text)
            if m:
                prefix = m.group(1)
                tagstext = ""
                text = text[m.end():]
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

        # Find romanizations from the pronunciation section (routinely
        # produced for Korean by {{ko-IPA}})
        for m in re.finditer(pron_romanization_re, text):
            prefix = m.group(1)
            w = m.group(2).strip()
            tag = pron_romanizations[prefix]
            form = {"form": w,
                    "tags": tag.split()}
            data_append(ctx, data, "forms", form)

        # Find IPA pronunciations
        for m in re.finditer(r"(?m)/[^][\n/,]+?/"
                             r"|"
                             r"\[[^]\n0-9,/][^],/]*?\]",
                             ipa_text):
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
                if not audios[idx].get("audio-ipa"):
                    audios[idx]["audio-ipa"] = v
                if prefix:
                    audios[idx]["form"] = prefix
            else:
                pron = {field: v}
                if active_pos:
                    pron["pos"] = active_pos
                if prefix:
                    pron["form"] = prefix
                parse_pronunciation_tags(ctx, tagstext, pron)
                if active_pos:
                    pron["pos"] = active_pos
                data_append(ctx, data, "sounds", pron)
            # have_pronunciations = True

        # XXX what about {{hyphenation|...}}, {{hyph|...}}
        # and those used to be stored under "hyphenation"

        # Add data that was collected in template_fn
        if audios:
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
                    if fn in config.redirects:
                        fn = config.redirects[fn]
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
                        ogg = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/{}/{}/{}"
                               .format(digest[:1], digest[:2], qfn))
                    else:
                        ogg = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/transcoded/"
                               "{}/{}/{}/{}.ogg"
                               .format(digest[:1], digest[:2], qfn, qfn))
                    if re.search(r"(?i)\.(mp3)$", fn):
                        mp3 = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/{}/{}/{}"
                               .format(digest[:1], digest[:2], qfn))
                    else:
                        mp3 = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/transcoded/"
                               "{}/{}/{}/{}.mp3"
                               .format(digest[:1], digest[:2], qfn, qfn))
                    audio["ogg_url"] = ogg
                    audio["mp3_url"] = mp3
                    if active_pos: audio["pos"] = active_pos
                if audio not in data.get("sounds", ()):
                    data_append(ctx, data, "sounds", audio)
            # have_pronunciations = True
        audios =[]
        for enpr in enprs:
            if re.match(r"/[^/]+/$", enpr):
                enpr = enpr[1: -1]
            pron = {"enpr": enpr}
            parse_pronunciation_tags(ctx, tagstext, pron)
            if active_pos:
                pron["pos"] = active_pos
            if pron not in data.get("sounds", ()):
                data_append(ctx, data, "sounds", pron)
            # have_pronunciations = True
        enprs = []
    
    ## I have commented out the otherwise unused have_pronunciation
    ## toggles; uncomment them to use this debug print
    # if not have_pronunciations and not have_panel_templates:
    #     ctx.debug("no pronunciations found from pronunciation section",
    #               sortid="pronunciations/533")
