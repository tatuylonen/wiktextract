import re
from collections.abc import Iterator

from wikitextprocessor import (
    HTMLNode,
    NodeKind,
    TemplateArgs,
    TemplateNode,
    WikiNode,
)
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.page import clean_node
from wiktextract.wxr_logging import logger

from .head import parse_head
from .models import Example, Linkage, Sense, TemplateData, WordEntry
from .parse_utils import (
    GREEK_LANGCODES,
    Heading,
    parse_lower_heading,
    remove_duplicate_forms,
)
from .related import process_related
from .section_titles import POS_HEADINGS
from .table import parse_table
from .tags_utils import convert_tags_in_sense
from .text_utils import (
    ENDING_NUMBER_RE,
    normalized_int,
)
from .translations import process_translations

# from wiktextract.wxr_logging import logger


def process_pos(
    wxr: WiktextractContext,
    node: WikiNode,
    data: WordEntry,
    prev_data: WordEntry | None,  # data from the last entry in this language
    # the "noun" in "Noun 2"
    pos: str,
    title: str,
    # the "2" in "Noun 2"
    pos_tags: list[str],
    pos_num: int = -1,
) -> WordEntry | None:
    """Process a part-of-speech section, like 'Noun'. `data` provides basic
    data common with other POS sections, like pronunciation or etymology."""

    # Metadata for different part-of-speech kinds.
    # print(f"{pos_title=}, {pos_tags=}, {pos_num=}")
    data.pos = pos  # the internal/translated name for the POS
    data.pos_num = pos_num  # SEW uses "Noun 1", "Noun 2" style headings.

    wxr.wtp.start_subsection(title)

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
                    s_num = normalized_int(m.group(1).strip())
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
    pos_contents = list(
        node.invert_find_child(LEVEL_KIND_FLAGS, include_empty_str=True)
        # include empty string only for debug printing?
    )

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

    # split_nodes_to_lines returns lists items on their own 'line'
    node_lines = list(split_nodes_to_lines(pos_contents))

    glosses_index = None
    glosses_lists = []
    for i, line in enumerate(node_lines):
        # Looking at the "rump" after glosses lists starts, it's simplest
        # just to pull all the list nodes, and handle them. Anything after
        # or inbetween (like categories, extra templates, tables and images)
        # can be ignored.
        if (
            len(line) == 1
            and isinstance(line[0], WikiNode)
            and line[0].kind == NodeKind.LIST
        ):
            if glosses_index is None:
                glosses_index = i
            glosses_lists.append(line[0])

    if glosses_index is None:
        # Could not find any glosses.
        # logger.info(f"  ////  {wxr.wtp.title}\n  MISSING GLOSSES")
        wxr.wtp.warning("Missing glosses", sortid="pos/20250121")
        return None

    template_data: list[TemplateData] = []
    category_data: list[str] = []
    table_nodes: list[tuple[str | None, WikiNode]] = []
    # template_depth is used as a nonlocal variable in bold_node_handler
    # to gauge how deep inside a top-level template we are; we want to
    # collect template data only for the top-level templates that are
    # visible in the wikitext, not templates inside templates.
    template_depth = 0
    top_template_name: str | None = None

    def bold_node_handler_fn(
        node: WikiNode,
    ) -> list[str | WikiNode] | None:
        """Insert special markers `__*S__` and `__*E__` around bold nodes so
        that the strings can later be split into "head-word" and "tag-words"
        parts. Collect incidental stuff, like side-tables, that are often
        put around the head."""
        assert isinstance(node, WikiNode)
        kind = node.kind
        nonlocal template_depth
        nonlocal top_template_name
        if kind == NodeKind.BOLD:
            # These are word forms almost always
            return ["__B__", *node.children, "__/B__"]
        elif kind == NodeKind.ITALIC:
            # These are almost always tag words; often 'kai' isn't italicized,
            # for example.
            return ["__I__", *node.children, "__/I__"]
        elif isinstance(node, TemplateNode):
            # Recursively expand templates so that even nodes inside the
            # the templates are handled with bold_node_handler.
            # Argh. Don't use "node_to_text", that causes bad output...
            expanded = wxr.wtp.expand(wxr.wtp.node_to_wikitext(node))
            if template_depth == 0:
                # We are looking at a top-level template in the original
                # wikitext.
                template_data.append(
                    TemplateData(
                        name=node.template_name,
                        args={
                            str(k): clean_node(wxr, None, v)
                            for k, v in node.template_parameters.items()
                        },
                        expansion=expanded,
                    )
                )
                top_template_name = node.template_name
            new_node = wxr.wtp.parse(expanded)

            template_depth += 1
            ret = wxr.wtp.node_to_text(
                new_node, node_handler_fn=bold_node_handler_fn
            )
            template_depth -= 1
            if template_depth == 0:
                top_template_name = None
            return ret
        elif kind == NodeKind.LINK:
            if not isinstance(node.largs[0][0], str):
                return None
            if node.largs[0][0].startswith("Κατηγορία:"):
                category_data.append(node.largs[0][0][len("Κατηγορία:") :])
                return [""]
            if node.largs[0][0].startswith("Αρχείο:"):
                return [""]
            # Often forms are 'formatted' with links, so let's mark these
            # too.
            return [
                "__L__",
                # unpacking a list-comprehension, unpacking into a list
                # seems to be more performant than adding lists together.
                *(
                    wxr.wtp.node_to_text(
                        node.largs[1:2] or node.largs[0],
                        node_handler_fn=bold_node_handler_fn,
                    )
                    # output the "visible" half of the link.
                ),
                # XXX collect link data if it turns out to be important.
                "__/L__",
            ]
            # print(f"{node.largs=}")

        elif kind in {
            NodeKind.TABLE,
        }:
            # XXX Handle tables here
            # template depth and top-level template name
            nonlocal table_nodes
            table_nodes.append((top_template_name, node))
            return [""]
        return None

    # Get Head Line
    # Head *should* be immediately before the glosses...
    # print(node_lines[:glosses_index])
    found_head = False

    for line in reversed(node_lines[:glosses_index]):
        template_data = []
        template_depth = 0
        stripped = wxr.wtp.node_to_text(
            line, node_handler_fn=bold_node_handler_fn
        ).strip()
        if not stripped:
            continue
        if not found_head and parse_head(wxr, data, stripped):
            # print(data)
            found_head = True
    if not found_head:
        # There are a bunch of Greek Wiktionary articles with POS sections
        # without heads, but they seem to always follow ones with heads;
        # in this case, the result is just not including any `forms` field
        # for these (or copying the previous one).

        if prev_data is None:
            wxr.wtp.warning(
                f"Part of speech missing head: {wxr.wtp.title}",
                sortid="pos/460/20250104",
            )
        else:
            # No head found, copy previous (in this language)
            data.forms = [
                form.model_copy(deep=True) for form in prev_data.forms
            ]

    if len(template_data) > 0:
        data.head_templates = template_data
        # logger.info(
        #     f"    //// {wxr.wtp.title}\n   >>>"
        #     + "\n   >>>".join(repr(td) for td in template_data)
        # )

    if len(table_nodes) > 0:
        for template_name, table_node in table_nodes:
            # XXX template_name
            parse_table(
                wxr,
                table_node,
                data,
                data.lang_code in GREEK_LANGCODES,
                template_name=template_name or "",
            )

    data.forms = remove_duplicate_forms(wxr, data.forms)

    # Ignore images and files
    # 2025-01-17 13:10:10,035 INFO:   ////  Ηρόδοτος
    # //// [[Αρχείο:Herodotus Massimo Inv124478.jpg|200px|thumb|[[προτομή]] του Ηροδότου]]

    # Have to ignore {{(( specifically. Creates columns.
    # 2025-01-17 13:10:11,059 INFO:   ////  κάνω
    #   //// {{((|width=97%}}

    # logger.info(f"<<<<<<<<< {wxr.wtp.title}\n<<<" + "\n<<<".join(pparts))
    # see: free -> {{en-verb-'free'}} creates a floating inflection table
    # followed by the usual head template

    # see: τηλεομοιοτυπία
    # '''{{PAGENAME}}''' {{θ}}
    # theta is basically {{f|...}}

    # see: θηλυκός
    # '''{{PAGENAME}}, -ή''' ''και'' '''-ιά, -ό'''
    # pagename, -e and -ia, -o, no indication of what these mean

    # Ιόνια νησιά
    # >>>'''{{PAGENAME}}''' ''πληθυντικός του'' [[ιόνιος|Ιόνιο]] [[νησί]]
    # plural of 'Ionian island'

    # >>>>>>>>> free
    # >>>{{en-adj-r}}  # floating table
    # >>>{{τ|en|{{PAGENAME}}}}, ''συγκριτικός'' '''freer''', ''υπερθετικός'' '''freest'''
    # pretty consistent bolding and italics

    # genus
    # {{τ|la|{{PAGENAME}}}} {{ο}} ([[γενική]]: generis) (3ης [[κλίση]]ς)

    # ουδέτερος
    # >>>'''{{PAGENAME}} -η -ο'''

    #  καφέ
    # >>>'''{{PAGENAME}}''' {{ακλ|επίθ}}
    # aklitos, uninflected

    # καφέ
    # >>>[[Αρχείο:Cafe Museum - Vienna (5402363918).jpg|μικρογραφία|τραπέζι σε βιενέζικο '''καφέ''']]
    # >>>'''{{PAGENAME}}''' {{ο}} {{ακλ|ουδ}}
    # Ignore images

    # κρόκος
    # >>>{| align="right"
    # >>>
    # >>>|-
    # >>>
    # >>>|[[Αρχείο:Crocus sativus1.jpg|thumb|150px|Άνθη '''κρόκου''' (''Crocus sativus'').]]
    # >>>
    # >>>
    # >>>|[[Αρχείο:Raw egg.jpg|thumb|200px|Ο '''κρόκος''' ενός αβγού.]]
    # >>>
    # >>>
    # >>>|}
    # >>>
    # >>>'''{{PAGENAME}}''' {{α}}

    #     p
    # >>>'''{{PAGENAME}}''' ''πεζό'' (''κεφαλαίο:'' '''{{l|P|la}}''')
    # lowercase, uppercase

    # Δημόκριτος
    # >>>'''{{PAGENAME}}'''
    # >>># {{όνομα||α}}
    # >>>{{clear}}
    # Clear is just formatting to move the line down where there are empty
    # margins.

    # BIG ASSUMPTION: let us assume that Greek Wiktionary doesn't use templates
    # that generate multiline text that is part of head. That is, we can see
    # each newline because they are in strings, and when something that does
    # generate virtual newlines (list) pops up, that's when the head portion
    # ends.
    # Greek Wiktionary head sections look like this:
    # > Pre-head templates that create side-tables, like inflections
    # > Possible formatting templates like {{clear}} that should be ignored
    # > Head template last before glosses list
    # > Clear again...
    # > Glosses list tree, where we can stop.
    # We can create "lines" of these by looping over the items in pos_content
    # and looking for newlines in strings, because that's where they mainly
    # should be (except side-table templates). We handle earlier lines
    # differently than the last line before the glosses list, which is the
    # head.

    # return None

    # ======================

    ### Glosses after head ###
    # parts = []
    got_senses = False
    for lst in glosses_lists:
        # Wiktionaries handle glosses the usual way: with numbered lists.
        # Each list entry is a gloss, sometimes with subglosses, but with
        # Simple English Wiktionary that seems rare.
        # logger.debug(f"{lst}")
        senses = recurse_glosses(wxr, lst, data)
        if len(senses) > 0:
            got_senses = True
            data.senses.extend(senses)

    if not got_senses and len(glosses_lists) > 0:
        wxr.wtp.error(
            "POS had a list, but the list did not return senses.",
            sortid="simple/pos/313",
        )

    # If there is no list, clump everything into one gloss.
    # if not len(glosses_lists > 0):
    #     sense = Sense()
    #     found_gloss = parse_gloss(wxr, sense, pos_contents[i:])
    #     if found_gloss is True or len(sense.raw_tags) > 0:
    #         convert_tags_in_sense(sense)
    #         if len(sense.glosses) == 0 and "no-gloss" not in sense.tags:
    #             sense.tags.append("no-gloss")
    #         data.senses.append(sense)

    if len(data.senses) == 0:
        data.senses.append(Sense(tags=["no-gloss"]))

    #####
    #####
    # TEMP DEBUG PRINTS

    pos_sublevels = list(
        node.find_child(LEVEL_KIND_FLAGS)
        # include empty string only for debug printing?
    )

    for sl in pos_sublevels:
        subtitle = clean_node(wxr, None, sl.largs[0]).lower().strip()

        type, pos, heading_name, tags, num, ok = parse_lower_heading(
            wxr, subtitle
        )

        # if type == Heading.Translation:
        #     process_translations(wxr, data, sl)
        # elif type == Heading.Infl:
        #     process_inflection_section(wxr, data, sl)
        if type == Heading.Related:
            process_related(wxr, data, sl)
        if type not in (
            Heading.Translation,
            Heading.Ignored,
            Heading.Translation,
            Heading.Infl,
            Heading.Related,
        ):
            ...
#             expanded = wxr.wtp.expand(wxr.wtp.node_to_wikitext(sl))
#             text = clean_node(wxr, None, sl)
#             logger.warning(
#                 f"""
# {wxr.wtp.title}: {type}, '{heading_name}', {ok=}
# {expanded}

# ###########################
# """
#             )

    #####
    #####
    return data


ExOrSense = Sense | Example


IGNORED_GLOSS_TEMPLATES = ("ignoredtemplatename",)

PARENS_BEFORE_RE = re.compile(r"\s*(\([^()]+\)\s*)+")
ITER_PARENS_RE = re.compile(r"\(([^()]+)\)")


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
        # if name in ("synonyms", "synonym", "syn"):
        #     # example. {{syn|case|illustration|lesson|object|part|pattern}}
        #     for syn in ht.values():  # ht for 'hashtable'. Tatu comes from C.
        #         # The template parameters of `synonyms` is simple: just a list.
        #         if not syn:
        #             continue
        #         synonyms.append(Linkage(word=syn))
        #     # Returning a string means replacing the 'expansion' that would
        #     # have otherwise appeared there with it; `None` leaves things alone.
        #     return ""
        # if name in ("antonyms", "antonym", "ant"):
        #     for ant in ht.values():
        #         if not ant:
        #             continue
        #         antonyms.append(Linkage(word=ant))
        #     return ""
        # # XXX Delete above.

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

    # Greek Wiktionary uses a lot of template-less tags.
    if parens_n := PARENS_BEFORE_RE.match(text):
        text = text[parens_n.end() :]
        blocks = ITER_PARENS_RE.findall(parens_n.group(0))
        parent_sense.raw_tags.extend(blocks)

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

    # Pydantic stuff doesn't play nice with Tatu's manual dict manipulation
    # functions, so we'll use a dummy dict here that we then check for
    # content and apply to `parent_sense`.
    dummy_parent: dict = {}

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
            text = clean_node(wxr, dummy_parent, contents).strip("⮡ \n")
            example = Example(text=text)
            # logger.debug(f"{wxr.wtp.title}/example\n{text}")
            if len(sublists) > 0:
                translation = clean_node(wxr, dummy_parent, sublists).strip(
                    "#*: \n"
                )
                if translation != "":
                    example.translation = translation

            for k, v in dummy_parent.items():
                if k == "categories":
                    parent_sense.categories.extend(v)
            dummy_parent = {}

            return [example]

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


def split_nodes_to_lines(
    nodes: list[WikiNode | str],
) -> Iterator[list[WikiNode | str]]:
    """Take a list of nodes and split up the list into lines.
    This could be done by using node_to_wikitext() to reverse the parsing,
    and then you could parse the individual lines after splitting the text,
    but it seems unnecessary in the context of Greek Wiktionary PoS sections.
    """
    parts: list[WikiNode | str] = []
    for node in nodes:
        if isinstance(node, WikiNode):
            # Lists are returned as whole, they're their own line
            if node.kind == NodeKind.LIST:
                if len(parts) > 0:
                    yield parts
                    parts = []
                yield [node]
                continue
            if isinstance(node, TemplateNode) and node.template_name in (
                # Ignore specific templates, like {{((}} that bookends a column.
                "((",
                "))",
                "clear",
                "κλείδα-ελλ",
            ):
                continue
            parts.append(node)
        else:
            if "\n" in node:
                split_string = node.splitlines()
                for spl in split_string[:-1]:
                    if spl:
                        parts.append(spl)
                    yield parts
                    parts = []
                # special handling for final newline; splitlines ignores it
                if node.endswith("\n"):
                    if split_string[-1]:
                        parts.append(split_string[-1])
                    yield parts
                    parts = []
                elif split_string[-1]:
                    parts.append(split_string[-1])
            elif node:
                parts.append(node)

    # yield final parts
    if len(parts) > 0:
        yield parts
