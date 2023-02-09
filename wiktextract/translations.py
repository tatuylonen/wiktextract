# Code related to parsing translations
#
# Copyright (c) 2019-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import copy
from wikitextprocessor import Wtp, MAGIC_FIRST, MAGIC_LAST

from .config import WiktionaryConfig
from .datautils import split_at_comma_semi, data_append, data_extend
from .form_descriptions import (classify_desc, decode_tags,
                                nested_translations_re, tr_note_re,
                                parse_translation_desc)


# Maps language names in translations to actual language names.
# E.g., "Apache" is not a language name, but "Apachean" is.
tr_langname_map = {
    "Apache": "Apachean",
}

# These names will be interpreted as script names or dialect names
# when used as a second-level name in translations.  Some script names
# are also valid language names, but it looks likes the ones that are
# also script names aren't used on the second level as language names.
# These will not be interpreted as a separate language, but will instead
# be included under the parent language with the script/dialect as a tag
# (with spaces replaced by hyphens).
script_and_dialect_names = set([
    # Scripts
    "ALUPEC",
    "Adlam",
    "Arabic",  # Script for Kashmiri
    "Bengali",
    "Burmese",
    "Carakan",
    "CJKV Characters",
    "Cyrillic",
    "Devanagari",
    "Glagolitic",
    "Gurmukhi",
    "Hebrew",  # For Aramaic
    "Jawi",
    "Khmer",
    "Latin",
    "Mongolian",
    "Roman",
    "Shahmukhi",
    "Sinhalese",
    "Syriac",  # For Aramaic
    "Classical Syriac",  # For Aramaic
    "Taraškievica",
    "Thai",
    "Uyghurjin",
    # Chinese dialects/languages
    "Cantonese",  # Variant of Chinese
    "Dungan",  # Chinese
    "Gan",  # Chinese
    "Hakka",  # Chinese
    "Hokkien",  # Chinese
    "Jin",  # Chinese
    "Mandarin",  # Chinese
    "Min Bei",  # Chinese
    "Min Dong",  # Chinese
    "Min Nan",  # Chinsese
    "Wu",  # Chinsese
    "Xiang",  # Chinese
    "Jianghuai Mandarin",  # Chinese
    "Jilu Mandarin",  # Chinese
    "Jin Mandarin",  # Chinese
    "Northern Mandarin",  # Chinese
    "Southwestern Mandarin",  # Chinese
    "Taiwanese Mandarin",  # Chinese
    "Coastal Min",  # Chinese
    "Inland Min",  # Chinese
    "Leizhou Min",  # Chinese
    "Min",  # Chinese
    "Puxian Min",  # Chinese
    "Shanghainese Wu",  # Chinese
    "Wenzhou Wu",  # Chinese
    "Wenzhou",  # Chinese
    "Hsinchu Hokkien",  # Chinese
    "Jinjiang Hokkien",  # Chinese
    "Kaohsiung Hokkien",  # Chinsese
    "Pinghua",  # Chinese
    "Eastern Punjabi",
    "Western Punjabi",
    # Various countries/regions
    "Alsace",
    "Bavaria",
    "Belgium",
    "Canada",
    "Central",
    "Cologne",
    "Fogo",
    "Föhr",
    "Föhr-Amrum",
    "Hallig",
    "Helgoland",
    "Heligoland",
    "Santiago",
    "Sylt",
    "Mooring",
    "Föhr-Amrum",
    "Vancouver Island",
    "Wiedingharde",
    "Anpezan",  # Variant of Ladin
    "Badiot",  # Ladin
    "Fascian",  # Ladin
    "Fodom",  # Ladin
    "Gherdëina",  # Ladin
    "Central Kurdish",  # Variant of Kurdish
    "Laki",  # Variant of Kurdish
    "Northern Kurdish",  # Variant of Kurdish
    "Anbarani",  # Variant of Talysh
    "Asalemi",  # Variant of Talysh
    "Upper Sorbian",  # Variant of Sorbian
    "Lower Sorbian",  # Variant of Sorbian
    "Alemannic German",  # Variant of German
    "Rhine Franconian",  # Variant of German
    "German Low German",  # Variant of Low German
    "Campidanese",  # Variant of Sardinian
    "Logudorese",  # Variant of Sardinian
    "Digor",  # Variant of Ossetian
    "Iron",  # Variant of Ossetian
    "Northern Puebla",  # Variant of Nahuatl
    "Mecayapan",  # Variant of Nathuatl
    "Egyptian Arabic",  # Variant of Arabic
    "Gulf Arabic",  # Variant of Arabic
    "Hijazi Arabic",  # Variant of Arabic
    "Moroccan Arabic",  # Variant of Arabic
    "North Levantine Arabic",  # Variant of Arabic
    "South Levantine Arabic",  # Variant of Arabic
    "Alviri",  # Variant of Alviri-Vidari
    "Vidari",  # Variant of Alviri-Vidari
    "Tashelhit",  # Variant of Berber
    "Bokmål",  # Variant of Norwegian
    "Nynorsk",  # Variant of Norwegian
    "Inari",  # Variant of Sami
    "Pite",  # Variant of Sami
    "Skolt",  # Variant of Sami
    "Mycenaean",  # Variant of Greek
    # Language varieties
    "Ancient",
    "Classical",
    "Draweno-Polabian",
    "Literary",
    "Lower",
    "Manitoba Saulteux",
    "Modern",
    "Modern Polabian",
    "Modified traditional",
    "Northern",
    "Northern and Southern",
    "Old Polabian",
    "Simplified",
    "Southern",
    "Traditional",
    "Western",
    "1708",
    "1918",
])

# These names should be interpreted as tags (as listed in the value
# space-separated) in second-level translations.
tr_second_tagmap = {
    "Föhr-Amrum, Bökingharde" : "Föhr-Amrum Bökingharde",
    "Halligen, Goesharde, Karrhard": "Halligen Goesharde Karrhard",
    "Föhr-Amrum and Sylt dialect": "Föhr-Amrum Sylt",
    "Hallig and Mooring": "Hallig Mooring",
    "Föhr-Amrum & Mooring": "Föhr-Amrum Mooring",
}

# Ignore translations that start with one of these
tr_ignore_prefixes = [
    "+",
    "Different structure used",
    "Literally",
    "No equivalent",
    "Not used",
    "Please add this translation if you can",
    "See: ",
    "Use ",
    "[Book Pahlavi needed]",
    "[book pahlavi needed]",
    "[script needed]",
    "different structure used",
    "e.g.",
    "lit.",
    "literally",
    "no equivalent",
    "normally ",
    "not used",
    "noun compound ",
    "please add this translation if you can",
    "prefix ",
    "see: ",
    "suffix ",
    "use ",
    "usually ",
]

# Ignore translations that contain one of these anywhere (case-sensitive).
# Or actually, put such translations in the "note" field rather than in "word".
tr_ignore_contains = [
    "usually expressed with ",
    " can be used ",
    " construction used",
    " used with ",
    " + ",
    "genitive case",
    "dative case",
    "nominative case",
    "accusative case",
    "absolute state",
    "infinitive of ",
    "participle of ",
    "for this sense",
    "depending on the circumstances",
    "expressed with ",
    " expression ",
    " means ",
    " is used",
    " — ",  # Used to give example sentences
    " translation",
    "not attested",
    "grammatical structure",
    "construction is used",
    "tense used",
    " lit.",
    " literally",
    "dative",
    "accusative",
    "genitive",
    "essive",
    "partitive",
    "translative",
    "elative",
    "inessive",
    "illative",
    "adessive",
    "ablative",
    "allative",
    "abessive",
    "comitative",
    "instructive",
    "particle",
    "predicative",
    "attributive",
    "preposition",
    "postposition",
    "prepositional",
    "postpositional",
    "prefix",
    "suffix",
    "translated",
]

# Ignore translations that match one of these regular expressions
tr_ignore_regexps = [
    r"^\[[\d,]+\]$",
    r"\?\?$",
    r"^\s*$",
]

# If a translation matches this regexp (with re.search), we print a debug
# message
tr_suspicious_re = re.compile(
    r" [mf][12345]$|" +
    r" [mfnc]$|" +
    r" (pf|impf|vir|nvir|anml|anim|inan|sg|pl)$|" +
    "|".join(re.escape(x) for x in
             ["; ", "* ", ": ", "[", "]",
              "{", "}", "／", "^", "literally", "lit.",
              # XXX check occurrences of ⫽, seems to be used as verb-object
              # separator but shouldn't really be part of the canonical form.
              # See e.g. 打工/Chinese
              "⫽",
              "also expressed with", "e.g.", "cf.",
              "used ", "script needed",
              "please add this translation",
              "usage "]))

# Regular expression to be searched from translation (with re.search) to check
# if it should be ignored.
tr_ignore_re = re.compile(
    "^(" + "|".join(re.escape(x) for x in tr_ignore_prefixes) + ")|" +
    "|".join(re.escape(x) for x in tr_ignore_contains) + "|" +
    "|".join(tr_ignore_regexps))  # These are not to be escaped

# These English texts get converted to tags in translations
english_to_tags = {
    "I have": "first-person singular",
    "you have": "second-person singular",
    "she has": "third-person singular feminine",
    "he has": "third-person singular masculine",
}

def parse_translation_item_text(ctx, word, data, item, sense, pos_datas,
                                lang, langcode, translations_from_template,
                                is_reconstruction, config):
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(data, dict)
    assert isinstance(item, str)
    assert sense is None or isinstance(sense, str)
    assert isinstance(pos_datas, list)
    assert lang is None or isinstance(lang, str)  # Parent item language
    assert langcode is None or isinstance(langcode, str)  # Template langcode
    assert isinstance(translations_from_template, list)
    for x in translations_from_template:
        assert isinstance(x, str)
    assert is_reconstruction in (True, False)
    assert isinstance(config, WiktionaryConfig)

    # print("parse_translation_item_text: {!r} lang={}".format(item, lang))

    if not item:
        return None

    # Find and remove nested translations from the item
    nested = list(m.group(1)
                  for m in re.finditer(nested_translations_re, item))
    if nested:
        item = re.sub(nested_translations_re, "", item)

    if re.search(r"\(\d+\)|\[\d+\]", item):
        if not item.find("numeral:"):
            ctx.debug("possible sense number in translation item: {}"
                      .format(item),
                      sortid="translations/324")

    # Translation items should start with a language name (except
    # some nested translation items don't and rely on the language
    # name from the higher level, and some append a language variant
    # name to a broader language name)
    extra_langcodes = set()
    if lang and lang in config.LANGUAGES_BY_NAME:
        extra_langcodes.add(config.LANGUAGES_BY_NAME[lang])
        # Canonicalize language name (we could have gotten it via
        # alias or other_names)
        lang = config.LANGUAGES_BY_CODE[config.LANGUAGES_BY_NAME[lang]][0]
        assert lang
    m = re.match(r"\*?\s*([-' \w][-'&, \w()]*)[:：]\s*", item)
    tags = []
    if m:
        sublang = m.group(1).strip()
        if lang is None:
            lang = sublang
        elif sublang in script_and_dialect_names:
            # If the second-level name is a script name, add it as
            # tag and keep the top-level language.
            # This helps with languages that script names
            # on the same level; those scripts may also be valid
            # language names.  See leaf/English/Translations/Pali.
            tags.append(re.sub(r" ", "-", sublang))
        elif sublang in tr_second_tagmap:
            # Certain second-level names are interpreted as tags
            # (mapped to tags).  Note that these may still have
            # separate language codes, so additional lancode
            # removal tricks may need to be played below.
            tags.extend(tr_second_tagmap[sublang].split())
        elif lang + " " + sublang in config.LANGUAGES_BY_NAME:
            lang = lang + " " + sublang
        elif sublang + " " + lang in config.LANGUAGES_BY_NAME:
            lang = sublang + " " + lang  # E.g., Ancient Egyptian
        elif sublang in config.LANGUAGES_BY_NAME:
            lang = sublang
        elif sublang[0].isupper() and classify_desc(sublang) == "tags":
            # Interpret it as a tag
            tags.append(sublang)
        else:
            # We don't recognize this prefix
            ctx.error("unrecognized prefix (language name?) in "
                      "translation item: {}".format(item),
                      sortid="translations/369")
            return None
        # Strip the language name/tag from the item
        item = item[m.end():]
    elif lang is None:
        # No mathing language prefix.  Try if it is missing colon.
        parts = item.split()
        if len(parts) > 1 and parts[0] in config.LANGUAGES_BY_NAME:
            lang = parts[0]
            item = " ".join(parts[1:])
        else:
            if item.find("__IGNORE__") < 0:
                ctx.error("no language name in translation item: {}"
                          .format(item), sortid="translations/382")
        return None

    # Map non-standard language names (e.g., "Apache" -> "Apachean")
    lang = tr_langname_map.get(lang, lang)

    # If we didn't get language code from the template, look it up
    # based on language name
    if langcode is None and lang in config.LANGUAGES_BY_NAME:
        langcode = config.LANGUAGES_BY_NAME[lang]

    # Remove (<langcode>) parts from the item.  They seem to be
    # generated by {{t+|...}}.
    if langcode:
        extra_langcodes.add(langcode)
        if "-" in langcode:
            extra_langcodes.add(langcode.split("-")[0])
        if langcode in ("zh", "yue", "cdo", "cmn", "dng", "hak",
                        "mnp", "nan", "wuu", "zh-min-nan"):
            extra_langcodes.update([
                "zh", "yue", "cdo", "cmn", "dng", "hak",
                "mnp", "nan", "wuu", "zh-min-nan"])
        elif langcode in ("nn", "nb", "no"):
            extra_langcodes.update(["no", "nn", "nb"])
        for x in extra_langcodes:
            item = re.sub(r"\s*\^?\({}\)".format(re.escape(x)),
                          "", item)

    # Map translations obtained from templates into magic characters
    # before splitting the translations list.  This way, if a comma
    # (or semicolon etc) was used inside the template, it won't get
    # split.  We restore the magic characters into the original
    # translations after splitting.  This kludge improves robustness
    # of collection translations for phrases whose translations
    # may contain commas.
    translations_from_template = list(sorted(
        translations_from_template,
        key=lambda x: len(x), reverse=True))
    tr_mappings = {}
    for i, trt in enumerate(translations_from_template):
        if not trt:
            continue
        ch = chr(MAGIC_FIRST + i)
        rex = re.escape(trt)
        if trt[0].isalnum():
            rex = r"\b" + rex
        if trt[-1].isalnum():
            rex = rex + r"\b"
        item = re.sub(rex, ch, item)
        tr_mappings[ch] = trt

    # There may be multiple translations, separated by comma
    nested.append(item)
    for item in nested:
        tagsets = []
        topics = []

        for part in split_at_comma_semi(item, extra=[
                " / ", " ／ ", r"\| furthermore: "]):
            # Substitute the magic characters back to original
            # translations (this is part of dealing with
            # phrasal translations containing commas).
            part = re.sub(r"[{:c}-{:c}]"
                          .format(MAGIC_FIRST, MAGIC_LAST),
                          lambda m: tr_mappings.get(m.group(0),
                                                    m.group(0)),
                          part)

            if part.endswith(":"):  # E.g. "salt of the earth"/Korean
                part = part[:-1].strip()
            if not part:
                continue

            # Strip language links
            tr = {"lang": lang, "code": langcode}
            if tags:
                tr["tags"] = list(tags)
                for t in tagsets:
                    tr["tags"].extend(t)
            if topics:
                tr["topics"] = list(topics)
            if sense:
                if sense.startswith(("Translations to be checked", ":The translations below need to be checked")):
                    continue  # Skip such translations
                else:
                    tr["sense"] = sense

            # Check if this part starts with (tags)
            m = re.match(r"\(([^)]+)\) ", part)
            if m:
                par = m.group(1)
                rest = part[m.end():]
                cls = classify_desc(par, no_unknown_starts=True)
                if cls == "tags":
                    tagsets2, topics2 = decode_tags(par)
                    for t in tagsets2:
                        data_extend(ctx, tr, "tags", t)
                    data_extend(ctx, tr, "topics", topics2)
                    part = rest

            # Check if this part ends with (tags).  Note that
            # note-re will mess things up if we rely on this being
            # checked later.
            m = re.search(r" +\(([^)]+)\)$", part)
            if m:
                par = m.group(1)
                rest = part[:m.start()]
                cls = classify_desc(par, no_unknown_starts=True)
                if cls == "tags":
                    tagsets2, topics2 = decode_tags(par)
                    for t in tagsets2:
                        data_extend(ctx, tr, "tags", t)
                    data_extend(ctx, tr, "topics", topics2)
                    part = rest

            # Check if this part starts with "<tags/english>: <rest>"
            m = re.match(r"([-\w() ]+): ", part)
            if m:
                par = m.group(1).strip()
                rest = part[m.end():]
                if par in ("", "see"):
                    part = "rest"
                else:
                    cls = classify_desc(par)
                    # print("par={!r} cls={!r}".format(par, cls))
                    if cls == "tags":
                        tagsets2, topics2 = decode_tags(par)
                        for t in tagsets2:
                            data_extend(ctx, tr, "tags", t)
                        data_extend(ctx, tr, "topics", topics2)
                        part = rest
                    elif cls == "english":
                        if re.search(tr_note_re, par):
                            if "note" in tr:
                                tr["note"] += "; " + par
                            else:
                                tr["note"] = par
                        else:
                            if "english" in tr:
                                tr["english"] += "; " + par
                            else:
                                tr["english"] = par
                        part = rest

            # Skip translations that our template_fn says to ignore
            # and those that contain Lua execution errors.
            if "__IGNORE__" in part:
                continue  # Contains something we want to ignore
            if part.startswith("Lua execution error"):
                continue

            # Handle certain suffixes in translations that
            # we might put in "note" but that we can actually
            # parse into tags.
            for suffix, t in (
                    (" with dative", "with-dative"),
                    (" with genitive", "with-genitive"),
                    (" with accusative", "with-accusative"),
                    (" in subjunctive", "with-subjunctive"),
                    (" and conditional mood", "with-conditional"),
                    (" - I have - you have",
                     "first-person second-person singular"),
                    (" - I have", "first-person singular"),
                    (" - you have", "second-person singular"),
            ):
                if part.endswith(suffix):
                    part = part[:-len(suffix)]
                    data_append(ctx, tr, "tags", t)
                    break

            # Handle certain prefixes in translations
            for prefix, t in (
                    ("subjunctive of ", "with-subjunctive"),
            ):
                if part.startswith(prefix):
                    part = part[len(prefix):]
                    data_append(ctx, tr, "tags", t)
                    break

            # Skip certain one-character translations entirely
            # (these could result from templates being ignored)
            if part in ",;.":
                continue

            if "english" in tr and tr["english"] in english_to_tags:
                data_extend(ctx, tr, "tags",
                            english_to_tags[tr["english"]].split())
                del tr["english"]

            # Certain values indicate it is not actually a translation.
            # See definition of tr_ignore_re to adjust.
            m = re.search(tr_ignore_re, part)
            if (m and (m.start() != 0 or m.end() != len(part) or
                       len(part.split()) > 1)):
                # This translation will be skipped because it
                # seems to be some kind of explanatory text.
                # However, let's put it in the "note" field
                # instead, unless it is one of the listed fully
                # ignored ones.
                if part in (
                        "please add this translation if you can",
                ):
                    continue
                # Save in note field
                tr["note"] = part
            else:
                # Interpret it as an actual translation
                parse_translation_desc(ctx, lang, part, tr)
                w = tr.get("word")
                if not w:
                    continue  # Not set or empty
                if w.startswith(("*", ":")):
                    w = w[1:].strip()
                if w in ("[Term?]", ":", "/", "?"):
                    continue  # These are not valid linkage targets
                if len(w) > 3 * len(word) + 20:
                    # Likely descriptive text or example
                    del tr["word"]
                    tr["note"] = w

            # Sanity check: try to detect certain suspicious
            # patterns in translations
            if "word" in tr:
                m = re.search(tr_suspicious_re, tr["word"])
                if m and lang not in (
                        "Bats",  # ^ in tree/English/Tr/Bats
                ):
                    ctx.debug("suspicious translation with {!r}: {}"
                              .format(m.group(0), tr),
                              sortid="translations/611")

            if "tags" in tr:
                tr["tags"] = list(sorted(set(tr["tags"])))

            # If we have only notes, add as-is
            if "word" not in tr:
                data_append(ctx, data, "translations", tr)
                continue

            # Split if it contains no spaces
            alts = [w]
            if " " not in w:
                # If no spaces, split by separator
                alts = re.split(r"/|／", w)
            # Note: there could be remaining slashes, but they are
            # sometimes used in ways we cannot resolve programmatically.
            # Create translations for each alternative.
            for alt in alts:
                alt = alt.strip()
                tr1 = copy.deepcopy(tr)
                if alt.startswith("*") or alt.startswith(":"):
                    alt = alt[1:].strip()
                if not alt:
                    continue
                tr1["word"] = alt
                data_append(ctx, data, "translations", tr1)

    # Return the language name, in case we have subitems
    return lang
