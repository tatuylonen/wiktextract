import re
import sys
import urllib
import hashlib

from .page import clean_node, is_panel_template
from wikitextprocessor import WikiNode, NodeKind
from .datautils import split_at_comma_semi, data_append
from .form_descriptions import parse_pronunciation_tags, classify_desc
from .tags import valid_tags

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

    def parse_expanded_zh_pron(node, parent_hdrs, ut):
        if isinstance(node, list):
            for item in node:
                parse_expanded_zh_pron(item, parent_hdrs, ut)
            return
        if not isinstance(node, WikiNode):
            return
        if node.kind != NodeKind.LIST:
            for item in node.children:
                parse_expanded_zh_pron(item, parent_hdrs, ut)
            return
        for item in node.children:
            assert isinstance(item, WikiNode)
            assert item.kind == NodeKind.LIST_ITEM
            base_item = list(x for x in item.children
                             if not isinstance(x, WikiNode) or
                                x.kind != NodeKind.LIST)
            text = clean_node(config, ctx, None, base_item)
            text = re.sub(r"(?s)\(Note:.*?\)", "", text)
            new_parent_hdrs = list(parent_hdrs)
            # look no further, here be dragons...
            if ": " in text or "：" in text:
                pron = {}
                pron["tags"] = []
                parts = re.split(r": |：", text)
                # cludge for weird synax i.e. (Hokkien: Xiamen, ...)
                if ("," in parts[1] or
                    parts[1].replace(")", "").replace("(", "").strip()
                    in valid_tags):
                    new_text = text
                    new_text = new_text.replace(" (", ",")
                    new_text = new_text.replace("(", "")
                    new_text = new_text.replace(")", "")
                    new_text = new_text.replace(":", ",")
                    # XXX this needs more attention.  It looks like this
                    # only considers the first and last subtitle, but e.g.
                    # in/Chinese has three valid levels.  @yoskari says this
                    # was a kludge to avoid too many tags in some other cases.
                    # The correct resolution is still unclear.
                    #if len(new_parent_hdrs) > 1:
                    #    new_parent_hdrs = [new_parent_hdrs[0]]
                    for hdr in new_text.split(","):
                        new_parent_hdrs.append(hdr.strip())
                else:
                    # if "Zhangzhou" in text:
                    #     print("\nFOUND IN:", text, "\n")
                    #     print("PARTS: ", repr(parts))
                    extra_tags = parts[0]
                    v = ":".join(parts[1:])
                    pron["zh-pron"] = v
                    new_parent_hdrs.append(extra_tags)
                    for hdr in new_parent_hdrs:
                        hdr = hdr.strip()
                        if hdr in config.ZH_PRON_TAGS:
                            for tag in config.ZH_PRON_TAGS[hdr]:
                                if tag not in pron["tags"]:
                                    pron["tags"].append(tag)
                        elif hdr in valid_tags:
                            if hdr not in pron["tags"]:
                                pron["tags"].append(hdr)
                        else:
                            # erhua cludge
                            if "(Standard Chinese, erhua-ed)" in text:
                                pron["tags"].append("Standard Chinese")
                                pron["tags"].append("Erhua")
                            else:
                                ut.add(hdr)
                    # convert into normal IPA format if has the IPA flag
                    if "IPA" in pron["tags"]:
                        pron["ipa"] = v
                        del pron["zh-pron"]
                        pron["tags"].remove("IPA")
                    # convert into IPA but retain the Sinological-IPA tag
                    elif "Sinological-IPA" in pron["tags"]:
                        pron["ipa"] = v
                        del pron["zh-pron"]

                    pron["tags"] = list(sorted(pron["tags"]))
                    if pron not in data.get("sounds", ()):
                        data_append(ctx, data, "sounds", pron)
            else:
                new_parent_hdrs.append(text)

            for x in item.children:
                if isinstance(x, WikiNode) and x.kind == NodeKind.LIST:
                    parse_expanded_zh_pron(x, new_parent_hdrs, ut)

    def parse_chinese_pron(contents, ut):
        if isinstance(contents, list):
            for item in contents:
                parse_chinese_pron(item, ut)
            return
        if not isinstance(contents, WikiNode):
            return
        if contents.kind != NodeKind.TEMPLATE:
            for item in contents.children:
                parse_chinese_pron(item, ut)
            return
        if (len(contents.args[0]) == 1 and
            isinstance(contents.args[0][0], str) and
            contents.args[0][0].strip() == "zh-pron"):

            src = ctx.node_to_wikitext(contents)
            expanded = ctx.expand(src, templates_to_expand={"zh-pron"})
            parsed = ctx.parse(expanded)
            parse_expanded_zh_pron(parsed, [], ut)
        else:
            for item in contents.children:
                parse_chinese_pron(item, ut)
            return

    if lang_code == "zh":
        ut = set()
        parse_chinese_pron(contents, ut)
        for hdr in ut:
            print("MISSING ZH-PRON HDR:", repr(hdr))
            sys.stdout.flush()

    # XXX change this code to iterate over node as a LIST, warning about
    # anything else.  Don't try to split by "*".
    # XXX fix enpr tags
    text = clean_node(config, ctx, data, contents,
                      template_fn=parse_pronunciation_template_fn)
    ipa_text = clean_node(config, ctx, data, contents,
                          post_template_fn=parse_pron_post_template_fn)
    have_pronunciations = False
    text_splits = re.split(r":*[*#\n]+:*", text)
    ipa_splits = re.split(r":*[*#\n]+:*", ipa_text)
    if len(text_splits) != len(ipa_splits):
        #ctx.warning("text_splits length differs from ipa_splits: "
        #            "{!r} vs. {!r}"
        #            .format(text, ipa_text))
        ipa_splits = text_splits
    prefix = None
    for text, ipa_text in zip(text_splits, ipa_splits):
        if text.find("IPA") >= 0:
            field = "ipa"
        else:
            # This is used for Rhymes, Homophones, etc
            field = "other"

        # Check if it contains Japanese "Tokyo" pronunciation with
        # special syntax
        m = re.search(r"(?m)\(Tokyo\) +([^ ]+) +\[", text)
        if m:
            pron = {field: m.group(1)}
            data_append(ctx, data, "sounds", pron)
            have_pronunciations = True
            continue

        # Check if it contains Rhymes
        m = re.match(r"\s*Rhymes: (.*)", text)
        if m:
            for ending in split_at_comma_semi(m.group(1)):
                ending = ending.strip()
                if ending:
                    pron = {"rhymes": ending}
                    data_append(ctx, data, "sounds", pron)
                    have_pronunciations = True
            continue

        # Check if it contains homophones
        m = re.search(r"(?m)\bHomophones?: (.*)", text)
        if m:
            for w in split_at_comma_semi(m.group(1)):
                w = w.strip()
                if w:
                    pron = {"homophone": w}
                    data_append(ctx, data, "sounds", pron)
                    have_pronunciations = True
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
                    data_append(ctx, data, "sounds", pron)
                    have_pronunciations = True

        m = re.search(r"\b(Syllabification|Hyphenation): ([^\s,]*)", text)
        if m:
            data_append(ctx, data, "hyphenation", m.group(2))
            have_pronunciations = True

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
        for m in re.finditer(r"(?m)/[^][/,]+?/|\[[^]0-9,/][^],/]*?\]",
                             ipa_text):
            v = m.group(0)
            # The regexp above can match file links.  Skip them.
            if v.startswith("[[File:"):
                continue
            if v == "/wiki.local/":
                continue
            if field == "ipa" and text.find("__AUDIO_IGNORE_THIS__") >= 0:
                m = re.search(r"__AUDIO_IGNORE_THIS__(\d+)__", text)
                assert m
                idx = int(m.group(1))
                if not audios[idx].get("audio-ipa"):
                    audios[idx]["audio-ipa"] = v
                if prefix:
                    audios[idx]["form"] = prefix
            else:
                pron = {field: v}
                if prefix:
                    pron["form"] = prefix
                parse_pronunciation_tags(ctx, tagstext, pron)
                data_append(ctx, data, "sounds", pron)
            have_pronunciations = True

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
                qfn = re.sub(r"/", "__slash__", qfn)
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
            if audio not in data.get("sounds", ()):
                data_append(ctx, data, "sounds", audio)
        have_pronunciations = True
    for enpr in enprs:
        if re.match(r"/[^/]+/$", enpr):
            enpr = enpr[1: -1]
        pron = {"enpr": enpr}
        # XXX need to parse enpr separately for each list item to get
        # tags correct!
        # parse_pronunciation_tags(ctx, tagstext, pron)
        if pron not in data.get("sounds", ()):
            data_append(ctx, data, "sounds", pron)
        have_pronunciations = True

    # if not have_pronunciations and not have_panel_templates:
    #     ctx.debug("no pronunciations found from pronunciation section")
