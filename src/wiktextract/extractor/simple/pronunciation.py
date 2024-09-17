import re
from typing import Optional, Union

from wikitextprocessor import LevelNode, TemplateArgs, WikiNode
from wiktextract import WiktextractContext
from wiktextract.page import clean_node
from wiktextract.wxr_logging import logger

from .models import Sound, WordEntry
from .parse_utils import PANEL_TEMPLATES
from .simple_tags import simple_tag_map
from .text_utils import POS_STARTS_RE

DEPTH_RE = re.compile(r"([*:;]+)\s*(.*)")

REMOVE_HYPHENATION_RE = re.compile(r"(?i)\s*hyphenation\s*,?:?\s*(.+)")

def process_pron(
    wxr: WiktextractContext,
    pr_nodes: list[Union[str, WikiNode]],
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
                if desc in simple_tag_map:
                    audio.tags.extend(simple_tag_map[desc])
                else:
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
            ).strip()
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
    for i, child in enumerate(pr_nodes):
        if isinstance(child, LevelNode):
            break
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

    # How deep we are into the list tree/hierarchy; each entry is a 'level'
    # which is applied to stuff from the later or deeper in the list.
    # 0 is the applicable part-of-speech, like "noun"; sometimes pronunciation
    # sections have these in front of parts of their list to show that a
    # pronunciation only applies to the verb, for example; see 'update'.
    # 1 is for when we can't figure out what it is, so default it to refering
    # to a 'sense', or if a sense template is used then we definitely know.
    # 2 is a list of normal tag strings, if we can extract them.
    # XXX extract tags
    depth: list[tuple[str, str, list[str]]] = [("", "", [])]

    for line in pron_main.splitlines():
        line = line.strip()
        if not line:
            # An empty line; reset everything to zero
            depth = [("", "", [])]
            continue
        if m := DEPTH_RE.match(line):
            if (cur_depth := len(m.group(1)) + 1) > len(depth):
                # We know we're "deeper" into the list hierarchy, so let's
                # make a new depth level by copying the old one, and later
                # change it if needed.
                old_pos, old_sense, old_tags = depth[-1]
                cur_level = (old_pos, old_sense, old_tags)
                for i in range(len(depth), cur_depth):
                    depth.append(cur_level)
            elif cur_depth < len(depth):
                depth = depth[:cur_depth]
        else:
            wxr.wtp.warning(
                f"Line outside lists in pronunciation section: "
                f"'{line[:255]}[...]'",
                sortid="pronunciation/166",
            )
            depth = [("", "", [])]
            continue
        # This might be a POS
        rest = m.group(2).strip()
        # print(f"{rest=}")
        if m2 := POS_STARTS_RE.match(rest):
            # print(f"pos: {m2.group(0)=}")
            pos = m2.group(0)
            _, old_sense, old_tags = depth[-1]
            # Replace currently "active" POS for this level; works also for
            # level 0 and 1
            depth[-1] = (pos, old_sense, old_tags)
        elif "__SOUND" not in line:
            # This text without a pronunciation template, like {{ipa}};
            # Simple Wikt. is pretty consistent with its pron. templates, so
            # we dismiss the possibility that someone put a stray string of
            # IPA here, and treat the text as a description or a reference
            # to a sense.
            desc = m.group(2).strip()
            # XXX parse for tags
            old_pos, _, old_tags = depth[-1]
            depth[-1] = (old_pos, desc, old_tags)
        else:
            pos, desc, _ = depth[-1]
            for sound_i in re.findall(r"__SOUND_(\d+)__", line):
                i = int(sound_i)
                sound = sound_templates[i]
                sound.pos = pos or ""
                if desc:
                    if desc in simple_tag_map:
                        sound.tags.extend(simple_tag_map[desc])
                    else:
                        sound.raw_tags.extend(desc)
            # These sound datas are attached to POS data later; for this, we
            # use the sound.pos field.
        # print(f"{line}")
        # print(f"{depth}")

    # print(pron_main)
    # for st in sound_templates:
    #     print(st.model_dump_json(exclude_defaults=True))

    # print(target_data)

    # remove duplicate tags
    for st in sound_templates:
        st.tags = list(set(st.tags))
        st.raw_tags = list(set(st.raw_tags))

    if len(sound_templates) > 0:
        # completely replace sound data with new
        target_data.sounds = sound_templates

    return None
