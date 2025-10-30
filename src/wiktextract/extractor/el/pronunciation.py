import re
from typing import cast

from wikitextprocessor import NodeKind, TemplateNode, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS  # , print_tree

from wiktextract import WiktextractContext
from wiktextract.clean import clean_value
from wiktextract.page import clean_node

# from wiktextract.wxr_logging import logger
from .models import Sound, WordEntry
from .parse_utils import POSReturns, find_sections
from .section_titles import Heading, POSName
from .tags_utils import convert_tags

TEMPLATES_TO_IGNORE: set[str] = set(
    # Honestly, just ignore everything...
    (
        "ήχος",  # audio files, -> <phonos>
        "ομόηχ",  # consonant??
    )
)

IPA_TEMPLATES: set[str] = set(
    (
        "δφα",  # ->  ΔΦΑ : /ˈci.klos/
    )
)

HYPHEN_TEMPLATES = set(
    (
        "συλλ",  # seems to be hyphenation XXX use hyphenation data
    )
)

HOMOPHONES_TEMPLATES = set(
    (
        "παρών",  # tonal paronym, near-synonym, cognate
        "παρων",
    )
)

IPA_RE = re.compile(r"ΔΦΑ : /([^/]+)/")

HYPHEN_RE = re.compile(r"τυπογραφικός συλλαβισμός : ([^\n]+)(\n|$)")

# HOMOPHONES_RE = re.compile(r"τονικό παρώνυμο[^:]+: ([^\n]+)(\n|$)")

HOMOPHONES_RE = re.compile(r"__HOMOPHONES__(.+)")


# Greek Wiktionary Pronunciation Sections #
# These tend to be super-simple and we might get away with using a
# template handling function that just extracts IPA templates (and others)
# from the content.


def process_pron(
    wxr: WiktextractContext,
    node: WikiNode,
    target_data: WordEntry,
    title: str,
    num: int,  # Section number
) -> tuple[int, POSReturns]:
    """Process a Pronunciation section WikiNode, extracting Sound data entries
    which are inserted into target_data.sounds. target_data is a WordEntry, so
    can be base_data (used to complete other entries) or an individual POS
    entry."""

    # We save data in parse_pronunciation_template_fn into this local list,
    # so the template_fn has to be defined inside this larger function so
    # that it has easy access to sound_templates. Can't be defined outside
    # this function either, because we need access to `wxr` from here, and
    # the template_fn signature is already set in wikitextprocessor.
    sounds: list[Sound] = []
    hyphenations: list[str] = []

    content: list[WikiNode] = []
    sublevels: list[WikiNode] = []

    pos_returns: POSReturns = []

    wxr.wtp.start_subsection(title)

    section_num = num

    for child in node.children:
        if isinstance(child, str):
            # Ignore strings
            continue
        if child.kind in LEVEL_KIND_FLAGS:
            # Stop at first Level; everything before this is 'content',
            # direct children of the parent node, everything after levels
            # start are sublevels.
            sublevels.append(child)
            continue
        content.append(child)

    def pronunciation_node_handler_fn(
        node: WikiNode,
    ) -> list[str | WikiNode] | str | None:
        assert isinstance(node, WikiNode)
        kind = node.kind
        if isinstance(node, TemplateNode):
            # Recursively expand templates so that even nodes inside the
            # the templates are handled with bold_node_handler.
            # Argh. Don't use "node_to_text", that causes bad output...
            tname = node.template_name.lower()
            expanded = wxr.wtp.expand(wxr.wtp.node_to_wikitext(node))
            new_node = wxr.wtp.parse(expanded)
            if tname in IPA_TEMPLATES:
                # print(f"{tname=}")
                if m := IPA_RE.search(clean_node(wxr, None, node)):
                    # print(f"{m=}")
                    sounds.append(Sound(ipa=m.group(1)))
                return []
            elif tname in HYPHEN_TEMPLATES:
                # print(f"{tname=}")
                if m := HYPHEN_RE.search(clean_node(wxr, None, node)):
                    # print(f"{m=}")
                    hyphenations.append(m.group(1))
                return []
            # Ugh, XXX, homophone templates are just a placeholder for the
            # text "homophones", and the actual data is in the text
            elif tname in HOMOPHONES_TEMPLATES:
                return ["__HOMOPHONES__"]
                # if m := HOMOPHONES_RE.search(clean_node(wxr, None, node)):
                #     sounds.append(Sound(homophones=[m.group(1)]))
            ret = wxr.wtp.node_to_text(new_node)
            return ret
        elif kind in {
            NodeKind.TABLE,
        }:
            return [*node.children]
        return None

    for line in wxr.wtp.node_to_text(
        content, node_handler_fn=pronunciation_node_handler_fn
    ).splitlines():
        if line.strip() == "":
            continue
        # Have to handle Homophones here because the homophone template
        # only generates a "homophones follow" message...
        if m := HOMOPHONES_RE.search(line):
            homophones = list(
                clean_value(wxr, s).strip() for s in m.group(1).split(",")
            )
            sounds.append(Sound(homophones=homophones))

    for heading_type, pos, heading_title, tags, num, subnode in find_sections(
        wxr, sublevels
    ):
        section_num = num if num > section_num else section_num

        if heading_type == Heading.POS:
            # SAFETY: Since the heading_type is POS, find_sections
            # "pos_or_section" is guaranteed to be a pos: POSName
            pos = cast(POSName, pos)
            pos_returns.append(
                (
                    pos,
                    heading_title,
                    tags,
                    num,
                    subnode,
                    target_data.model_copy(deep=True),
                )
            )

    # remove duplicate tags
    for st in sounds:
        legit_tags, raw_tags, poses = convert_tags(st.raw_tags)
        if len(legit_tags) > 0:
            st.tags = sorted(set(legit_tags))
            st.raw_tags = sorted(set(raw_tags))
        if len(poses) > 0:
            st.poses.extend(poses)
        st.poses = sorted(set(st.poses))

    if len(sounds) > 0:
        # completely replace sound data with new
        target_data.sounds = sounds
    else:
        target_data.sounds = []
    if len(hyphenations) > 0:
        target_data.hyphenation += ", ".join(hyphenations)
    else:
        target_data.hyphenation = ""

    # print(f"{sounds=}, {hyphenations=}, {target_data=}")
    return section_num, pos_returns
