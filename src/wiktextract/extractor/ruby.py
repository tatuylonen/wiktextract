from typing import Optional, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import (
    GeneralNode,
    HTMLNode,
    LevelNode,
    TemplateNode,
)
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def parse_ruby(
    wxr: WiktextractContext, node: WikiNode
) -> Optional[tuple[str, str]]:
    """Parse a HTML 'ruby' node for a kanji part and a furigana (ruby) part,
    and return a tuple containing those. Discard the rp-element's parentheses,
    we don't do anything with them."""
    ruby_nodes: list[Union[str, WikiNode]] = []
    furi_nodes: list[Union[str, WikiNode]] = []  # furi_nodes is technically
    # just list[WikiNode], but this appeases the type-checker for clean_node()
    for child in node.children:
        if (
            not isinstance(child, WikiNode)
            or child.kind != NodeKind.HTML
            or child.sarg not in {"rp", "rt"}
        ):
            ruby_nodes.append(child)
        elif child.sarg == "rt":
            furi_nodes.append(child)
    ruby_kanji = clean_node(wxr, None, ruby_nodes).strip()
    furigana = clean_node(wxr, None, furi_nodes).strip()
    if not ruby_kanji or not furigana:
        # like in パイスラッシュ there can be a template that creates a ruby
        # element with an empty something (apparently, seeing as how this
        # works), leaving no trace of the broken ruby element in the final
        # HTML source of the page!
        return None
    return ruby_kanji, furigana


def extract_ruby(
    wxr: WiktextractContext,
    contents: GeneralNode,
) -> tuple[list[tuple[str, ...]], list[Union[WikiNode, str]]]:
    # If contents is a list, process each element separately
    extracted = []
    new_contents = []
    if isinstance(contents, (list, tuple)):
        for x in contents:
            e1, c1 = extract_ruby(wxr, x)
            extracted.extend(e1)
            new_contents.extend(c1)
        return extracted, new_contents
    # If content is not WikiNode, just return it as new contents.
    if not isinstance(contents, WikiNode):
        return [], [contents]
    # Check if this content should be extracted
    if contents.kind == NodeKind.HTML and contents.sarg == "ruby":
        rb = parse_ruby(wxr, contents)
        if rb is not None:
            return [rb], [rb[0]]
    # Otherwise content is WikiNode, and we must recurse into it.
    kind = contents.kind
    new_node = WikiNode(kind, contents.loc)
    if kind in {
        NodeKind.LEVEL2,
        NodeKind.LEVEL3,
        NodeKind.LEVEL4,
        NodeKind.LEVEL5,
        NodeKind.LEVEL6,
        NodeKind.LINK,
    }:
        # Process args and children
        if kind != NodeKind.LINK:
            new_node = LevelNode(kind, new_node.loc)
        new_args = []
        for arg in contents.largs:
            e1, c1 = extract_ruby(wxr, arg)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.largs = new_args
        e1, c1 = extract_ruby(wxr, contents.children)
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
        e1, c1 = extract_ruby(wxr, contents.children)
        extracted.extend(e1)
        new_node.children = c1
    elif kind == NodeKind.HLINE:
        # No arguments or children
        pass
    elif kind in (NodeKind.LIST, NodeKind.LIST_ITEM):
        # Keep args as-is, process children
        new_node.sarg = contents.sarg
        e1, c1 = extract_ruby(wxr, contents.children)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in {
        NodeKind.TEMPLATE,
        NodeKind.TEMPLATE_ARG,
        NodeKind.PARSER_FN,
        NodeKind.URL,
    }:
        # Process only args
        if kind == NodeKind.TEMPLATE:
            new_node = TemplateNode(
                new_node.loc,
                wxr.wtp.namespace_prefixes(
                    wxr.wtp.NAMESPACE_DATA["Template"]["id"]
                ),
            )
        new_args = []
        for arg in contents.largs:
            e1, c1 = extract_ruby(wxr, arg)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.largs = new_args
    elif kind == NodeKind.HTML:
        # Keep attrs and args as-is, process children
        new_node = HTMLNode(new_node.loc)
        new_node.attrs = contents.attrs
        new_node.sarg = contents.sarg
        e1, c1 = extract_ruby(wxr, contents.children)
        extracted.extend(e1)
        new_node.children = c1
    else:
        raise RuntimeError(f"extract_ruby: unhandled kind {kind}")
    new_contents.append(new_node)
    return extracted, new_contents
