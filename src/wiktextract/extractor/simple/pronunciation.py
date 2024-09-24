import re
from copy import copy
from typing import Optional, Union

from wikitextprocessor import LevelNode, NodeKind, TemplateArgs, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, print_tree
from wiktextract import WiktextractContext
from wiktextract.page import clean_node
from wiktextract.wxr_logging import logger

from .models import Sound, WordEntry
from .parse_utils import PANEL_TEMPLATES
from .section_titles import POS_HEADINGS
from .tags_utils import convert_tags
from .text_utils import POS_ENDING_NUMBER_RE

DEPTH_RE = re.compile(r"([*:;]+)\s*(.*)$")

REMOVE_HYPHENATION_RE = re.compile(r"(?i)\s*hyphenation\s*,?:?\s*(.+)")

POS_STARTS_RE = re.compile(r"^(.+)\s+(\d)\s*$")


def recurse_list(
    wxr: WiktextractContext,
    node: WikiNode,
    sound_templates: list[Sound],
    pos: str,
    raw_tags: list[str],
) -> tuple[Optional[str], Optional[list[str]]]:

    assert node.kind == NodeKind.LIST

    this_level_tags = raw_tags[:]

    if len(node.children) == 1:
        ### HACKYHACKHACK ###
        # ; pos or raw tags
        # * pron 1
        # * pron 2
        # The first line is a typical way Simple English Wiktionary
        # does tagging for entries "below" it, even though ";" shouldn't
        # be used to make things bold according to wikitext guidelines
        # (creates broken HTML5 and breaks screen-readers). The ";" list
        # is also separate from the "*" list, so they're completely separated
        # in our parse tree; two different LIST objects!
        return recurse_list_item(
            wxr,
            # Guaranteed LIST_ITEM
            node.children[0],  # type:ignore[arg-type]
            sound_templates,
            pos,
            this_level_tags
        )
    for child in node.children:
        recurse_list_item(
            wxr,
            # We are pretty much guaranteed a LIST will only only have
            # LIST_ITEM children.
            child,  # type:ignore[arg-type]
            sound_templates,
            pos,
            this_level_tags)

    return None, None


def recurse_list_item(
    wxr: WiktextractContext,
    node: WikiNode,
    sound_templates: list[Sound],
    pos: str,
    raw_tags: list[str],
) -> tuple[Optional[str], Optional[list[str]]]:
    """Recurse through list and list_item nodes. In some cases, a call might
    return a tuple of a POS string and list of raw tags, which can be applied
    to `pos` and `raw_tags` parameters on the same level."""

    # We can trust that contents has only stuff from the beginning of this
    # list_item because because lists would "consume" the rest.
    assert node.kind in (NodeKind.LIST_ITEM, NodeKind.ROOT)

    contents = list(node.invert_find_child(NodeKind.LIST))

    text = clean_node(wxr, None, contents).strip()

    if pos_m := POS_ENDING_NUMBER_RE.search(text):
        if text[: pos_m.start()].strip().lower() in POS_HEADINGS:
            # XXX might be better to separate out the POS-number here
            pos = text.strip().lower()
        if len(contents) == len(node.children):
            # No sublists in this node
            return pos, []  # return "noun 1"

    new_tags = []

    if "__SOUND" not in text:
        # This is text without a pronunciation template like {{ipa}}.
        # Simple Wikt. is pretty consistent with its pron. templates, so
        # we dismiss the possibility that someone put a stray string of
        # IPA here, and treat the text as a description or a reference
        # to a sense.
        # XXX extract raw tags more gracefully
        new_tags = [text.strip(": \n.,;")]
        if len(contents) == len(node.children):
            # No sublists, no POS detected; send up to be caught into new_tags2
            return None, new_tags

    line_raw_tags = []
    for sound_m in re.findall(r"([^_]*)__SOUND_(\d+)__", text):
        # findall returns a list strings, it's not a re.Match object
        new_raw_tags = re.findall(r"\(([^()]+)\)", sound_m[0])
        # logger.debug(f"{wxr.wtp.title}\n/////  {raw_tags}")

        if new_raw_tags:
            line_raw_tags = new_raw_tags

        i = int(sound_m[-1])  # (\d+)
        sound = sound_templates[i]  # the Sound object

        # These sound datas are attached to POS data later; for this, we
        # use the sound.pos field.
        sound.pos = pos or ""

        for d in raw_tags + new_tags + line_raw_tags:
            if not d.strip(" \t\n,.;:*#-–"):
                continue
            sound.raw_tags.append(d)


    this_level_tags = raw_tags + new_tags

    for li in node.find_child(NodeKind.LIST):
        new_pos, new_tags2 = recurse_list(
            wxr, li, sound_templates, pos, this_level_tags
        )
        if new_pos is not None:
            pos = new_pos
        if new_tags2 is not None:
            this_level_tags = raw_tags + new_tags2

    return None, None


def recursively_complete_sound_data(
    wxr: WiktextractContext, node: WikiNode, sound_templates: list[Sound]
) -> None:
    """Parse all the lists for pronunciation data recursively."""

    # node should be NodeKind.ROOT
    recurse_list_item(wxr, node, sound_templates, "", [])
    return None


def process_pron(
    wxr: WiktextractContext,
    node: WikiNode,
    target_data: WordEntry,
) -> None:
    """Process a Pronunciation section WikiNode, extracting Sound data entries
    which are inserted into target_data.sounds. target_data is a WordEntry, so
    can be base_data (used to complete other entries) or an individual POS
    entry."""

    # XXX: figure out a way to collect category here with clean_node so that
    # it can be properly assigned to the right POS WordEntry; currently,
    # clean_node insert the category stuff straight into whatever data object
    # is its target, which would make target_data (if used for this) basically
    # have every category from every pron-section level. We already use a hack
    # to later assign sound data to the correct POS with the `pos` field in
    # SoundEntry... Currently ignoring categories for sound.

    # print("====")
    # print_tree(pr_node)

    # We save data in parse_pronunciation_template_fn into this local list,
    # so the template_fn has to be defined inside this larger function so
    # that it has easy access to sound_templates. Can't be defined outside
    # this function either, because we need access to `wxr` from here, and
    # the template_fn signature is already set in wikitextprocessor.
    sound_templates: list[Sound] = []

    # Template handling functions are function objects that are used to process
    # a parsed template node (a WikiNode object parsed from `{{template|arg}}`
    # that hasn't been expanded yet into text). The function objects are passed
    # into certain functions like like clean_node. When the expander comes
    # across a template, before expanding the template it calls whatever was
    # passed to template_fn=. The handler function can return a string, which is
    # inserted into the returned text, or None in case nothing special will be
    # done with the template and it will use the normal expanded value.
    # post_template_fn= is the same, except it happens after the template has
    # already been expanded and receives that text as a parameter. If you want
    # to replace templates based on their names or arguments before expansion,
    # use template_fn=, if you want access to the expanded text without doing
    # it manually, use post_template_fn=
    def parse_pronunciation_template_fn(
        name: str, ht: TemplateArgs
    ) -> Optional[str]:
        lname = name.lower()
        if lname in PANEL_TEMPLATES:
            return ""
        if lname == "audio":
            filename = ht.get(1) or ""
            desc = ht.get(2) or ""
            desc = clean_node(wxr, None, [desc]).strip()
            audio = Sound(audio=filename.strip())
            if desc:
                audio.raw_tags.append(desc)
            # if current_pos:
            #     audio.pos = current_pos
            sound_templates.append(audio)
            return "__SOUND_" + str(len(sound_templates) - 1) + "__"
        if lname == "audio-ipa":
            filename = ht.get(1) or ""
            ipa = ht.get(2) or ""
            ipa = clean_node(wxr, None, [ipa])
            audio = Sound(audio=filename.strip())
            if ipa:
                audio.ipa = ipa
            sound_templates.append(audio)
            return "__SOUND_" + str(len(sound_templates) - 1) + "__"
        if lname == "ipachar":
            ipa = ht.get(1) or ""
            if ipa:
                ipa = clean_node(wxr, None, [ipa])
                audio = Sound(ipa=ipa.strip())
                sound_templates.append(audio)
                return "__SOUND_" + str(len(sound_templates) - 1) + "__"
        # Simple Wiktionary AHD = enPR
        # The IPA templates of Simple Wiktionary are simple enough that we can
        # just pull the data from the arguments and clean them up and use as
        # is; in contrast with en.wiktionary's templates, where you can have
        # processed qualifiers everywhere, it becomes necessary to do all of
        # this in post_template_fn= and parse the expanded output.
        if lname in (
            "ipa",
            "sampa",
            "ahd",
            "enpr",
        ):
            for ipa in (ht.get(x, "") for x in (1, 2, 3, 4)):
                if ipa:
                    ipa = clean_node(wxr, None, [ipa])
                    if lname == "ipa":
                        audio = Sound(ipa=ipa.strip())
                    elif lname == "sampa":
                        audio = Sound(sampa=ipa.strip())
                    elif lname in ("ahd", "enpr"):
                        audio = Sound(enpr=ipa.strip())
                    sound_templates.append(audio)
                    return "__SOUND_" + str(len(sound_templates) - 1) + "__"
        if lname in (
            "homophone",
            "homophones",
            "hmp",
        ):
            homophones = [s for s in ht.values()]
            audio = Sound()
            for hp in homophones:
                hp = clean_node(wxr, None, [hp])
                audio.homophones.append(hp)
            if homophones:
                sound_templates.append(audio)
                return "__SOUND_" + str(len(sound_templates) - 1) + "__"

        return None

    def post_parse_pronunciation_template_fn(
        name: str,
        ht: TemplateArgs,
        expanded: str,
    ) -> Optional[str]:
        lname = name.lower()
        if lname in PANEL_TEMPLATES:
            return ""
        if lname in ("hyph", "hyphenation"):
            # Add hyphenation template output straight to data
            # English hyphenation rules don't make sense. You don't break up
            # "united" into "ụ-nit-ed", that t definitely belongs at the
            # beginning of the last syllable. """you-night.... ED""". Bah.
            text = clean_node(
                wxr,
                None,
                [expanded],
            )  # clean_node strip()s by default
            m = REMOVE_HYPHENATION_RE.match(text)
            if m:
                text = m.group(1)
            if text and target_data.hyphenation:
                target_data.hyphenation += "; " + text
            elif text:
                target_data.hyphenation = text
            else:
                return None
            return ""
        return None

    # Using the already parsed parse-tree would be ideal, but because wikitext
    # is written by humans, sometimes that parse-tree does not actually reflect
    # what it *is*. A pronunciation section for Simple Wiktionary is relatively
    # simple and usually pretty similar, but if we suddenly were introduced to
    # something like a template that generates more entries that are appended to
    # the source text as bullet points, that isn't reflected in the parse tree
    # which has unexpanded templates. The parse tree also doesn't understand
    # what a line is; newlines are just parts of strings, or something that
    # would be created by a parse node implicitly. We know that a line is
    # meaningful in this context: if we use clean_node to revert the parse tree
    # and expand template nodes found in it so that we have a 'clean' raw-text
    # representation with a few remnants of wikitext syntax (like headers and
    # bullet point syntax), then we can handle each line separately and also
    # keep an eye out on the list hierarchy/depth at the same time. The expanded
    # templates can also be handled in template_fn and post_template_fn,
    # even going so far as to leave magic markers in the text that are easily
    # regexable later.
    parts: list[str] = []
    for i, child in enumerate(node.invert_find_child(LEVEL_KIND_FLAGS)):
        parts.append(
            clean_node(
                wxr,
                None,
                child,
                template_fn=parse_pronunciation_template_fn,
                post_template_fn=post_parse_pronunciation_template_fn,
                no_strip=True,
            )
        )
    pron_main = "".join(parts)

    # logger.debug(f"{wxr.wtp.title}\n{pron_main}")

    # We parse the already expanded and cleaned text; templates have been either
    # expanded or they've been replaced with something in the _template_fn
    # handler functions. We're left with a "bare-bones" parse tree that mainly
    # has list structure.
    # This is future-proofing, but it's an issue in other extractors: if a
    # template is used to generate the pronunciation section list, it has
    # been expanded here and properly parsed.
    pron_root = wxr.wtp.parse(pron_main)
    # logger.debug(print_tree(pron_root, indent=2, ret_value=True))

    recursively_complete_sound_data(wxr, pron_root, sound_templates)

    # print(pron_main)
    # for st in sound_templates:
    #     print(st.model_dump_json(exclude_defaults=True))

    # print(target_data)

    # remove duplicate tags
    for st in sound_templates:
        legit_tags, raw_tags = convert_tags(st.raw_tags)
        if len(legit_tags) > 0:
            st.tags = list(set(legit_tags))
            st.raw_tags = list(set(raw_tags))

    if len(sound_templates) > 0:
        # completely replace sound data with new
        target_data.sounds = sound_templates

    return None
