# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
from collections import defaultdict
from copy import copy
from typing import Any, Callable, Optional, Union

from mediawiki_langcodes import name_to_code
from wikitextprocessor.core import (
    NamespaceDataEntry,
    PostTemplateFnCallable,
    TemplateArgs,
    TemplateFnCallable,
)
from wikitextprocessor.node_expand import NodeHandlerFnCallable
from wikitextprocessor.parser import GeneralNode, NodeKind, WikiNode

from .clean import clean_value
from .datautils import data_append, data_extend
from .import_utils import import_extractor_module
from .wxr_context import WiktextractContext

# NodeKind values for subtitles
LEVEL_KINDS = {
    NodeKind.LEVEL2,
    NodeKind.LEVEL3,
    NodeKind.LEVEL4,
    NodeKind.LEVEL5,
    NodeKind.LEVEL6,
}


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    """Parses the text of a Wiktionary page and returns a list of
    dictionaries, one for each word/part-of-speech defined on the page
    for the languages specified by ``capture_language_codes`` (None means
    all available languages).  ``word`` is page title, and ``text`` is
    page text in Wikimedia format.  Other arguments indicate what is
    captured."""
    page_extractor_mod = import_extractor_module(wxr.wtp.lang_code, "page")
    page_data = page_extractor_mod.parse_page(wxr, page_title, page_text)
    if wxr.config.extract_thesaurus_pages:
        inject_linkages(wxr, page_data)
    if wxr.config.dump_file_lang_code == "en":
        process_categories(wxr, page_data)
    remove_duplicate_data(page_data)
    return page_data


def is_panel_template(wxr: WiktextractContext, template_name: str) -> bool:
    """Checks if `Template_name` is a known panel template name (i.e., one that
    produces an infobox in Wiktionary, but this also recognizes certain other
    templates that we do not wish to expand)."""
    page_extractor_mod = import_extractor_module(wxr.wtp.lang_code, "page")
    if (
        hasattr(page_extractor_mod, "PANEL_TEMPLATES")
        and template_name in page_extractor_mod.PANEL_TEMPLATES
    ):
        return True
    if hasattr(
        page_extractor_mod, "PANEL_PREFIXES"
    ) and template_name.startswith(tuple(page_extractor_mod.PANEL_PREFIXES)):
        return True
    return False


def recursively_extract(
    contents: Union[WikiNode, str, list[Union[str, WikiNode]]],
    fn: Callable[[Union[WikiNode, list[WikiNode]]], bool],
) -> tuple[list[Union[str, WikiNode]], list[Union[str, WikiNode]]]:
    """Recursively extracts elements from contents for which ``fn`` returns
    True.  This returns two lists, the extracted elements and the remaining
    content (with the extracted elements removed at each level).  Only
    WikiNode objects can be extracted."""
    # If contents is a list, process each element separately
    extracted = []
    new_contents = []
    if isinstance(contents, (list, tuple)):
        for x in contents:
            e1, c1 = recursively_extract(x, fn)
            extracted.extend(e1)
            new_contents.extend(c1)
        return extracted, new_contents
    # If content is not WikiNode, just return it as new contents.
    if not isinstance(contents, WikiNode):
        return [], [contents]
    # Check if this content should be extracted
    if fn(contents):
        return [contents], []
    # Otherwise content is WikiNode, and we must recurse into it.
    kind = contents.kind
    new_node = copy(contents)
    new_node.children = []
    new_node.sarg = ""
    new_node.largs = []
    new_node.attrs = {}
    new_contents.append(new_node)
    if kind in LEVEL_KINDS or kind == NodeKind.LINK:
        # Process args and children
        new_args = []
        for arg in contents.largs:
            e1, c1 = recursively_extract(arg, fn)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.largs = new_args
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in {
        NodeKind.ITALIC,
        NodeKind.BOLD,
        NodeKind.TABLE,
        NodeKind.TABLE_CAPTION,
        NodeKind.TABLE_ROW,
        NodeKind.TABLE_HEADER_CELL,
        NodeKind.TABLE_CELL,
        NodeKind.PRE,
        NodeKind.PREFORMATTED,
    }:
        # Process only children
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in (NodeKind.HLINE,):
        # No arguments or children
        pass
    elif kind in (NodeKind.LIST, NodeKind.LIST_ITEM):
        # Keep args as-is, process children
        new_node.sarg = contents.sarg
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in {
        NodeKind.TEMPLATE,
        NodeKind.TEMPLATE_ARG,
        NodeKind.PARSER_FN,
        NodeKind.URL,
    }:
        # Process only args
        new_args = []
        for arg in contents.largs:
            e1, c1 = recursively_extract(arg, fn)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.largs = new_args
    elif kind == NodeKind.HTML:
        # Keep attrs and args as-is, process children
        new_node.attrs = contents.attrs
        new_node.sarg = contents.sarg
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    else:
        raise RuntimeError(f"recursively_extract: unhandled kind {kind}")
    return extracted, new_contents


def inject_linkages(wxr: WiktextractContext, page_data: list[dict]) -> None:
    # Inject linkages from thesaurus entries
    from .thesaurus import search_thesaurus

    local_thesaurus_ns = wxr.wtp.NAMESPACE_DATA.get("Thesaurus", {}).get("name")  # type: ignore[call-overload]
    for data in page_data:
        if "pos" not in data:
            continue
        word = data["word"]
        lang_code = data["lang_code"]
        pos = data["pos"]
        for term in search_thesaurus(
            wxr.thesaurus_db_conn,  # type:ignore[arg-type]
            word,
            lang_code,
            pos,  # type: ignore[arg-type]
        ):
            for dt in data.get(term.linkage, ()):
                if dt.get("word") == term.term and (
                    not term.sense or dt.get("sense") == term.sense
                ):
                    break
            else:
                dt = {
                    "word": term.term,
                    "source": f"{local_thesaurus_ns}:{word}",
                }
                if len(term.sense) > 0:
                    dt["sense"] = term.sense
                if len(term.tags) > 0:
                    dt["tags"] = term.tags
                if len(term.raw_tags) > 0:
                    dt["raw_tags"] = term.raw_tags
                if len(term.topics) > 0:
                    dt["topics"] = term.topics
                if len(term.roman) > 0:
                    dt["roman"] = term.roman
                data_append(data, term.linkage, dt)


def process_categories(
    wxr: WiktextractContext, page_data: list[dict[str, Any]]
) -> None:
    # Categories are not otherwise disambiguated, but if there is only
    # one sense and only one data in ret for the same language, move
    # categories to the only sense.  Note that categories are commonly
    # specified for the page, and thus if we have multiple data in
    # ret, we don't know which one they belong to (not even which
    # language necessarily?).
    # XXX can Category links be specified globally (i.e., in a different
    # language?)
    by_lang = defaultdict(list)
    for data in page_data:
        by_lang[data["lang"]].append(data)
    for la, lst in by_lang.items():
        if len(lst) > 1:
            # Propagate categories from the last entry for the language to
            # its other entries.  It is common for them to only be specified
            # in the last part-of-speech.
            last = lst[-1]
            for field in ("categories",):
                if field not in last:
                    continue
                vals = last[field]
                for data in lst[:-1]:
                    assert data is not last
                    assert data.get(field) is not vals
                    if data.get("alt_of") or data.get("form_of"):
                        continue  # Don't add to alt-of/form-of entries
                    data_extend(data, field, vals)
            continue
        if len(lst) != 1:
            continue
        data = lst[0]
        senses = data.get("senses") or []
        if len(senses) != 1:
            continue
        # Only one sense for this language.  Move categories and certain other
        # data to sense.
        for field in ("categories", "topics", "wikidata", "wikipedia"):
            if field in data:
                v = data[field]
                del data[field]
                data_extend(senses[0], field, v)

    # If the last part-of-speech of the last language (i.e., last item in "ret")
    # has categories or topics not bound to a sense, propagate those
    # categories and topics to all datas on "ret".  It is common for categories
    # to be specified at the end of an article.  Apparently these can also
    # apply to different languages.
    if len(page_data) > 1:
        last = page_data[-1]
        for field in ("categories",):
            if field not in last:
                continue
            lst = last[field]
            for data in page_data[:-1]:
                if data.get("form_of") or data.get("alt_of"):
                    continue  # Don't add to form_of or alt_of entries
                data_extend(data, field, lst)

    # Remove category links that start with a language name from entries for
    # different languages
    rhymes_ns_prefix = (
        wxr.wtp.NAMESPACE_DATA.get("Rhymes", {}).get("name", "") + ":"  # type: ignore[call-overload]
    )
    for data in page_data:
        lang_code = data.get("lang_code")
        cats = data.get("categories", [])
        new_cats = []
        for cat in cats:
            no_prefix_cat = cat.removeprefix(rhymes_ns_prefix)
            cat_lang = no_prefix_cat.split(maxsplit=1)[0].split(
                "/", maxsplit=1
            )[0]
            cat_lang_code = name_to_code(cat_lang, "en")
            if (
                cat_lang_code != ""
                and cat_lang_code != lang_code
                and not (lang_code == "mul" and cat_lang_code == "en")
            ):
                continue
            new_cats.append(cat)
        if len(new_cats) == 0:
            if "categories" in data:
                del data["categories"]
        else:
            data["categories"] = new_cats


def remove_duplicate_data(page_data: dict) -> None:
    # Remove duplicates from tags, categories, etc.
    for data in page_data:
        for field in ("categories", "topics", "tags", "wikidata", "wikipedia"):
            if field in data:
                data[field] = sorted(set(data[field]))
            for sense in data.get("senses", ()):
                if field in sense:
                    sense[field] = sorted(set(sense[field]))

    # If raw_glosses is identical to glosses, remove it
    # If "empty-gloss" in tags and there are glosses, remove the tag
    for data in page_data:
        for s in data.get("senses", []):
            rglosses = s.get("raw_glosses", ())
            if not rglosses:
                continue
            sglosses = s.get("glosses", ())
            if sglosses:
                tags = s.get("tags", ())
                while "empty-gloss" in s.get("tags", ()):
                    tags.remove("empty-gloss")
            if len(rglosses) != len(sglosses):
                continue
            same = True
            for rg, sg in zip(rglosses, sglosses):
                if rg != sg:
                    same = False
                    break
            if same:
                del s["raw_glosses"]


def clean_node(
    wxr: WiktextractContext,
    sense_data: Optional[Any],
    wikinode: GeneralNode,
    template_fn: Optional[TemplateFnCallable] = None,
    post_template_fn: Optional[PostTemplateFnCallable] = None,
    node_handler_fn: Optional[NodeHandlerFnCallable] = None,
    collect_links: bool = False,
    no_strip=False,
    no_html_strip=False,
) -> str:
    """
    Expands node or nodes to text, cleaning up HTML tags and duplicate spaces.

    If `sense_data` is a dictionary, expanded category links will be added to
    it under the `categories` key. And if `collect_link` is `True`, expanded
    links will be added to the `links` key.
    """

    # print("CLEAN_NODE:", repr(value))
    def clean_template_fn(name: str, ht: TemplateArgs) -> Optional[str]:
        if template_fn is not None:
            return template_fn(name, ht)
        if is_panel_template(wxr, name):
            return ""
        return None

    def clean_node_handler_fn_default(
        node: WikiNode,
    ) -> Optional[list[Union[str, WikiNode]]]:
        assert isinstance(node, WikiNode)
        kind = node.kind
        if kind in {
            NodeKind.TABLE_CELL,
            NodeKind.TABLE_HEADER_CELL,
        }:
            return node.children
        return None

    if node_handler_fn is not None:
        # override clean_node_handler_fn, the def above can't be accessed
        clean_node_handler_fn = node_handler_fn
    else:
        clean_node_handler_fn = clean_node_handler_fn_default

    # print("clean_node: value={!r}".format(value))
    v = wxr.wtp.node_to_html(
        wikinode,
        node_handler_fn=clean_node_handler_fn,
        template_fn=template_fn,
        post_template_fn=post_template_fn,
    )
    # print("##########")
    # print(f"{wikinode=}")
    # print("clean_node: v={!r}".format(v))

    # Capture categories if sense_data has been given.  We also track
    # Lua execution errors here.
    # If collect_links=True (for glosses), capture links
    category_ns_data: NamespaceDataEntry = wxr.wtp.NAMESPACE_DATA.get(
        "Category",
        {},  # type: ignore[typeddict-item]
    )
    category_ns_names: set[str] = {category_ns_data.get("name")} | set(
        category_ns_data.get("aliases")  # type:ignore[assignment,arg-type]
    )
    category_ns_names |= {"Category", "category"}
    category_names_pattern = rf"(?:{'|'.join(category_ns_names)})"
    if sense_data is not None:
        # Check for Lua execution error
        if '<strong class="error">Lua execution error' in v:
            data_append(sense_data, "tags", "error-lua-exec")
        if '<strong class="error">Lua timeout error' in v:
            data_append(sense_data, "tags", "error-lua-timeout")
        # Capture Category tags
        if not collect_links:
            for m in re.finditer(
                rf"(?is)\[\[:?\s*{category_names_pattern}\s*:([^]|]+)",
                v,
            ):
                cat = clean_value(wxr, m.group(1))
                cat = re.sub(r"\s+", " ", cat)
                cat = cat.strip()
                if not cat:
                    continue
                if not sense_data_has_value(sense_data, "categories", cat):
                    data_append(sense_data, "categories", cat)
        else:
            for m in re.finditer(
                r"(?is)\[\[:?(\s*([^][|:]+):)?\s*([^]|]+)(\|([^]|]+))?\]\]",
                #            1   2               3       4  5
                v,
            ):
                # Add here other stuff different "Something:restofthelink"
                # things;
                if m.group(2) and m.group(2).strip() in category_ns_names:
                    cat = clean_value(wxr, m.group(3))
                    cat = re.sub(r"\s+", " ", cat)
                    cat = cat.strip()
                    if not cat:
                        continue
                    if not sense_data_has_value(sense_data, "categories", cat):
                        data_append(sense_data, "categories", cat)
                elif not m.group(1):
                    if m.group(5):
                        ltext = clean_value(wxr, m.group(5))
                        ltarget = clean_value(wxr, m.group(3))
                    elif not m.group(3):
                        continue
                    else:
                        txt = clean_value(wxr, m.group(3))
                        ltext = txt
                        ltarget = txt
                    ltarget = re.sub(r"\s+", " ", ltarget)
                    ltarget = ltarget.strip()
                    ltext = re.sub(r"\s+", " ", ltext)
                    ltext = ltext.strip()
                    if not ltext and not ltarget:
                        continue
                    if not ltext and ltarget:
                        ltext = ltarget
                    ltuple = (ltext, ltarget)
                    if not sense_data_has_value(sense_data, "links", ltuple):
                        data_append(sense_data, "links", ltuple)

    v = clean_value(wxr, v, no_strip=no_strip, no_html_strip=no_html_strip)
    # print("After clean_value:", repr(v))

    # Strip any unhandled templates and other stuff.  This is mostly intended
    # to clean up erroneous codings in the original text.
    # v = re.sub(r"(?s)\{\{.*", "", v)
    # Some templates create <sup>(Category: ...)</sup>; remove
    v = re.sub(
        rf"(?si)\s*(?:<sup>)?\({category_names_pattern}:[^)]+\)(?:</sup>)?",
        "",
        v,
    )
    # Some templates create question mark in <sup>, e.g.,
    # some Korean Hanja form
    v = re.sub(r"\^\?", "", v)
    return v


def sense_data_has_value(
    sense_data: dict[str, Any], name: str, value: Any
) -> bool:
    """
    Return True if `sense_data` has value in the attribute `name`'s value or
    in the value of key `name` if `sense_date` is dictionary.
    """
    if hasattr(sense_data, name):
        return value in getattr(sense_data, name)
    elif isinstance(sense_data, dict):
        return value in sense_data.get(name, ())  # type:ignore[operator]
    return False
