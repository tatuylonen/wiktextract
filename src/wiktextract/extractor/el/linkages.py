import re

from wikitextprocessor import TemplateNode, WikiNode
from wikitextprocessor.parser import NodeKind

from wiktextract.extractor.el.tags import translate_raw_tags
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Form, Linkage, WordEntry
from .section_titles import Heading

Node = str | WikiNode

LINK_RE = re.compile(r"(__/?[IL]__)")

EXAMPLES_RE = re.compile(r"(?sm)__E__(.*?)__/E__")


def process_linkage_section(
    wxr: WiktextractContext,
    data: WordEntry,
    rnode: WikiNode,
    linkage_type: Heading,
) -> None:
    transliteration_template_data: list[Form] = []

    def prehandle_templates_fn(
        node: WikiNode,
    ) -> list[Node] | None:
        """Handle nodes in the parse tree specially."""
        # print(f"{node=}")
        if not isinstance(node, TemplateNode):
            return None
        if node.template_name == "βλ":
            # print("REACHED")
            # print(f"{node.largs=}")
            ret: list[Node] = []
            # print(f"{ret=}")
            comma = False
            for arg in node.largs[1:]:
                if comma:
                    ret.append(", ")
                ret.append("__L__")
                ret.append(wxr.wtp.node_to_text(arg))
                ret.append("__/L__")
                comma = True
            return ret
        if node.template_name in ("eo-h", "eo-x"):
            transliteration_template_data.append(
                Form(
                    form="".join(
                        wxr.wtp.node_to_text(arg) for arg in node.largs[1]
                    ),
                    raw_tags=[
                        "H-sistemo"
                        if node.template_name == "eo-h"
                        else "X-sistemo"
                    ],
                    tags=["transliteration"],
                    source="linkage",
                )
            )
            return []
        return None

    def links_node_fn(
        node: WikiNode,
    ) -> list[Node] | None:
        """Handle nodes in the parse tree specially."""
        # print(f"{node=}")
        if node.kind == NodeKind.ITALIC:
            return ["__I__", *node.children, "__/I__"]
        if node.kind == NodeKind.LINK:
            if not isinstance(node.largs[0][0], str):
                return None
            return [
                "__L__",
                # unpacking a list-comprehension, unpacking into a list
                # seems to be more performant than adding lists together.
                *(
                    wxr.wtp.node_to_text(
                        node.largs[1:2] or node.largs[0],
                    )
                    # output the "visible" half of the link.
                ),
                # XXX collect link data if it turns out to be important.
                "__/L__",
            ]
            # print(f"{node.largs=}")
        if isinstance(node, TemplateNode) and node.template_name == "βλ":
            # print("REACHED")
            # print(f"{node=}")
            return node.children
        if node.kind == NodeKind.LIST_ITEM and node.sarg.endswith(":"):
            return [node.sarg, "__E__", *node.children, "__/E__\n"]
        return None

    # parse nodes to get lists and list_items
    reparsed = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(rnode, node_handler_fn=prehandle_templates_fn),
        expand_all=True,
    )

    combined_line_data: list[tuple[list[str], list[str], list[str]]] = []

    for list_item in reparsed.find_child_recursively(NodeKind.LIST_ITEM):
        # print(f"{list_item=}")
        text = wxr.wtp.node_to_text(list_item, node_handler_fn=links_node_fn)

        chained_links: list[str] = []
        line_tags: list[str] = []
        inside_link = False
        inside_italics = False
        interrupted_link = False

        examples = []
        for m in EXAMPLES_RE.finditer(text):
            example = re.sub(r"__/?[IL]__", "", m.group(1))
            parsed = wxr.wtp.parse(example)
            example = clean_node(wxr, None, parsed)
            example = example.strip(" \n*:⮡")
            examples.append(example)

        text = EXAMPLES_RE.sub("", text)

        for i, token in enumerate(LINK_RE.split(text)):
            # print(f"{token=}")
            token = token.strip()

            if not token:
                continue

            if i % 2 == 0:
                # Actual text, not __L__or __/L__
                # print(f"{i=}, {token=}, {line_tags=}")
                if inside_italics:
                    line_tags.append(token)
                    continue
                if inside_link is False and token:
                    # There's something between two link nodes
                    interrupted_link = True
                    continue
                if inside_link is True:
                    if interrupted_link is True and len(chained_links) > 0:
                        combined_line_data.append(
                            (chained_links, line_tags, examples)
                        )
                        chained_links = [token]
                    else:
                        chained_links.append(token)
                    continue
            if token == "__I__":
                inside_italics = True
                continue
            if token == "__/I__":
                inside_italics = False
                continue
            if token == "__L__":
                inside_link = True
                continue
            if token == "__/L__":
                inside_link = False
                interrupted_link = False
                continue
        if chained_links:
            combined_line_data.append((chained_links, line_tags, examples))

    new_combined = []
    for link_parts, tags, examples in combined_line_data:
        if link_parts:
            new_combined.append((link_parts, tags, examples))
    combined_line_data = new_combined

    match linkage_type:
        case Heading.Related:
            target_field = data.related
        case Heading.Synonyms:
            target_field = data.synonyms
        case Heading.Antonyms:
            target_field = data.antonyms
        case Heading.Derived:
            target_field = data.derived
        case Heading.Transliterations:
            # For transliteration sections we add these to forms instead.
            transliteration_forms = [
                Form(
                    form=" ".join(link_parts),
                    raw_tags=ltags,
                    tags=["transliteration"],
                    source="linkage",
                )
                for link_parts, ltags, _ in combined_line_data
            ]
            for form in transliteration_forms:
                translate_raw_tags(form)
            data.forms.extend(transliteration_forms)
            if transliteration_template_data:
                data.forms.extend(transliteration_template_data)
            return
        case _:
            wxr.wtp.error(
                "process_linkage_section() given unhandled Heading: "
                f"{linkage_type=}",
                sortid="linkages/83",
            )
            return

    linkages = [
        Linkage(word=" ".join(link_parts), raw_tags=ltags, examples=lexamples)
        for link_parts, ltags, lexamples in combined_line_data
    ]
    for linkage in linkages:
        translate_raw_tags(linkage)
    target_field.extend(linkages)

    # iterate over list item lines and get links

    # if links are next to each other with only whitespace between,
    # that's part of one entry

    # if there's something that isn't a link in-between, then they're
    # separate words
