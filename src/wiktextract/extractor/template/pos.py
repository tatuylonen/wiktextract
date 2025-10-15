from wikitextprocessor import NodeKind, TemplateArgs, TemplateNode, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.page import clean_node

from .models import Example, Form, Linkage, Sense, TemplateData, WordEntry
from .section_titles import POS_HEADINGS
from .table import parse_pos_table
from .tags_utils import convert_tags_in_sense
from .text_utils import (
    ENDING_NUMBER_RE,
    STRIP_PUNCTUATION,
)

# from wiktextract.wxr_logging import logger


def remove_duplicate_forms(
    wxr: WiktextractContext, forms: list[Form]
) -> list[Form]:
    """Check for identical `forms` and remove duplicates."""
    if not forms:
        return []
    new_forms = []
    for i, form in enumerate(forms):
        for comp in forms[i + 1 :]:
            if (
                form.form == comp.form
                and form.tags == comp.tags
                and form.raw_tags == comp.raw_tags
            ):
                break
                # basically "continue" for the outer for block in this case,
                # but this will not trigger the following else-block
        else:
            # No duplicates found in for loop (exited without breaking)
            new_forms.append(form)
    if len(forms) > len(new_forms):
        # wxr.wtp.debug("Found duplicate forms", sortid="simple/pos/32")
        return new_forms
    return forms


ExOrSense = Sense | Example

IGNORED_GLOSS_TEMPLATES = ("ignoredtemplatename",)


def parse_gloss(
    wxr: WiktextractContext, parent_sense: Sense, contents: list[str | WikiNode]
) -> bool:
    """Take what is preferably a line of text and extract tags and a gloss from
    it. The data is inserted into parent_sense, and for recursion purposes
    we return a boolean that tells whether there was any gloss text in a
    lower node."""
    if len(contents) == 0:
        return False

    template_tags: list[str] = []
    found_template = False
    synonyms: list[Linkage] = []
    antonyms: list[Linkage] = []

    # Wikitext `{{template|arg}}` handler example, from Simple English Wikt.
    def gloss_template_fn(name: str, ht: TemplateArgs) -> str | None:
        # XXX Delete these and replace with specific templates to handle.
        if name in ("synonyms", "synonym", "syn"):
            # example. {{syn|case|illustration|lesson|object|part|pattern}}
            for syn in ht.values():  # ht for 'hashtable'. Tatu comes from C.
                # The template parameters of `synonyms` is simple: just a list.
                if not syn:
                    continue
                synonyms.append(Linkage(word=syn))
            # Returning a string means replacing the 'expansion' that would
            # have otherwise appeared there with it; `None` leaves things alone.
            return ""
        if name in ("antonyms", "antonym", "ant"):
            for ant in ht.values():
                if not ant:
                    continue
                antonyms.append(Linkage(word=ant))
            return ""
        # XXX Delete above.

        if name in IGNORED_GLOSS_TEMPLATES:
            return ""

        # Don't handle other templates here.
        return None

    for i, tnode in enumerate(contents):
        if (
            isinstance(tnode, str)
            and tnode.strip(STRIP_PUNCTUATION)
            or not isinstance(tnode, (TemplateNode, str))
        ):
            # When we encounter the first naked string that isn't just
            # whitespace or the first WikiNode that isn't a template.
            # This is a pretty common pattern, to have templates before
            # the main text.
            break
        if isinstance(tnode, TemplateNode):
            # Example of a template that creates some text that basically
            # say "this is a stub". Give the sense a no-gloss tag for later
            # handling.
            if tnode.template_name == "stub":
                parent_sense.raw_tags.append("no-gloss")
                return False
            tag_text = clean_node(
                wxr, parent_sense, tnode, template_fn=gloss_template_fn
            )
            if tag_text.endswith((")", "]")):
                # Simple English wiktionary, where this example is taken from,
                # is pretty good at making these templates have brackets
                tag_text = tag_text.strip(STRIP_PUNCTUATION)
                if tag_text:
                    found_template = True
                    template_tags.append(tag_text)
            else:
                # looks like normal text, so probably something {{plural of}}.
                break
    # else for the for loop: if we never break
    else:
        # If we never break, that means the last item was a tag.
        i += 1

    if found_template is True:
        contents = contents[i:]

    # The rest of the text.
    text = clean_node(
        wxr, parent_sense, contents, template_fn=gloss_template_fn
    )

    if len(synonyms) > 0:
        parent_sense.synonyms = synonyms

    if len(antonyms) > 0:
        parent_sense.antonyms = antonyms

    if len(template_tags) > 0:
        parent_sense.raw_tags.extend(template_tags)

    if len(text) > 0:
        parent_sense.glosses.append(text)
        return True

    return False


def recurse_glosses1(
    wxr: WiktextractContext,
    parent_sense: Sense,
    node: WikiNode,
) -> list[ExOrSense]:
    """Helper function for recurse_glosses"""
    ret: list[ExOrSense] = []
    found_gloss = False

    # List nodes contain only LIST_ITEM nodes, which may contain sub-LIST nodes.
    if node.kind == NodeKind.LIST:
        for child in node.children:
            if isinstance(child, str) or child.kind != NodeKind.LIST_ITEM:
                # This should never happen
                wxr.wtp.error(
                    f"{child=} is direct child of NodeKind.LIST",
                    sortid="simple/pos/44",
                )
                continue
            ret.extend(
                recurse_glosses1(wxr, parent_sense.model_copy(deep=True), child)
            )
    elif node.kind == NodeKind.LIST_ITEM:
        contents = []
        sublists = []
        broke_out = False
        for i, c in enumerate(node.children):
            # The contents ends when a new sublist begins.
            if isinstance(c, WikiNode) and c.kind == NodeKind.LIST:
                broke_out = True
                break
            contents.append(c)
        if broke_out is True:
            sublists = node.children[i:]

        # A LIST and LIST_ITEM `sarg` is basically the prefix of the line, like
        # `#` or `##:`: the token that appears at the very start of a line that
        # is used to parse the depth and structure of lists.
        # `#` Item 1
        # `##` Item 1.1
        # `##*` Example 1.1
        if node.sarg.endswith((":", "*")) and node.sarg not in (":", "*"):
            # This is either a quotation or example.
            # The `not in` filters out lines that are usually notes or random
            # stuff not inside gloss lists; see "dare".
            text = clean_node(
                wxr, parent_sense, contents
            )  # clean_node strip()s already so no need to .strip() here.
            example = Example(text=text)
            # logger.debug(f"{wxr.wtp.title}/example\n{text}")
            # We will not bother with subglosses for example entries;
            # XXX do something about it if it becomes relevant.
            return [example]
        elif node.sarg in (":", "*"):
            # Lines that start with only ":" or "*".
            # Someone probably messed up something on the Wiktionary side,
            # but some editions might use these as parts of their gloss
            # list structure. Using debug print calls we can later take
            # a look at what happened here, and then handle stuff more
            # appropriately in a later version of the extractor.
            wxr.wtp.debug(
                f"Gloss item line starts with {node.sarg=}.",
                sortid="simple/pos/214",
            )
            return []

        found_gloss = parse_gloss(wxr, parent_sense, contents)

        for sl in sublists:
            if not (isinstance(sl, WikiNode) and sl.kind == NodeKind.LIST):
                # Should not happen
                wxr.wtp.error(
                    f"Sublist is not NodeKind.LIST: {sublists=!r}",
                    sortid="simple/pos/82",
                )
                continue
            for r in recurse_glosses1(
                wxr, parent_sense.model_copy(deep=True), sl
            ):
                if isinstance(r, Example):
                    parent_sense.examples.append(r)
                else:
                    ret.append(r)

    if len(ret) > 0:
        # the recursion returned actual senses from below, so we will
        # ignore everything else (incl. any example data that might have
        # been given to parent_sense) and return that instead.
        # XXX if this becomes relevant, add the example data to a returned
        # subsense instead?
        return ret

    # If nothing came from below, then this.
    if found_gloss is True or "no-gloss" in parent_sense.raw_tags:
        return [parent_sense]

    return []


def recurse_glosses(
    wxr: WiktextractContext, node: WikiNode, data: WordEntry
) -> list[Sense]:
    """Recurse through WikiNodes to find glosses and sense-related data."""
    base_sense = Sense()
    ret = []

    for r in recurse_glosses1(wxr, base_sense, node):
        if isinstance(r, Example):
            wxr.wtp.error(
                f"Example() has bubbled to recurse_glosses: {r.json()}",
                sortid="simple/pos/glosses",
            )
            continue
        convert_tags_in_sense(r)
        ret.append(r)

    if len(ret) > 0:
        return ret

    return []


##### PART OF SPEECH SECTION #####
# ====Noun====
# {{head-template|foo}}
# # A part of speech section.
# ## An example used in extractor starting template code.
# ##: 'Foo bar baz gloss example text.'

def process_pos(
    wxr: WiktextractContext,
    node: WikiNode,
    data: WordEntry,
    # the "noun" in "Noun 2"
    pos_title: str,
    # the "2" in "Noun 2"
    pos_num: int = -1,
) -> WordEntry | None:
    """Process a part-of-speech section, like 'Noun'. `data` provides basic
    data common with other POS sections, like pronunciation or etymology."""

    # Metadata for different part-of-speech kinds.
    pos_meta = POS_HEADINGS[pos_title]
    data.pos = pos_meta["pos"]  # the internal/translated name for the POS
    data.pos_num = pos_num  # SEW uses "Noun 1", "Noun 2" style headings.

    # Sound data associated with this POS might be coming from a shared
    # section, in which case we've tried to tag the sound data with its
    # pos name + number if possible. Filter out stuff that doesn't fit.
    # This is actually pretty common, but if the edition has proper hierarchies
    # for this, doing this step might be unnecessary.
    new_sounds = []
    for sound in data.sounds:
        if len(sound.poses) == 0:
            # This sound data wasn't tagged with any specific pos section(s), so
            # we add it to everything; this is basically the default behavior.
            new_sounds.append(sound)
        else:
            for sound_pos in sound.poses:
                m = ENDING_NUMBER_RE.search(sound_pos)
                if m is not None:
                    s_num = int(m.group(1).strip())
                    s_pos = sound_pos[: m.start()].strip().lower()
                else:
                    s_pos = sound_pos.strip().lower()
                    s_num = -1
                sound_meta = POS_HEADINGS[s_pos]
                s_pos = sound_meta["pos"]
                if s_pos == data.pos and s_num == data.pos_num:
                    new_sounds.append(sound)
    data.sounds = new_sounds

    # Get child nodes *except* headings (= LEVEL).
    pos_contents = list(node.invert_find_child(LEVEL_KIND_FLAGS))

    if len(pos_contents) == 0 or (
        len(pos_contents) == 1
        and isinstance(pos_contents[0], str)
        # Just a single newline or whitespace after heading.
        and not pos_contents[0].strip()
    ):
        # Most probably a bad article.
        wxr.wtp.error(
            "No body for Part-of-speech section.", sortid="simple/pos/271"
        )
        data.senses.append(Sense(tags=["no-gloss"]))
        return data

    # Check POS templates at the start of the section (Simple English specific).
    template_tags: list[str] = []
    template_forms: list[Form] = []
    head_templates: list[TemplateData] = []

    # Typically, a Wiktionary has a word head before glosses, which contains
    # the main form of the word (usually same as the title of the article)
    # and common other forms of the word, plus qualifiers and other data
    # like that.

    # We can handle that stuff one node at a time...
    parts: list[str] = []
    for i, child in enumerate(pos_contents):
        if isinstance(child, str):
            parts.append(child)
            continue
        # TemplateNode is a subclass of WikiNode; not all kinds of nodes have
        # a subclass, but TemplateNode is handy.
        if isinstance(child, TemplateNode):
            ...
            # handle templates, append their output to parts if needed...
            template_text = clean_node(wxr, None, child, no_strip=True)
            parts.append(template_text)
            ...
            # If it was a head-specific template with stuff we want to keep,
            # add it to `head_templates` field later.
            head_templates.append(
                TemplateData(
                    name=child.template_name,
                    args={
                        str(k): clean_node(wxr, None, v)
                        for k, v in child.template_parameters.items()
                    },
                    expansion=template_text,
                    # Clean node returns an empty string for a table.
                    # expansion = clean_node(wxr, None, child)
                )
            )
        else:
            break

    head_text = "".join(parts)
    # Or we can also just call clean_node on pos_contents and use a template_fn
    # to hand template stuff.
    def head_template_fn(name: str, ht: TemplateArgs) -> str | None:
        # handle templates, put stuff into head_templates, etc.
        # If the edition uses form templates (that is, 'plural of foo'
        # style templates, that could be handled here too.
        ...

    head_text = clean_node(
        wxr, data, pos_contents, template_fn=head_template_fn
    )

    # do stuff with head_text, like parsing it for different forms.
    # Unfortunately, you often have to parse stuff by hand.

    template_tags = sorted(set(template_tags))
    data.forms.extend(template_forms)
    data.forms = remove_duplicate_forms(wxr, data.forms)
    data.tags.extend(template_tags)
    data.head_templates.extend(head_templates)


    ### Glosses after head ###
    # parts = []
    found_list = False
    got_senses = False
    for child in pos_contents[i:]:
        # Wiktionaries handle glosses the usual way: with numbered lists.
        # Each list entry is a gloss, sometimes with subglosses, but with
        # Simple English Wiktionary that seems rare.
        # logger.debug(f"{child}")
        if isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            senses = recurse_glosses(wxr, child, data)
            found_list = True
            if len(senses) > 0:
                got_senses = True
                data.senses.extend(senses)

    if not got_senses and found_list:
        wxr.wtp.error(
            "POS had a list, but the list did not return senses.",
            sortid="simple/pos/313",
        )

    # If there is not list, clump everything into one gloss.
    if not found_list:
        sense = Sense()
        found_gloss = parse_gloss(wxr, sense, pos_contents[i:])
        if found_gloss is True or len(sense.raw_tags) > 0:
            convert_tags_in_sense(sense)
            if len(sense.glosses) == 0 and "no-gloss" not in sense.tags:
                sense.tags.append("no-gloss")
            data.senses.append(sense)

    if len(data.senses) == 0:
        data.senses.append(Sense(tags=["no-gloss"]))

    return data
