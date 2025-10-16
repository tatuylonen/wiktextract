import re
from collections.abc import Iterator
from functools import partial
from typing import TypeAlias
from unicodedata import name as unicode_name

from wikitextprocessor import (
    HTMLNode,
    NodeKind,
    TemplateArgs,
    TemplateNode,
    WikiNode,
)
from wikitextprocessor.parser import LEVEL_KIND_FLAGS

from wiktextract import WiktextractContext
from wiktextract.extractor.el.tags import translate_raw_tags
from wiktextract.page import clean_node
from wiktextract.wxr_logging import logger

from .head import parse_head
from .linkages import process_linkage_section
from .models import Example, FormOf, Linkage, Sense, TemplateData, WordEntry
from .parse_utils import (
    GREEK_LANGCODES,
    Heading,
    parse_lower_heading,
    remove_duplicate_forms,
)
from .section_titles import POS_HEADINGS
from .table import parse_table, process_inflection_section
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
            and (line[0].sarg != ":")
        ):
            if glosses_index is None:
                glosses_index = i
            glosses_lists.append(line[0])

    if glosses_index is None:
        # if nothing found, accept ":" nodes
        for i, line in enumerate(node_lines):
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
        data.tags.append("no-gloss")

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
    ) -> list[str | WikiNode] | str | None:
        """Insert special markers `__*S__` and `__*E__` around bold nodes so
        that the strings can later be split into "head-word" and "tag-words"
        parts. Collect incidental stuff, like side-tables, that are often
        put around the head."""
        assert isinstance(node, WikiNode)
        kind = node.kind
        nonlocal template_depth
        nonlocal top_template_name
        if kind == NodeKind.BOLD or (
            isinstance(node, HTMLNode)
            and (
                node.tag == "span"
                and "style" in node.attrs
                and (
                    "bold" in node.attrs["style"]
                    # Special handling for output for stuff in arabic script
                    or node.attrs["style"] == "color:black; font-size:200%;"
                )
                or node.tag == "b"
                or node.tag == "strong"
            )
        ):
            # These are word forms almost always
            return ["__B__", *node.children, "__/B__"]
        elif kind == NodeKind.ITALIC or (
            isinstance(node, HTMLNode)
            and (
                (
                    node.tag == "span"
                    and "style" in node.attrs
                    and "italic" in node.attrs["style"]
                )
                or node.tag == "i"
                or node.tag == "em"
            )
        ):
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
            # Special case for meta-links like Πρότυπο:ετ that generate
            # both a category link and :category link that is actually
            # displayed as a link, but for our purposes we want to ignore
            # that it is a link; it's a tag.
            if node.largs[0][0].startswith(":Κατηγορία:"):
                # unpacking a list-comprehension, unpacking into a list
                # seems to be more performant than adding lists together.
                return [
                    wxr.wtp.node_to_text(
                        node.largs[1:2] or node.largs[0],
                        node_handler_fn=bold_node_handler_fn,
                    )
                    # output the "visible" half of the link.
                ]
            if node.largs[0][0].startswith("Αρχείο:"):
                return [""]
            # Often forms are 'formatted' with links, so let's mark these
            # too.
            return [
                "__L__",
                wxr.wtp.node_to_text(
                    node.largs[1:2] or node.largs[0],
                    node_handler_fn=bold_node_handler_fn,
                ),
                # output the "visible" half of the link.
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
        stripped = (
            wxr.wtp.node_to_text(line, node_handler_fn=bold_node_handler_fn)
            .removeprefix(":")
            .strip()
        )
        if not stripped:
            continue
        if not found_head and (parsed_forms := parse_head(wxr, stripped)):
            for form in parsed_forms:
                translate_raw_tags(form)
            data.forms.extend(parsed_forms)
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
                source="inflection",
            )
            for form in data.forms:
                translate_raw_tags(form)

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
            for sense in senses:
                translate_raw_tags(sense)
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
        subtitle = clean_node(wxr, None, sl.largs).lower().strip()

        type, pos, heading_name, tags, num, ok = parse_lower_heading(
            wxr, subtitle
        )

        if type == Heading.Translations:
            process_translations(wxr, data, sl)
        elif type == Heading.Infl:
            source = "inflection"
            if data.lang_code in ("el", "grc"):
                source = "conjugation"
            process_inflection_section(wxr, data, sl, source=source)
        elif type in (
            Heading.Related,
            Heading.Synonyms,
            Heading.Antonyms,
            Heading.Transliterations,
        ):
            process_linkage_section(wxr, data, sl, type)
    #     if type not in (
    #         Heading.Translations,
    #         Heading.Ignored,
    #         Heading.Infl,
    #         Heading.Related,
    #         Heading.Synonyms,
    #         Heading.Antonyms,
    #         Heading.Derived,
    #         # We're going to ignore homonyms because they're
    #         # only tangentially related, like anagrams
    #         Heading.Homonyms,
    #     ):
    #         # ...
    #         expanded = wxr.wtp.expand(wxr.wtp.node_to_wikitext(sl))
    #         # text = clean_node(wxr, None, sl)
    #         logger.warning(
    #             f"""
    # {wxr.wtp.title}: {type}, '{heading_name}', {ok=}
    # {expanded}

    # ###########################
    # """
    #         )

    #####
    #####
    return data


PARENS_BEFORE_RE = re.compile(r"\s*(\([^()]+\)\s*)+")
ITER_PARENS_RE = re.compile(r"\(([^()]+)\)")


def bold_node_fn(
    node: WikiNode,
) -> list[str | WikiNode] | None:
    """Handle nodes in the parse tree specially."""
    # print(f"{node=}")
    if node.kind == NodeKind.ITALIC:
        return ["__I__", *node.children, "__/I__"]
    if node.kind == NodeKind.BOLD:
        return ["__B__", *node.children, "__/B__"]
    # if node.kind == NodeKind.LINK:
    #     if not isinstance(node.largs[0][0], str):
    #         return None
    #     return [
    #         "__L__",
    #         # unpacking a list-comprehension, unpacking into a list
    #         # seems to be more performant than adding lists together.
    #         *(
    #             wxr.wtp.node_to_text(
    #                 node.largs[1:2] or node.largs[0],
    #             )
    #             # output the "visible" half of the link.
    #         ),
    #         # XXX collect link data if it turns out to be important.
    #         "__/L__",
    #     ]
    #     # print(f"{node.largs=}")
    return None


def extract_form_of_templates(
    wxr: WiktextractContext,
    parent_sense: Sense | WordEntry,
    t_node: TemplateNode,
    siblings: list[str | WikiNode],
    siblings_index: int,
) -> None:
    """Parse form_of for nouns, adjectives and verbs.

    Supports:
    * κλ             | generic                | form_of
    * γρ             | generic                | form_of
    * πτώση/πτώσεις  | nouns, adjectives etc. | form_of and tags
    * ρημ τύπος      | verbs                  | form_of
    * μτχ            | verbs                  | form_of

    * References:
    https://el.wiktionary.org/wiki/Πρότυπο:κλ
    https://el.wiktionary.org/wiki/Module:άλλημορφή
    https://el.wiktionary.org/wiki/Κατηγορία:Πρότυπα_για_κλιτικούς_τύπους
    https://el.wiktionary.org/wiki/Πρότυπο:ρημ_τύπος
    https://el.wiktionary.org/wiki/Κατηγορία:Πρότυπα_για_μετοχές
    """
    t_name = t_node.template_name

    basic_extract = partial(
        extract_form_of_templates_basic,
        wxr,
        parent_sense,
        siblings,
        siblings_index,
        t_name,
        t_node,
    )
    # Generic
    if t_name == "κλ":
        return basic_extract(extract_argument=2)

    # Notes:
    # * All occurrences in wiktionary have at least one argument
    # * Only handle cases where the second argument refers to a form:
    #   μορφ / μορφή / λόγια μορφή του, etc.
    #   and ignore those mistakenly used as synonym templates
    if t_name == "γρ" and 2 in t_node.template_parameters:
        second_arg = t_node.template_parameters[2]
        second_arg_str = clean_node(wxr, None, second_arg)
        if "μορφ" in second_arg_str:
            return basic_extract(extract_argument=1)

    # Nouns and adjectives
    inflection_t_names = ("πτώσεις", "πτώση")
    if any(name in t_name for name in inflection_t_names):
        return extract_form_of_templates_ptosi(wxr, parent_sense, t_node)

    # Verbs
    if t_name == "ρημ τύπος":
        return basic_extract(extract_argument=2)

    if t_name.startswith("μτχ"):
        return basic_extract(extract_argument=1)


def extract_form_of_templates_basic(
    wxr: WiktextractContext,
    parent_sense: Sense | WordEntry,
    siblings: list[str | WikiNode],
    sibling_index: int,
    t_name: str,
    t_node: TemplateNode,
    extract_argument: int | str,
):
    t_args = t_node.template_parameters
    if extract_argument not in t_args:
        # mtxpp template has no args, consume the next links for the
        # form_of field
        wxr.wtp.warning(
            f"Form-of template does not have lemma data: {t_name}, {t_args=}",
            sortid="pos/570/20250517",
        )
        links: list[str | WikiNode] = []
        for node in siblings[sibling_index + 1 :]:
            if not (
                (isinstance(node, str) and node.strip() == "")
                or (isinstance(node, WikiNode) and node.kind == NodeKind.LINK)
            ):
                break
            links.append(node)
        lemma = clean_node(wxr, None, links).strip()
    else:
        lemma = clean_node(wxr, None, t_args[extract_argument]).strip()

    if lemma:
        form_of = FormOf(word=lemma)
        parent_sense.form_of.append(form_of)
    else:
        wxr.wtp.warning(
            "Lemma extract from form-of template was empty or whitespace:"
            f"{t_name}, {t_args=}, {lemma=}",
            sortid="pos/609/20250925",
        )


def extract_form_of_templates_ptosi(
    wxr: WiktextractContext,
    parent_sense: Sense | WordEntry,
    t_node: TemplateNode,
) -> None:
    """Parse form_of for nouns and adjectives.

    Supports:
    * [gender του] πτώση-πτώσεις templates

    Notes:
    * πτώση has exactly one case, πτώσεις as at least two cases
    """
    t_name = t_node.template_name
    inflection_t_names = ("πτώσεις", "πτώση")
    tags: list[str] = []

    # Parse and consume gender if any
    if "-" in t_name:
        # Cf. {{ουδ του-πτώσειςΟΑΚεν|καλός|grc}}
        gender, inflection = t_name.split("-")
        code = gender[:3]
        GENDER_INFLECTION_MAP = {
            "θηλ": "feminine",
            "αρσ": "masculine",
            "ουδ": "neuter",
        }
        try:
            gender_tag = GENDER_INFLECTION_MAP[code]
        except KeyError:
            # Bad template name.
            return
        tags.append(gender_tag)
    else:
        inflection = t_name

    # Remove πτώση-πτώσεις prefix
    for prefix in inflection_t_names:
        if inflection.startswith(prefix):
            inflection = inflection[len(prefix) :]
            break

    PTOSI_INFLECTION_MAP = {
        "Ο": "nominative",
        "Α": "accusative",
        "Γ": "genitive",
        "Κ": "vocative",
    }

    # The πτώση-πτώσεις templates contains:
    # * Case(s) (1 for πτώση, >1 for πτώσεις) in uppercase characters.
    # * Number in either "εν" (singular) or "πλ" (plural)
    #
    # Examples:
    # * {{πτώσηΑεν|κόρφος}}    > accusative           | singular
    # * {{πτώσειςΟΚπλ|κόρφος}} > nominative, vocative | plural
    try:
        lowercase = "".join(ch for ch in inflection if ch.islower())
        number = {"εν": "singular", "πλ": "plural"}[lowercase]
        uppercase = [ch for ch in inflection if not ch.islower()]
        cases = [PTOSI_INFLECTION_MAP[ch] for ch in uppercase]
    except KeyError:
        # Bad template name.
        return

    tags.extend([elt for elt in cases + [number]])

    t_args = t_node.template_parameters

    if 1 not in t_args:
        wxr.wtp.warning(
            f"Form-of template does not have lemma data: {t_name}, {t_args=}",
            sortid="pos/620/20250416",
        )
        return

    lemma = clean_node(wxr, None, t_args[1])
    form_of = FormOf(word=lemma)
    parent_sense.form_of.append(form_of)
    tags.sort()  # For the tests, but also good practice
    parent_sense.tags.extend(tags)


def parse_gloss(
    wxr: WiktextractContext, parent_sense: Sense, contents: list[str | WikiNode]
) -> bool:
    """Take what is preferably a line of text and extract tags and a gloss from
    it. The data is inserted into parent_sense, and for recursion purposes
    we return a boolean that tells whether there was any gloss text in a
    lower node."""
    if len(contents) == 0:
        return False

    for i, t_node in enumerate(contents):
        if isinstance(t_node, TemplateNode):
            extract_form_of_templates(wxr, parent_sense, t_node, contents, i)

    template_tags: list[str] = []

    bl_linkages: list[Linkage] = []
    no_gloss_but_keep_anyway = False

    def bl_template_handler_fn(name: str, ht: TemplateArgs) -> str | None:
        nonlocal bl_linkages
        if name == "βλ":
            for k, v in ht.items():
                if isinstance(k, int):
                    bl_linkages.append(Linkage(word=clean_node(wxr, None, v)))
            return ""
        return None

    # The rest of the text.
    text = clean_node(
        wxr,
        parent_sense,
        contents,
        template_fn=bl_template_handler_fn,
        node_handler_fn=bold_node_fn,
    )

    if len(bl_linkages) > 0:
        parent_sense.related.extend(bl_linkages)
        no_gloss_but_keep_anyway = True

    if not text.strip():
        if len(bl_linkages) <= 0:
            return False

    # print(f"   ============  {contents=}, {text=}")

    # Greek Wiktionary uses a lot of template-less tags.
    if parens_n := PARENS_BEFORE_RE.match(text):
        blocks = ITER_PARENS_RE.findall(parens_n.group(0))
        # print(f"{blocks=}")
        kept_blocks: list[str] = []
        forms: list[str] = []
        raw_tag_texts: list[str] = []
        for block in blocks:
            if block_has_non_greek_text(block):
                # Keep parentheses with non-greek text with gloss text)
                kept_blocks.extend(("(", block, ") "))
                continue
            nforms, nraw_tag_texts = extract_forms_and_tags(block)
            forms.extend(nforms)
            raw_tag_texts.extend(nraw_tag_texts)
        # print(f"{forms=}, {raw_tag_texts=}")
        if forms:
            # print(f"{forms=}")
            parent_sense.related.extend(Linkage(word=form) for form in forms)
        parent_sense.raw_tags.extend(raw_tag_texts)
        kept_blocks.append(text[parens_n.end() :])
        text = "".join(kept_blocks)

    text = re.sub(r"__/?[IB]__", "", text)

    if len(template_tags) > 0:
        parent_sense.raw_tags.extend(template_tags)

    if len(text) > 0:
        parent_sense.glosses.append(text)
        return True

    if no_gloss_but_keep_anyway:
        parent_sense.raw_tags.append("no-gloss")
        return True

    return False


Related: TypeAlias = Linkage
Synonym: TypeAlias = Linkage
Antonym: TypeAlias = Linkage


def recurse_glosses1(
    wxr: WiktextractContext,
    parent_sense: Sense,
    node: WikiNode,
) -> tuple[
    list[Sense],
    list[Example],
    list[Related],
    list[Synonym],
    list[Antonym],
]:
    """Helper function for recurse_glosses"""
    # print(f"{node=}")

    ret_senses: list[Sense] = []
    ret_examples: list[Example] = []
    ret_related: list[Related] = []
    ret_synonyms: list[Synonym] = []
    ret_antonyms: list[Antonym] = []
    found_gloss = False

    # Pydantic stuff doesn't play nice with Tatu's manual dict manipulation
    # functions, so we'll use a dummy dict here that we then check for
    # content and apply to `parent_sense`.
    dummy_parent: dict = {}

    related_linkages: list[Linkage] = []
    example_is_synonym = False
    example_is_antonym = False

    def bl_template_handler_fn(name: str, ht: TemplateArgs) -> str | None:
        nonlocal related_linkages
        nonlocal example_is_synonym
        nonlocal example_is_antonym
        # Sometimes the bl-templates point to synonyms or antonyms, instead
        # of just "related"; we save them, and if example_is_xxxnym is true,
        # we later return them as xxxnyms.
        if name == "βλ":
            for k, v in ht.items():
                if isinstance(k, int):
                    related_linkages.append(
                        Linkage(word=clean_node(wxr, None, v))
                    )
            return ""
        if name == "συνων":
            example_is_synonym = True
            return ""
        if name == "αντων":
            example_is_antonym = True
            return ""
        return None

    # List nodes contain only LIST_ITEM nodes, which may contain sub-LIST nodes.
    if node.kind == NodeKind.LIST:
        list_ret: tuple[
            list[Sense],
            list[Example],
            list[Related],
            list[Synonym],
            list[Antonym],
        ] = ([], [], [], [], [])
        for child in node.children:
            if isinstance(child, str) or child.kind != NodeKind.LIST_ITEM:
                # This should never happen
                wxr.wtp.error(
                    f"{child=} is direct child of NodeKind.LIST",
                    sortid="simple/pos/44",
                )
                continue
            (
                senses,
                examples,
                related,
                synonyms,
                antonyms,
            ) = recurse_glosses1(wxr, parent_sense.model_copy(deep=True), child)
            list_ret[0].extend(senses)
            list_ret[1].extend(examples)
            list_ret[2].extend(related)
            list_ret[3].extend(synonyms)
            list_ret[4].extend(antonyms)
        return list_ret

    elif node.kind == NodeKind.LIST_ITEM:
        # Split at first LIST node found
        split_at = next(
            (
                i
                for i, c in enumerate(node.children)
                if isinstance(c, WikiNode) and c.kind == NodeKind.LIST
            ),
            len(node.children),
        )
        contents = node.children[:split_at]
        sublists = node.children[split_at:]

        # A LIST and LIST_ITEM `sarg` is basically the prefix of the line, like
        # `#` or `##:`: the token that appears at the very start of a line that
        # is used to parse the depth and structure of lists.
        # `#` Item 1
        # `##` Item 1.1
        # `##*` Example 1.1
        if node.sarg.endswith((":", "*")) and node.sarg not in (":", "*"):
            # This is either a quotation or example.
            text = clean_node(
                wxr, dummy_parent, contents, template_fn=bl_template_handler_fn
            ).strip("⮡ \n")

            # print(f"{contents=}, {text=}, {related_linkages=}")

            if example_is_synonym or example_is_antonym:
                link_linkages = []
                for snode in contents:
                    if not isinstance(snode, WikiNode):
                        continue
                    if snode.kind == NodeKind.LINK:
                        link_linkages.append(
                            Linkage(
                                word=clean_node(wxr, None, snode.largs[0][0])
                            )
                        )
                    else:
                        for link in snode.find_child_recursively(NodeKind.LINK):
                            link_linkages.append(
                                Linkage(word=clean_node(wxr, None, link))
                            )

                # print("=====")
                # print(f"{link_linkages=}")

                if example_is_synonym:
                    return [], [], [], link_linkages + related_linkages, []
                elif example_is_antonym:
                    return [], [], [], [], link_linkages + related_linkages

            if len(related_linkages) > 0:
                # parent_sense.related.extend(bl_linkages)
                # related_linkages = []
                # if not text.strip():
                return [], [], related_linkages, [], []

            example_is_synonym = False
            example_is_antonym = False

            if not text.strip():
                return [], [], [], [], []

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

            return [], [example], [], [], []

        found_gloss = parse_gloss(wxr, parent_sense, contents)

        for sl in sublists:
            if not (isinstance(sl, WikiNode) and sl.kind == NodeKind.LIST):
                # Should not happen
                wxr.wtp.error(
                    f"Sublist is not NodeKind.LIST: {sublists=!r}",
                    sortid="simple/pos/82",
                )
                continue
            (
                senses,
                examples,
                related,
                synonyms,
                antonyms,
            ) = recurse_glosses1(wxr, parent_sense.model_copy(deep=True), sl)
            ret_senses.extend(senses)
            ret_examples.extend(examples)
            ret_related.extend(related)
            ret_synonyms.extend(synonyms)
            ret_antonyms.extend(antonyms)
    if len(ret_senses) > 0:
        # the recursion returned actual senses from below, so we will
        # ignore everything else (incl. any example data that might have
        # been given to parent_sense) and return that instead.
        # XXX if this becomes relevant, add the example data to a returned
        # subsense instead?
        # if any(
        #     isinstance(r, Sense) and r.raw_tags == ["no-gloss"] for r in ret
        # ):
        #     print(f"{ret=}")
        return (
            combine_senses_with_identical_glosses(ret_senses),
            [],
            [],
            [],
            [],
        )

    # If nothing came from below, then this.
    if found_gloss is True or "no-gloss" in parent_sense.raw_tags:
        parent_sense.examples.extend(ret_examples)
        parent_sense.related.extend(ret_related)
        parent_sense.synonyms.extend(ret_synonyms)
        parent_sense.antonyms.extend(ret_antonyms)

        return [parent_sense], [], [], [], []

    return [], ret_examples, ret_related, ret_synonyms, ret_antonyms


def recurse_glosses(
    wxr: WiktextractContext, node: WikiNode, data: WordEntry
) -> list[Sense]:
    """Recurse through WikiNodes to find glosses and sense-related data."""
    base_sense = Sense()
    ret: list[Sense] = []

    senses, examples, related, synonyms, antonyms = recurse_glosses1(
        wxr, base_sense, node
    )
    if (
        len(examples) > 0
        or len(related) > 0
        or len(synonyms) > 0
        or len(antonyms) > 0
    ):
        wxr.wtp.error(
            "NOT Sense has bubbled to recurse_glosses: "
            f"{examples=}, {related=}, {synonyms=}, {antonyms=}",
            sortid="pos/glosses/966",
        )
    for sense in senses:
        convert_tags_in_sense(sense)
        ret.append(sense)

    return ret


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


BOLD_RE = re.compile(r"(__/?[BI]__|, |\. )")


def extract_forms_and_tags(tagged_text: str) -> tuple[list[str], list[str]]:
    forms: list[str] = []
    tags: list[str] = []

    # print(f"{tagged_text=}")
    # inside_italics = False
    inside_bold = False

    for i, t in enumerate(BOLD_RE.split(tagged_text)):
        t = t.strip()
        # print(f"{i}: {t=}")
        if not t:
            continue

        if i % 2 == 0:
            # Text between splitters
            if inside_bold is True:
                forms.append(t)
                continue
            # Add everything else to raw_tags
            # if inside_italics is True:
            #     tags.append(t)
            #     continue
            # ". " and ", " just split. They're stripped to "." and "," if
            # this needs to be modified later.
            tags.append(t)
            continue
        match t:
            case "__B__":
                inside_bold = True
            case "__/B__":
                inside_bold = False
            # case "__I__":
            #     inside_italics = True
            # case "__/I__":
            #     inside_italics = False

    return forms, tags


META_RE = re.compile(r"__/?[ILEB]__")


def block_has_non_greek_text(text: str) -> bool:
    text = META_RE.sub("", text)
    for t in text.split():
        for ch in t:
            if not ch.isalpha():
                continue
            if not unicode_name(ch).startswith("GREEK"):
                return True
            break
    return False


def combine_senses_with_identical_glosses(
    orig_senses: list[Sense],
) -> list[Sense]:
    glosses_to_senses: dict[tuple[str, ...], list[Sense]] = {}
    senses: list[Sense] = []

    found_identical_glosses = False

    for item in orig_senses:
        glosses_key = tuple(item.glosses)
        if glosses_key not in glosses_to_senses:
            glosses_to_senses[glosses_key] = [item]
        else:
            glosses_to_senses[glosses_key].append(item)
            found_identical_glosses = True

    if not found_identical_glosses:
        return orig_senses

    for twinned_senses in glosses_to_senses.values():
        main_sense = twinned_senses[0]
        for other_sense in twinned_senses[1:]:
            main_sense.merge(other_sense)
        senses.append(main_sense)

    return senses
