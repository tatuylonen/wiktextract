# Code related to parsing linkages (synonyms, hypernyms, related terms, etc)
#
# Copyright (c) 2019-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import unicodedata
from typing import Optional, Sequence

from wikitextprocessor import (
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)
from wikitextprocessor.core import TemplateArgs
from wikitextprocessor.parser import (
    HTMLNode,
    is_list,
    is_list_item,
)

from ...datautils import (
    data_append,
    data_extend,
    ns_title_prefix_tuple,
    split_at_comma_semi,
)
from ...page import clean_node, is_panel_template
from ...tags import linkage_beginning_tags, valid_tags
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby, parse_ruby  # noqa: F401
from .form_descriptions import (
    classify_desc,
    decode_tags,
    head_final_bantu_langs,
    head_final_bantu_re,
    head_final_numeric_langs,
    head_final_other_langs,
    head_final_other_re,
    head_final_re,
    parse_head_final_tags,
    parse_sense_qualifier,
)
from .section_titles import TRANSLATIONS_TITLE
from .type_utils import FormData, LinkageData, SenseData, WordData

# Linkage will be ignored if it matches this regexp before splitting
linkage_pre_split_ignore_re = re.compile(
    r"^("
    + "|".join(
        re.escape(x)
        for x in [
            "For more variations, see ",
            "Signal flag:",
            "Semaphore:",
        ]
    )
    + r")"
)

# Linkage will be ignored if it has one of these prefixes
linkage_ignore_prefixes = [
    "Historical and regional synonyms of ",
    "edit data",
    "or these other third-person pronouns",
    "introduced in Unicode ",
    "Entries in the ",
    "Wikipedia article ",
    "Wiktionary's coverage of ",
    "Ethnologue entry for ",
    "Any of Thesaurus:",
    "See contents of Category:",
    "See also Thesaurus:",
    "See also Appendix:",
    "As SMS messaging ",
    "For the reversed question mark used in some right-to-left-scripts",
    "such as ",
    "Appendix:",
    "Category:",
    ":Category:",
]

# Linkage will be ignored if it has any of these suffixes
linkage_ignore_suffixes = [
    " Wikipedia",
    " Wikipedia.",
    " edition of Wiktionary",
]

# Linkage will be ignored if it is one of these (with full match)
linkage_ignore_whole = [
    "etc.",
    "other derived terms:",
    "Formal terms",
    "informal and slang terms",
]

# Linkage will be ignored if it matches this regexp
linkage_ignore_re = re.compile(
    r"^("
    + "|".join(re.escape(x) for x in linkage_ignore_whole)
    + r")$|^("
    + "|".join(re.escape(x) for x in linkage_ignore_prefixes)
    + r")|("
    + "|".join(re.escape(x) for x in linkage_ignore_suffixes)
    + r")$"
)

# These prefixes will be removed from linkages, leaving the rest.  This is
# considered separately for each linkage in a list.
linkage_remove_prefixes_re = re.compile(
    r"^("
    + r"|".join(
        re.escape(x)
        for x in [
            ":",
            "see Thesaurus:",
            "See Thesaurus:",
            "see also Thesaurus:",
            "See also Thesaurus:",
            "see also ",
            "See also ",
            "see ",
            "See ",
            "from ",
            "abbreviation of ",
            "ISO 639-1 code ",
            "ISO 639-3 code ",
            "Thesaurus:",
        ]
    )
    + ")"
)

# When removing prefix from linkage, this dictionary can be used to map
# the removed prefix to a space-separated list of tags to add
linkage_remove_prefixes_tags = {
    "abbreviation of ": "abbreviation",
}

# These suffixes will be removed from linkages, leaving the rest.  This is
# considered separately for each linkage in a list.
linkage_remove_suffixes_re = re.compile(
    r"(\s+on (Wikispecies|Wikimedia Commons|"
    r"[A-Z]\w+ Wiktionary|[A-Z]\w+ Wikipedia)\.?|"
    r"\s*[-–] Pre-reform orthography.*)"
    r"$"
)

# Ignore linkage parenthesized sections that contain one of these strings
linkage_paren_ignore_contains_re = re.compile(
    r"\b("
    + "|".join(
        re.escape(x)
        for x in [
            "from Etymology",
            "used as",
            "usage notes",
        ]
    )
    + ")([, ]|$)"
)

taxonomic_ending_map = {
    "superkingdoms": "superkingdom",
    "kingdoms": "kingdom",
    "subkingdoms": "subkingdom",
    "infrakingdoms": "infrakingdom",
    "phylums": "phylum",
    "subphylums": "subphylum",
    "infraphylums": "infraphylum",
    "superclasses": "superclass",
    "classes": "class",
    "orders": "order",
    "suborders": "suborder",
    "families": "family",
    "subfamilies": "subfamily",
    "genera": "genus",
}
for k, v in list(taxonomic_ending_map.items()):
    taxonomic_ending_map[v] = v  # Also add singular -> singular
taxonomic_ending_re = re.compile(
    r"\s+[-‐‑‒–—]\s+({})$".format(
        "|".join(re.escape(x) for x in taxonomic_ending_map)
    )
)

# Exceptional splits for linkages.  This can be used to fix particular linkages
# that are not handled correctly by the default code.  This can also be used
# to create automatic aliases, e.g., for mapping "..." and "…" to both.
linkage_split_exceptions = {
    "∛ ∜": ["∛", "∜"],
    "...": ["...", "…"],
    "…": ["...", "…"],
}

# Truncate linkage word if it matches any of these strings
linkage_truncate_re = re.compile(
    "|".join(
        re.escape(x)
        for x in [
            " and its derived terms",
            " UTF-16 0x214C",
        ]
    )
)

# Regexp for identifying special linkages containing lists of letters, digits,
# or characters
script_chars_re = re.compile(
    r"(script letters| script| letters|"
    r"Dialectological|Puctuation|Symbols|"
    r"Guillemets|Single guillemets|"
    r" tetragrams|"
    r" digits)(;|$)|"
    r"(^|; )(Letters using |Letters of the |"
    r"Variations of letter )|"
    r"^(Hiragana|Katakana)$"
)

# Matches an unicode character including any combining diacritics (even if
# separate characters)
unicode_dc_re = re.compile(
    r"\w[{}]|.".format(
        "".join(
            chr(x)
            for x in range(0, 0x110000)
            if unicodedata.category(chr(x)) == "Mn"
        )
    )
)


def extract_alt_form_section(
    wxr: WiktextractContext, word_entry: WordData, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.children:
                if isinstance(node, TemplateNode) and node.template_name in [
                    "l",
                    "link",
                    "L",
                    "alt",
                    "alter",
                ]:
                    extract_l_template(wxr, word_entry, node)
                elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "":
                        form: FormData = {"form": word, "tags": ["alternative"]}
                        data_append(word_entry, "forms", form)


def extract_l_template(
    wxr: WiktextractContext, word_entry: WordData, t_node: TemplateNode
) -> None:
    forms: list[FormData] = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "")
        if span_lang == lang_code:
            word = clean_node(wxr, None, span_tag)
            if word != "":
                form: FormData = {"form": word, "tags": ["alternative"]}
                forms.append(form)
        elif span_lang.endswith("-Latn") and len(forms) > 0:
            roman = clean_node(wxr, None, span_tag)
            if roman != "":
                forms[-1]["roman"] = roman
        elif "label-content" in span_class and len(forms) > 0:
            tag_text = clean_node(wxr, None, span_tag)
            if classify_desc(tag_text) == "tags":
                tagsets1, _ = decode_tags(tag_text)
                tags: list[str] = []
                for ts in tagsets1:
                    tags.extend(ts)
                for form in forms:
                    form["tags"].extend(tags)
    data_extend(word_entry, "forms", forms)


ZH_DIAL_TAGS = {
    "Classical Chinese": ["Classical-Chinese"],
    "Formal": ["formal"],
    "Written Standard Chinese": ["Written-vernacular-Chinese"],
    "Northeastern Mandarin": ["Northeastern-Mandarin"],
    "Jilu Mandarin": ["Jilu-Mandarin"],
    "Jiaoliao Mandarin": ["Jiaoliao-Mandarin"],
    "Central Plains Mandarin": ["Central-Plains-Mandarin"],
    "Lanyin Mandarin": ["Lanyin-Mandarin"],
    "Southwestern Mandarin": ["Southwestern-Mandarin"],
    "Jianghuai Mandarin": ["Jianghuai-Mandarin"],
    "Northern Min": ["Min-Bei"],
    "Eastern Min": ["Min-Dong"],
    "Southern Min": ["Min-Nan"],
    "Zhongshan Min": ["Zhongshan-Min"],
    "Southern Pinghua": ["Southern-Pinghua"],
    "Puxian Min": ["Puxian-Min"],
}


def extract_zh_dial_template(
    wxr: WiktextractContext,
    word_entry: WordData,
    t_node: TemplateNode,
    sense: str,
):
    # https://en.wiktionary.org/wiki/Template:zh-dial
    from .pronunciation import split_zh_pron_raw_tag

    linkage_list: list[LinkageData] = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table_node in expanded_node.find_child_recursively(NodeKind.TABLE):
        is_note_row = False
        note_tags = {}
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            for cell_node in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    is_note_row = clean_node(wxr, None, cell_node) == "Note"
                elif is_note_row:
                    for note_str in clean_node(wxr, None, cell_node).split(";"):
                        if "-" in note_str:
                            note_symbol, note = note_str.split("-", maxsplit=1)
                            note_symbol = note_symbol.strip()
                            note = note.strip()
                            if note_symbol != "" and note != "":
                                note_tags[note_symbol] = note
        lang_tags = []
        region_tags = []
        for row_node in table_node.find_child(NodeKind.TABLE_ROW):
            if not row_node.contain_node(NodeKind.TABLE_CELL):
                continue  # skip header row
            for header_node in row_node.find_child(NodeKind.TABLE_HEADER_CELL):
                lang_tags = split_zh_pron_raw_tag(
                    clean_node(wxr, None, header_node)
                )
            if lang_tags == ["Note"]:  # skip last note row
                continue
            for cell_node in row_node.find_child(NodeKind.TABLE_CELL):
                for link_node in cell_node.find_child(NodeKind.LINK):
                    region_tags = split_zh_pron_raw_tag(
                        clean_node(wxr, None, link_node)
                    )
                for span_tag in cell_node.find_html("span"):
                    span_text = clean_node(wxr, None, span_tag)
                    if span_text == "":
                        continue
                    if (
                        span_tag.attrs.get("lang", "") == "zh"
                        and span_text != wxr.wtp.title
                    ):
                        l_data: LinkageData = {"word": span_text}
                        if sense != "":
                            l_data["sense"] = sense
                        if len(lang_tags) > 0:
                            data_extend(l_data, "raw_tags", lang_tags)
                        if len(region_tags) > 0:
                            data_extend(l_data, "raw_tags", region_tags)
                        linkage_list.append(l_data)
                    elif (
                        span_tag.attrs.get("style", "") == "font-size:60%"
                        and len(linkage_list) > 0
                    ):
                        for note_symbol in span_text.split(","):
                            note_symbol = note_symbol.strip()
                            raw_tag = note_symbol
                            if note_symbol in note_tags:
                                raw_tag = note_tags[note_symbol]
                            if raw_tag != "":
                                data_append(
                                    linkage_list[-1], "raw_tags", raw_tag
                                )

        for l_data in linkage_list:
            raw_tags = []
            for raw_tag in l_data.get("raw_tags", []):
                if raw_tag in ZH_DIAL_TAGS:
                    data_extend(l_data, "tags", ZH_DIAL_TAGS[raw_tag])
                elif raw_tag in valid_tags:
                    data_append(l_data, "tags", raw_tag)
                else:
                    raw_tags.append(raw_tag)
            if len(raw_tags) > 0:
                l_data["raw_tags"] = raw_tags
            elif "raw_tags" in l_data:
                del l_data["raw_tags"]
        data_extend(word_entry, "synonyms", linkage_list)


def parse_linkage(
    wxr: WiktextractContext,
    data: WordData,
    field: str,
    linkagenode: LevelNode,
    word: str,
    sense_datas: list[SenseData],
    is_reconstruction: bool,
) -> None:
    assert isinstance(data, dict)
    assert isinstance(field, str)
    assert isinstance(linkagenode, LevelNode)
    # print("field", field)
    # print("data", data)
    # print("children:")
    if not wxr.config.capture_linkages:
        return
    have_panel_template = False

    def linkage_template_fn1(name: str, ht: TemplateArgs) -> Optional[str]:
        nonlocal have_panel_template
        if is_panel_template(wxr, name):
            have_panel_template = True
            return ""
        return None

    # Main body of parse_linkage()
    l_nodes: list[str | WikiNode] = []
    l_sense = ""
    for node in linkagenode.children:
        if isinstance(node, TemplateNode) and node.template_name == "zh-dial":
            extract_zh_dial_template(wxr, data, node, l_sense)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                for t_node in list_item.find_child(NodeKind.TEMPLATE):
                    if t_node.template_name in ["s", "sense"]:
                        l_sense = clean_node(wxr, None, t_node).strip("(): ")
            l_nodes.append(node)
        else:
            l_nodes.append(node)
    text = wxr.wtp.node_to_wikitext(l_nodes)
    parsed = wxr.wtp.parse(
        text, expand_all=True, template_fn=linkage_template_fn1
    )

    text_outside_list_items = parse_linkage_recurse(
        wxr,
        parsed.children,
        field,
        None,
        None,
        word,
        data,
        sense_datas,
        is_reconstruction,
    )

    if not data.get(field) and not have_panel_template:
        text = "".join(text_outside_list_items).strip()
        if "\n" not in text and "," in text and text.count(",") > 3:
            if not text.startswith("See "):
                parse_linkage_item(
                    wxr,
                    [text],
                    field,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                    None,
                )


def parse_linkage_recurse(
    wxr: WiktextractContext,
    contents: list[WikiNode | str],
    field: str,
    sense: str | None,
    block_header_sense: str | None,
    word: str,
    data,
    sense_datas,
    is_reconstruction,
) -> list[str]:
    assert isinstance(contents, (list, tuple))
    assert sense is None or isinstance(sense, str)
    # print("PARSE_LINKAGE_RECURSE: {}: {}".format(sense, contents))

    # Return values
    text_outside_list_items: list[str] = []

    for node in contents:
        if isinstance(node, str):
            # Ignore top-level text, generally comments before the
            # linkages list.  However, if no linkages are found, then
            # use this for linkages (not all words use bullet points
            # for linkages).
            text_outside_list_items.append(node)
            continue
        assert isinstance(node, WikiNode)
        kind = node.kind
        # print("PARSE_LINKAGE_RECURSE CHILD", kind)
        if is_list(node) or kind in (NodeKind.TABLE, NodeKind.TABLE_ROW):
            toli = parse_linkage_recurse(
                wxr,
                node.children,
                field,
                sense,
                block_header_sense,
                word,
                data,
                sense_datas,
                is_reconstruction,
            )
            text_outside_list_items.extend(toli)
        elif is_list_item(node) or kind == NodeKind.TABLE_CELL:
            v = parse_linkage_item(
                wxr,
                node.children,
                field,
                word,
                data,
                sense_datas,
                is_reconstruction,
                sense,
            )
            if v is not None:
                # parse_linkage_item() can return a value that should
                # be used as the sense for the follow-on linkages,
                # which are typically provided in a table (see 滿)
                block_header_sense = "".join(v)
        elif kind in (
            NodeKind.TABLE_CAPTION,
            NodeKind.TABLE_HEADER_CELL,
            NodeKind.PREFORMATTED,
            NodeKind.BOLD,
        ):
            # Let's still ignore table extra stuff
            continue
        elif isinstance(node, HTMLNode):
            # Recurse to process inside the HTML for most tags
            if node.sarg in ("gallery", "ref", "cite", "caption"):
                continue
            classes = (node.attrs.get("class") or "").replace("+", " ").split()
            if "qualifier-content" in classes:
                sense1 = clean_node(wxr, None, node.children)
                if sense1.endswith(":"):
                    sense1 = sense1[:-1].strip()
                if sense and sense1:
                    wxr.wtp.debug(
                        "linkage qualifier-content on multiple "
                        "levels: {!r} and {!r}".format(sense, sense1),
                        sortid="page/2170",
                    )
                toli = parse_linkage_recurse(
                    wxr,
                    node.children,
                    field,
                    sense1,
                    block_header_sense,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                )
                text_outside_list_items.extend(toli)
            elif "list-switcher-header" in classes:
                block_header_sense = clean_node(wxr, None, node.children)
                if block_header_sense.endswith(":"):
                    block_header_sense = block_header_sense[:-1].strip()
            elif any(x in classes for x in ("NavFrame", "term-list")):
                # NavFrame uses previously assigned block_header_sense
                # (from a "(sense):" item) and clears it afterwards
                # print(f"{sense=}, {block_header_sense=}")
                toli = parse_linkage_recurse(
                    wxr,
                    node.children,
                    field,
                    sense or block_header_sense,
                    block_header_sense,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                )
                text_outside_list_items.extend(toli)
                block_header_sense = None
            else:
                toli = parse_linkage_recurse(
                    wxr,
                    node.children,
                    field,
                    sense,
                    block_header_sense,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                )
                text_outside_list_items.extend(toli)
        elif isinstance(node, LevelNode):
            # Just recurse to any possible subsections
            toli = parse_linkage_recurse(
                wxr,
                node.children,
                field,
                sense,
                block_header_sense,
                word,
                data,
                sense_datas,
                is_reconstruction,
            )
            text_outside_list_items.extend(toli)
        elif kind in (NodeKind.BOLD, NodeKind.ITALIC):
            # Skip these on top level; at least sometimes bold is
            # used for indicating a subtitle
            continue
        elif kind == NodeKind.LINK:
            # Recurse into the last argument
            # Apparently ":/" is used as a link to "/", so strip
            # initial value
            toli = parse_linkage_recurse(
                wxr,
                node.largs[-1],
                field,
                sense,
                block_header_sense,
                word,
                data,
                sense_datas,
                is_reconstruction,
            )
            text_outside_list_items.extend(toli)
        else:
            wxr.wtp.debug(
                "parse_linkage_recurse unhandled {}: {}".format(kind, node),
                sortid="page/2196",
            )

    return text_outside_list_items


def parse_linkage_item(
    wxr: WiktextractContext,
    contents: list[str | WikiNode],
    field: str,
    word: str,
    data: WordData,
    sense_datas: list[SenseData],
    is_reconstruction: bool,
    sense: str | None = None,
) -> list[str]:
    assert isinstance(contents, (list, tuple))
    assert isinstance(field, str)
    assert sense is None or isinstance(sense, str)

    # print("PARSE_LINKAGE_ITEM: {} ({}): {}"
    #    .format(field, sense, contents))

    parts: list[str] = []
    ruby: list[tuple[str, str]] = []
    urls: list[str] = []
    # data about link text; this is used to skip splitting on
    # linkage text items that contain stuff like commas; for
    # example "Hunde, die bellen, beißen nicht" in article
    # beißen is split into "Hunde", "die bellen" etc.
    # We take that link text and use it, eventually,
    # in split_at_comma_semi to skip splitting on those
    # commas.
    links_that_should_not_be_split: list[str] = []

    def item_recurse(
        contents: list[str | WikiNode], possible_sense: str | None = None
    ) -> bool:
        assert isinstance(contents, (list, tuple))
        nonlocal sense
        nonlocal ruby
        nonlocal parts
        is_sense = False
        # print("ITEM_RECURSE:", contents)
        for node in contents:
            if isinstance(node, str):
                parts.append(node)
                continue
            kind = node.kind
            # print(
            #     "ITEM_RECURSE KIND:",
            #     kind,
            #     node.sarg if node.sarg else node.largs,
            # )

            #### parts into possible_sense
            if (
                is_list_item(node)
                or is_list(node)
                or kind
                in (
                    NodeKind.TABLE,
                    NodeKind.TABLE_ROW,
                    NodeKind.TABLE_CELL,
                )
                and parts
            ):
                # print(f"{parts=}")
                candidate_sense: str | None
                candidate_sense = clean_node(wxr, None, parts)
                is_sense = False

                if candidate_sense.endswith(":"):
                    is_sense = True
                    candidate_sense = candidate_sense[:-1].strip()
                if candidate_sense.startswith("(") and candidate_sense.endswith(
                    ")"
                ):
                    is_sense = True
                    candidate_sense = candidate_sense[1:-1].strip()
                if (
                    candidate_sense.lower() == TRANSLATIONS_TITLE
                    or not is_sense
                ):
                    candidate_sense = None
                # print(f"{possible_sense=}, {is_sense=}")
                if is_sense:
                    possible_sense = candidate_sense
                    parts = []
                else:
                    candidate_sense = None

            # Handle nodes
            if is_list_item(node):
                parse_linkage_item(
                    wxr,
                    node.children,
                    field,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                    possible_sense or sense,
                )
            elif is_list(node) or kind in (
                NodeKind.TABLE,
                NodeKind.TABLE_ROW,
                NodeKind.TABLE_CELL,
            ):
                parse_linkage_recurse(
                    wxr,
                    node.children,
                    field,
                    possible_sense or sense,
                    None,
                    word,
                    data,
                    sense_datas,
                    is_reconstruction,
                )
            elif kind in (
                NodeKind.TABLE_HEADER_CELL,
                NodeKind.TABLE_CAPTION,
            ):
                continue
            elif kind == NodeKind.HTML:
                classes = (node.attrs.get("class") or "").split()
                if node.sarg in ("gallery", "ref", "cite", "caption"):
                    continue
                elif node.sarg == "ruby":
                    rb = parse_ruby(wxr, node)
                    if rb:
                        ruby.append(rb)
                        parts.append(rb[0])
                    continue
                elif node.sarg == "math":
                    parts.append(clean_node(wxr, None, node))
                    continue
                elif "interProject" in classes:
                    continue  # These do not seem to be displayed
                if "NavFrame" in classes:
                    parse_linkage_recurse(
                        wxr,
                        node.children,
                        field,
                        possible_sense or sense,
                        None,
                        word,
                        data,
                        sense_datas,
                        is_reconstruction,
                    )
                else:
                    item_recurse(node.children, possible_sense)
            elif kind == NodeKind.LINK:
                ignore = False
                if isinstance(node.largs[0][0], str):
                    v1 = node.largs[0][0].strip().lower()
                    if v1.startswith(
                        ns_title_prefix_tuple(wxr, "Category", True)
                        + ns_title_prefix_tuple(wxr, "File", True)
                    ):
                        ignore = True
                    if not ignore:
                        v = node.largs[-1]
                        if (
                            len(node.largs) == 1
                            and len(v) > 0
                            and isinstance(v[0], str)
                            and v[0][0] == ":"
                        ):
                            v = [v[0][1:]] + list(v[1:])  # type:ignore
                        if isinstance(v[0], str) and not v[0].isalnum():
                            links_that_should_not_be_split.append("".join(v[0]))  # type: ignore
                        item_recurse(v, possible_sense)
            elif kind == NodeKind.URL:
                if len(node.largs) < 2 and node.largs:
                    # Naked url captured
                    urls.extend(node.largs[-1])  # type:ignore[arg-type]
                    continue
                if len(node.largs) == 2:
                    # Url from link with text
                    urls.append(node.largs[0][-1])  # type:ignore[arg-type]
                # print(f"{node.largs=!r}")
                # print("linkage recurse URL {}".format(node))
                item_recurse(node.largs[-1], possible_sense)
            elif kind in (
                NodeKind.PREFORMATTED,
                NodeKind.BOLD,
                NodeKind.ITALIC,
            ):
                item_recurse(node.children)
            else:
                wxr.wtp.debug(
                    "linkage item_recurse unhandled {}: {}".format(
                        node.kind, node
                    ),
                    sortid="page/2073",
                )

        return is_sense

    # print("LINKAGE CONTENTS BEFORE ITEM_RECURSE: {!r}"
    #       .format(contents))

    is_sense = item_recurse(contents)

    if not is_sense:
        item = clean_node(wxr, None, parts)
        # print("LINKAGE ITEM CONTENTS:", parts)
        # print("CLEANED ITEM: {!r}".format(item))
        # print(f"URLS {urls=!r}")

        if v := parse_linkage_item_text(
            wxr,
            word,
            data,
            field,
            item,
            sense,
            ruby,
            sense_datas,
            is_reconstruction,
            urls or None,
            links_that_should_not_be_split or None,
        ):
            return [v]

    return []


def parse_linkage_item_text(
    wxr: WiktextractContext,
    word: str,
    data: WordData,
    field: str,
    item: str,
    sense: Optional[str],
    ruby: list,
    pos_datas: list,
    is_reconstruction: bool,
    urls: Optional[list[str]] = None,
    links: Optional[list[str]] = None,
) -> Optional[str]:
    """Parses a linkage item once it has been converted to a string.  This
    may add one or more linkages to ``data`` under ``field``.  This
    returns None or a string that contains a sense that should be applied
    to additional linkages (commonly used in tables for Asian characters)."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(word, str)  # Main word (derived from page title)
    assert isinstance(data, dict)  # Parsed linkages are stored here under field
    assert isinstance(field, str)  # The field under which to store linkage
    assert isinstance(item, str)  # The string to parse
    assert sense is None or isinstance(sense, str)
    assert isinstance(ruby, list)  # Captured ruby (hiragana/katakana) or ""
    assert isinstance(pos_datas, list)  # List of senses (containing "glosses")
    assert urls is None or isinstance(urls, list)  # Captured urls
    assert is_reconstruction in (True, False)

    item = item.replace("()", "")
    item = re.sub(r"\s+", " ", item)
    item = item.strip()

    base_roman = None
    base_alt = None
    base_english = None
    script_chars = False
    base_qualifier = None
    lang = wxr.wtp.section

    # If ``sense`` can be parsed as tags, treat it as tags instead
    if sense:
        cls = classify_desc(sense, no_unknown_starts=True)
        if cls == "tags":
            base_qualifier = sense
            sense = None

    # Check if this item is a stand-alone sense (or tag) specifier
    # for following items (e.g., commonly in a table, see 滿)
    m = re.match(r"\(([-a-zA-Z0-9 ]+)\):$", item)
    if m:
        return m.group(1)

    # Check for pre-split ignored linkages using the appropriate regexp
    if re.search(linkage_pre_split_ignore_re, item):
        return None

    # print("    LINKAGE ITEM: {}: {} (sense {})"
    #       .format(field, item, sense))

    # Replace occurrences of ~ in the item by the page title
    safetitle = wxr.wtp.title.replace("\\", "\\\\")  # type: ignore[union-attr]
    item = item.replace(" ~ ", " " + safetitle + " ")
    item = re.sub(r"^~ ", safetitle + " ", item)
    item = re.sub(r" ~$", " " + safetitle, item)

    # Many taxonomic terms contain hyponym lists that end with the
    # kind of the hyponym (a taxonomic level in plural).  Recognize
    # such and add the term in singular to all linkages in the list.
    m = re.search(taxonomic_ending_re, item)
    if m:
        base_english = taxonomic_ending_map[m.group(1)]
        item = item[: m.start()]

    # Some Korean and Japanese words use "word (romanized): english" pattern
    # Sometimes the parenthesized part contains comma-separated alt and roman.
    m = re.match(r"(.+?) \(([^():]+)\): ([-a-zA-Z0-9,. ]+)$", item)
    if m:
        rom = m.group(2)
        eng = m.group(3)
        rest = m.group(1)
        if (
            classify_desc(rest, no_unknown_starts=True) == "other"
            and classify_desc(eng, no_unknown_starts=True) == "english"
        ):
            item = rest
            base_roman = rom
            lst = base_roman.split(", ")
            if (
                len(lst) == 2
                and classify_desc(lst[0], no_unknown_starts=True) == "other"
            ):
                base_alt = lst[0]
                base_roman = lst[1]
            if base_english:
                base_english += "; " + eng
            else:
                base_english = eng

    # Many words have tags or similar descriptions in the beginning
    # followed by a colon and one or more linkages (e.g.,
    # panetella/Finnish)
    m = re.match(r"^\((([^():]|\([^()]*\))+)\): ([^:]*)$", item) or re.match(
        r"^([a-zA-Z][-'a-zA-Z0-9 ]*" r"(\([^()]+\)[-'a-zA-Z0-9 ]*)*): ([^:]*)$",
        item,
    )
    if m:
        desc = m.group(1)
        rest = m.group(len(m.groups()))
        # Check for certain comma-separated tags combined
        # with English text at the beginning or end of a
        # comma-separated parenthesized list
        lst = split_at_comma_semi(desc, skipped=links)
        while len(lst) > 1:
            # Check for tags at the beginning
            cls = classify_desc(lst[0], no_unknown_starts=True)
            if cls == "tags":
                if base_qualifier:
                    base_qualifier += ", " + lst[0]
                else:
                    base_qualifier = lst[0]
                lst = lst[1:]
                continue
            # Check for tags at the end
            cls = classify_desc(lst[-1], no_unknown_starts=True)
            if cls == "tags":
                if base_qualifier:
                    base_qualifier += ", " + lst[-1]
                else:
                    base_qualifier = lst[-1]
                lst = lst[:-1]
                continue
            break
        desc = ", ".join(lst)

        # Sometimes we have e.g. "chemistry (slang)" with are
        # both tags (see "stink").  Handle that case by
        # removing parentheses if the value is still tags.  The part with
        # parentheses could be on either side of the colon.
        if "(" in desc:
            x = desc.replace("(", ",").replace(")", ",")
            if classify_desc(x, no_unknown_starts=True) == "tags":
                desc = x
        elif "(" in rest:
            x = rest.replace("(", ",").replace(")", ",")
            if classify_desc(x, no_unknown_starts=True) == "tags":
                rest = desc
                desc = x

        # See if the prefix should trigger special handling for script
        # character, letter, digit, etc. handling
        if re.search(script_chars_re, desc):
            script_chars = True

        # Try to determine which side is description and which is
        # the linked term (both orders are widely used in Wiktionary)
        cls = classify_desc(desc, no_unknown_starts=True)
        cls2 = classify_desc(rest, no_unknown_starts=True)
        # print("linkage prefix: desc={!r} cls={} rest={!r} cls2={}"
        #      .format(desc, cls, rest, cls2))

        e1 = wxr.wtp.page_exists(desc)
        e2 = wxr.wtp.page_exists(rest)
        if cls != "tags":
            if (
                cls2 == "tags"
                or (e1 and not e1)
                or (
                    e1
                    and e2
                    and cls2 == "english"
                    and cls in ("other", "romanization")
                )
                or (
                    not e1
                    and not e2
                    and cls2 == "english"
                    and cls in ("other", "romanization")
                )
            ):
                desc, rest = rest, desc  # Looks like swapped syntax
                cls = cls2
        if re.search(linkage_paren_ignore_contains_re, desc):
            desc = ""
        # print("linkage colon prefix desc={!r} rest={!r} cls={}"
        #      .format(desc, rest, cls))

        # Handle the prefix according to its type
        if cls == "tags":
            if base_qualifier:
                base_qualifier += ", " + desc
            else:
                base_qualifier = desc
            item = rest
        elif desc in ("NATO phonetic", "Morse code", "Braille", "ASL Manual"):
            if base_english:
                base_english += "; " + base_english
            else:
                base_english = desc
            item = rest
        elif cls in ("english", "taxonomic"):
            if sense:
                sense += "; " + desc
            else:
                sense = desc
            item = rest
        elif desc.isdigit():
            idx = int(desc) - 1
            if idx >= 0 and idx < len(pos_datas):
                d = pos_datas[idx]
                gl = "; ".join(d.get("glosses", ()))
                if not gl:
                    wxr.wtp.debug(
                        "parenthesized numeric linkage prefix, "
                        "but the referenced sense has no gloss: "
                        "{}".format(desc),
                        sortid="linkages/355",
                    )
                elif sense:
                    sense += "; " + gl
                else:
                    sense = gl
                item = rest
            else:
                wxr.wtp.debug(
                    "parenthesized numeric linkage prefix, "
                    "but there is no sense with such index: {}".format(desc),
                    sortid="linkages/365",
                )
                item = rest
        else:
            wxr.wtp.debug(
                "unrecognized linkage prefix: {} desc={} rest={} "
                "cls={} cls2={} e1={} e2={}".format(
                    item, desc, rest, cls, cls2, e1, e2
                ),
                sortid="linkages/371",
            )
            item = rest

    base_sense = sense

    # Check for certain plural tag forms at end of items list, and apply
    # them to all items if found
    m = re.search(
        r" [-‐‑‒–—―] (diminutives|Diminutives|letters|digits|"
        r"characters|symbols|tetragrams|letter names|names|"
        r"female names|male names|proper nouns|contractions|"
        r"nonstandard spellings|verbs|prepositions|postpositions|"
        r"interjections|Abbreviations|abbreviations|variants|"
        r"ordinals|nouns|phrases|adjectives|adverbs|"
        r"augmentatives|pejoratives|compound words|numerals|"
        r"Tally marks|surnames|modern nonstandard spellings)$",
        item,
    )
    if m:
        suffix = m.group(1)
        if base_qualifier:
            base_qualifier += ", " + suffix
        else:
            base_qualifier = suffix
        item = item[: m.start()]

    # Certain linkage items have space-separated valus.  These are
    # generated by, e.g., certain templates
    if base_sense and base_sense.endswith(" paper sizes"):
        base_qualifier = None
        item = ", ".join(item.split())
    # XXX isn't this now handled by the generic digits/letters/etc code?
    # elif base_qualifier in ("Arabic digits",):
    #    item = ", ".join(item.split())

    item = re.sub(r"\s*\^\(\s*\)|\s*\^\s+", "", item)  # Now empty superscript
    item = item.strip()
    if not item:
        return None

    # Kludge: if the item contains ")/" (with possibly spaces in between),
    # replace it by a comma so it gets split.
    item = re.sub(r"\)\s*/", "), ", item)

    # The item may contain multiple comma-separated linkages
    if base_roman:
        subitems = [item]
    else:
        # Split at commas.  Also, in most cases split by " or ", but this
        # is complicated - "or" may end certain words (e.g., "logical or")
        # and it may separate head-final tags (e.g. "foo f or m").  Also,
        # some words have parenthesizxed parts in between, e.g.,
        # wife/English/Translations/Yiddish:
        #   "ווײַב‎ n (vayb) or f, פֿרוי‎ f (froy)"
        subitems = []
        for item1 in split_at_comma_semi(item, skipped=links):
            if " or " not in item1:
                subitems.append(item1)
                continue
            # Item1 contains " or "
            item2 = re.sub(r"\s*\([^)]*\)", "", item1)
            item2 = re.sub(r"\s+", " ", item2)
            if (
                (
                    lang not in head_final_bantu_langs
                    or not re.search(head_final_bantu_re, item2)
                )
                and (
                    lang not in head_final_other_langs
                    or not re.search(head_final_other_re, item2)
                )
                and (
                    not re.search(head_final_re, item2)
                    or (
                        item2[-1].isdigit()
                        and lang not in head_final_numeric_langs
                    )
                )
                and not re.search(r"\bor\b", wxr.wtp.title or "MISSING_TITLE")
                and all(
                    wxr.wtp.title not in x.split(" or ")
                    for x in split_at_comma_semi(item2, skipped=links)
                    if " or " in x
                )
            ):
                # We can split this item.  Split the non-cleaned version
                # that still has any intervening parenthesized parts.
                subitems.extend(
                    split_at_comma_semi(item1, extra=[" or "], skipped=links)
                )
            else:
                subitems.append(item1)
    if len(subitems) > 1:  # Would be merged from multiple subitems
        ruby = []  # XXX what is the purpose of this?
    for item1 in subitems:
        if len(subitems) > 1 and item1 in ("...", "…"):
            # Some lists have ellipsis in the middle - don't generate
            # linkages for the ellipsis
            continue
        item1 = item1.strip()
        qualifier = base_qualifier
        sense = base_sense
        parts = []
        roman = base_roman  # Usually None
        alt = base_alt  # Usually None
        taxonomic = None
        english = base_english

        # Some words have derived terms with parenthesized quoted English
        # descriptions, which can sometimes essentially be tags
        # Some word (bleki/Esperanto...) can have parentheses inside
        # the quotes, so let's make this regex even more unreadable.
        m = re.search(r"\s*\(“([^”]+)”\)", item1)
        if m:
            t = m.group(1)
            item1 = (item1[: m.start()] + item1[m.end() :]).strip()
            cls = classify_desc(t)
            if cls == "tags":
                if qualifier:
                    qualifier += ", " + t
                else:
                    qualifier = t
            else:
                english = t

        # Some Korean words use "word (alt, oman, “english”) pattern
        # See 滿/Korean
        m = re.match(
            r"([^(),;:]+) \(([^(),;:]+), ([^(),;:]+), "
            r'[“”"]([^”“"]+)[“”"]\)$',
            item1,
        )
        if (
            m
            and classify_desc(m.group(1), no_unknown_starts=True) == "other"
            and classify_desc(m.group(2), no_unknown_starts=True) == "other"
        ):
            alt = m.group(2)
            roman = m.group(3)
            english = m.group(4)
            item1 = m.group(1)

        words = item1.split(" ")
        if (
            len(words) > 1
            and words[0] in linkage_beginning_tags
            and words[0] != wxr.wtp.title
        ):
            t = linkage_beginning_tags[words[0]]
            item1 = " ".join(words[1:])
            if qualifier:
                qualifier += ", " + t
            else:
                qualifier = t

        # Extract quoted English translations (there are also other
        # kinds of English translations)
        def english_repl(m: re.Match) -> str:
            nonlocal english
            nonlocal qualifier
            v = m.group(1).strip()
            # If v is "tags: sense", handle the tags
            m1 = re.match(r"^([a-zA-Z ]+): (.*)$", v)
            if m1 is not None:
                desc, rest = m1.groups()
                if classify_desc(desc, no_unknown_starts=True) == "tags":
                    if qualifier:
                        qualifier += ", " + desc
                    else:
                        qualifier = desc
                    v = rest
            if english:
                english += "; " + v
            else:
                english = v
            return ""

        item1 = re.sub(r'[“"]([^“”"]+)[“”"],?\s*', english_repl, item1).strip()

        # There could be multiple parenthesized parts, and
        # sometimes both at the beginning and at the end.
        # And sometimes even in the middle, as in e.g.
        # wife/English/Translations/Yiddish
        while not script_chars and (
            not sense or not re.search(script_chars_re, sense)
        ):
            par = None
            nonfirst_par = False
            if par is None:
                # Try to find a parenthesized part from the beginning.
                m = re.match(r"\((([^()]|\([^()]*\))*)\):?\s*", item1)
                if m:
                    par = m.group(1)
                    item1 = item1[m.end() :]
                else:
                    # Try to find a parenthesized part at the end or from the
                    # middle.
                    m = re.search(
                        r"\s+\((\d|\d\d|[^\d]([^()]|\([^()]*\))*)\)" r"(\.$)?",
                        item1,
                    )
                    if m:
                        par = m.group(1)
                        item1 = item1[: m.start()] + item1[m.end() :]
                        nonfirst_par = True
            if not par:
                break
            if re.search(linkage_paren_ignore_contains_re, par):
                continue  # Skip these linkage descriptors
            par = par.strip()
            # Handle tags from beginning of par.  We also handle "other"
            # here as Korean entries often have Hanja form in the
            # beginning of parenthesis, before romanization.  Similar
            # for many Japanese entries.
            while par:
                idx = par.find(",")
                if idx <= 0:
                    break
                cls = classify_desc(par[:idx], no_unknown_starts=True)
                if cls == "other" and not alt:
                    alt = par[:idx]
                elif cls == "taxonomic":
                    taxonomic = par[:idx]
                elif cls == "tags":
                    if qualifier:
                        qualifier += ", " + par[:idx]
                    else:
                        qualifier = par[:idx]
                else:
                    break
                par = par[idx + 1 :].strip()

            # Check for certain comma-separated tags combined
            # with English text at the beginning or end of a
            # comma-separated parenthesized list
            lst = par.split(",") if len(par) > 1 else [par]
            lst = list(x.strip() for x in lst if x.strip())
            while len(lst) > 1:
                cls = classify_desc(lst[0], no_unknown_starts=True)
                if cls == "tags":
                    if qualifier:
                        qualifier += ", " + lst[0]
                    else:
                        qualifier = lst[0]
                    lst = lst[1:]
                    continue
                cls = classify_desc(lst[-1], no_unknown_starts=True)
                if cls == "tags":
                    if qualifier:
                        qualifier += ", " + lst[-1]
                    else:
                        qualifier = lst[-1]
                    lst = lst[:-1]
                    continue
                break
            par = ", ".join(lst)

            # Handle remaining types
            if not par:
                continue
            if re.search(script_chars_re, par):
                script_chars = True
                if classify_desc(par, no_unknown_starts=True) == "tags":
                    if base_qualifier:
                        base_qualifier += "; " + par
                    else:
                        base_qualifier = par
                    if qualifier:
                        qualifier += "; " + par
                    else:
                        qualifier = par
                else:
                    if base_sense:
                        base_sense += "; " + par
                    else:
                        base_sense = par
                    if sense:
                        sense += "; " + par
                    else:
                        sense = par
            elif par.endswith(" letter names"):
                if base_qualifier:
                    base_qualifier += "; " + par
                else:
                    base_qualifier = par
                if qualifier:
                    qualifier += "; " + par
                else:
                    qualifier = par
            else:
                cls = classify_desc(par)
                # print("classify_desc: {!r} -> {}".format(par, cls))
                if cls == "tags":
                    if qualifier:
                        qualifier += ", " + par
                    else:
                        qualifier = par
                elif cls == "english":
                    if nonfirst_par:
                        if english:
                            english += "; " + par
                        else:
                            english = par
                    else:
                        if sense:
                            sense += "; " + par
                        else:
                            sense = par
                elif cls == "romanization":
                    roman = par
                elif cls == "taxonomic":
                    taxonomic = par
                elif par.isdigit():
                    idx = int(par) - 1
                    if idx >= 0 and idx < len(pos_datas):
                        d = pos_datas[idx]
                        gl = "; ".join(d.get("glosses", ()))
                        if not gl:
                            wxr.wtp.debug(
                                "parenthesized number "
                                "but the referenced sense has no "
                                "gloss: {}".format(par),
                                sortid="linkages/665",
                            )
                        elif sense:
                            sense += "; " + gl
                        else:
                            sense = gl
                    else:
                        wxr.wtp.debug(
                            "parenthesized number but there is "
                            "no sense with such index: {}".format(par),
                            sortid="linkages/674",
                        )
                else:
                    if alt:
                        alt += "; " + par
                    else:
                        alt = par

        # Handle certain special cases, unless we are parsing
        # script characters.
        if not script_chars:
            # Ignore all linkages with certain prefixes, suffixes, or parts
            # (this is done after removing certain prefixes and suffixes)
            if re.search(linkage_ignore_re, item1):
                continue  # Ignore linkages with certain prefixes

            # Remove certain prefixes from linkages
            m = re.match(linkage_remove_prefixes_re, item1)
            if m:
                prefix = item1[: m.end()]
                item1 = item1[m.end() :]
                if prefix in linkage_remove_prefixes_tags:
                    if qualifier:
                        qualifier += ", " + linkage_remove_prefixes_tags[prefix]
                    else:
                        qualifier = linkage_remove_prefixes_tags[prefix]
                # Recheck ignored linkages
                if re.search(linkage_ignore_re, item1):
                    continue

            # Remove certain suffixes from linkages
            m = re.search(linkage_remove_suffixes_re, item1)
            if m:
                item1 = item1[: m.start()]

            # Parse linkages with "value = english" syntax (e.g.,
            # väittää/Finnish)
            idx = item1.find(" = ")
            if idx >= 0:
                eng = item1[idx + 3 :]
                if classify_desc(eng, no_unknown_starts=True) == "english":
                    english = eng
                    item1 = item1[:idx]
                else:
                    # Some places seem to use it reversed
                    # "english = value"
                    eng = item1[:idx]
                    if classify_desc(eng, no_unknown_starts=True) == "english":
                        english = eng
                        item1 = item1[idx + 3 :]

            # Parse linkages with "value - english" syntax (e.g.,
            # man/Faroese)
            m = re.search(r" [-‐‑‒–—―] ", item1)
            if m and "(" not in item1:
                suffix = item1[m.end() :]
                cls = classify_desc(suffix, no_unknown_starts=True)
                if cls == "english":
                    # This case intentionally ignores old values from english
                    # (otherwise taxonomic lists fail)
                    english = suffix
                    item1 = item1[: m.start()]
                elif cls == "tags":
                    if qualifier:
                        qualifier += ", " + suffix
                    else:
                        qualifier = suffix
                    item1 = item1[: m.start()]

            # Parse certain tags at the end of the linked term (unless
            # we are in a letters list)
            item1, q = parse_head_final_tags(wxr, lang or "MISSING_LANG", item1)
            if q:
                if qualifier:
                    qualifier += ", " + ", ".join(q)
                else:
                    qualifier = ", ".join(q)

        m = re.search(linkage_truncate_re, item1)
        if m:
            # suffix = item1[m.start():]  # Currently ignored
            item1 = item1[: m.start()]
        if not item1:
            continue  # Ignore empty link targets
        if item1 == word:
            continue  # Ignore self-links

        def add(w: str, r: Optional[str]) -> None:
            assert isinstance(w, str)
            assert r is None or isinstance(r, str)
            nonlocal alt
            nonlocal taxonomic

            # We remove "*" from the beginning of reconstruction linkages.
            # Such linkages should only occur in reconstruction senses, so
            # this should not cause ambiguity.
            if is_reconstruction and w.startswith("*"):
                w = w[1:]

            # Check if the word contains the Fullwith Solidus, and if
            # so, split by it and treat the the results as alternative
            # linkages.  (This is very commonly used for alternative
            # written forms in Chinese compounds and other linkages.)
            # However, if the word contains a comma, then we wont't
            # split as this is used when we have a different number
            # of romanizations than written forms, and don't know
            # which is which.
            if (
                (not w or "," not in w)
                and (not r or "," not in r)
                and not wxr.wtp.page_exists(w)
            ):
                lst = w.split("／") if len(w) > 1 else [w]
                if len(lst) == 1:
                    lst = w.split(" / ")
                if len(lst) == 1 and len(lst[0]) >= 6:
                    lst = w.split("/")
                if len(lst) > 1:
                    # Treat each alternative as separate linkage
                    for w in lst:
                        add(w, r)
                    return None

            # Heuristically remove "." at the end of most linkages
            # (some linkage lists end in a period, but we also have
            # abbreviations that end with a period that should be kept)
            if (
                w.endswith(".")
                and not wxr.wtp.page_exists(w)
                and (
                    wxr.wtp.page_exists(w[:-1])
                    or (len(w) >= 5)
                    and "." not in w[:-1]
                )
            ):
                w = w[:-1]

            # If we have roman but not alt and the word is ASCII,
            # move roman to alt.
            if r and not alt and w.isascii():
                alt = r
                r = None
            # Add the linkage
            dt: LinkageData = {}
            if qualifier:
                parse_sense_qualifier(wxr, qualifier, dt)
            if sense:
                dt["sense"] = sense.strip()
            if r:
                dt["roman"] = r.strip()
            if ruby:
                dt["ruby"] = ruby
            if english:
                dt["english"] = english.strip()  # DEPRECATED for "translation"
                dt["translation"] = english.strip()
            if taxonomic:
                if re.match(r"×[A-Z]", taxonomic):
                    data_append(dt, "tags", "extinct")
                    taxonomic = taxonomic[1:]
                dt["taxonomic"] = taxonomic
            if re.match(r"×[A-Z]", w):
                data_append(dt, "tags", "extinct")
                w = w[1:]  # Remove × before dead species names
            if alt and re.match(r"×[A-Z]", alt):
                data_append(dt, "tags", "extinct")
                alt = alt[1:]  # Remove × before dead species names
            if alt and alt.strip() != w:
                dt["alt"] = alt.strip()
            if urls:
                dt["urls"] = [
                    url.strip() for url in urls if url and isinstance(url, str)
                ]
            dt["word"] = w
            for old in data.get(field, ()):  # type: ignore[attr-defined]
                if dt == old:
                    break
            else:
                data_append(data, field, dt)

        # Handle exceptional linkage splits and other linkage
        # conversions (including expanding to variant forms)
        if item1 in linkage_split_exceptions:
            for item2 in linkage_split_exceptions[item1]:
                add(item2, roman)
            continue

        # Various templates for letters in scripts use spaces as
        # separators and also have multiple characters without
        # spaces consecutively.
        v = sense or qualifier
        # print("lang={} v={} script_chars={} item1={!r}"
        #       .format(wxr.wtp.section, v, script_chars, item1))
        if v and script_chars:
            if (
                len(item1.split()) > 1
                or len(list(re.finditer(unicode_dc_re, item1))) == 2
                or (len(subitems) > 10 and v in ("Hiragana", "Katakana"))
            ):
                if v == qualifier:
                    # if sense:
                    #     sense += "; " + qualifier
                    # else:
                    #     sense = qualifier
                    qualifier = None
                if re.search(r" (letters|digits|script)$", v):
                    qualifier = v  # Also parse as qualifier
                elif re.search(
                    r"Variations of letter |"
                    r"Letters using |"
                    r"Letters of the ",
                    v,
                ):
                    qualifier = "letter"
                parts = item1.split(". ")
                extra: Sequence[str] = ()
                if len(parts) > 1:
                    extra = parts[1:]
                    item1 = parts[0]
                # Handle multi-character names for chars in language's
                # alphabet, e.g., "Ny ny" in P/Hungarian.
                if (
                    len(subitems) > 20
                    and len(item1.split()) == 2
                    and all(len(x) <= 3 for x in item1.split())
                ):
                    parts = list(
                        m.group(0)
                        for m in re.finditer(r"(\w[\u0300-\u036f]?)+|.", item1)
                        if not m.group(0).isspace()
                        and m.group(0) not in ("(", ")")
                    )
                else:
                    parts = list(
                        m.group(0)
                        for m in re.finditer(r".[\u0300-\u036f]?", item1)
                        if not m.group(0).isspace()
                        and m.group(0) not in ("(", ")")
                    )
                for e in extra:
                    idx = e.find(":")
                    if idx >= 0:
                        e = e[idx + 1 :].strip()
                        if e.endswith("."):
                            e = e[:-1]
                        parts.extend(e.split())

                # XXX this is not correct - see P/Vietnamese
                # While some sequences have multiple consecutive
                # characters, others use pairs and some have
                # 2/3 character names, e.g., "Ng ng".

                rparts: Optional[list[Optional[str]]] = None
                if roman:
                    rparts = list(
                        m.group(0)
                        for m in re.finditer(r".[\u0300-\u036f]", roman)
                        if not m.group(0).isspace()
                    )
                    if len(rparts) != len(parts):
                        rparts = None
                if not rparts:
                    rparts = [None] * len(parts)

                for w, r in zip(parts, rparts):
                    add(w, r)
                continue

        add(item1, roman)
    return None
