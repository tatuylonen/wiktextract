from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .linkage import process_linkage_list_item
from .models import Example, Sense, WordEntry
from .section_titles import LINKAGES


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
    parent_list_text: str = "",
) -> None:
    # https://ja.wiktionary.org/wiki/Wiktionary:用例#用例を示す形式

    # check if it's linkage data
    for node_idx, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node:
            linkage_type_text = clean_node(
                wxr, None, list_item.children[:node_idx]
            )
            if linkage_type_text in LINKAGES:
                process_linkage_list_item(
                    wxr,
                    word_entry,
                    list_item,
                    "",
                    sense.glosses[0] if len(sense.glosses) > 0 else "",
                )
                return

    if any(
        child.contain_node(NodeKind.BOLD) or child.kind == NodeKind.BOLD
        for child in list_item.children
        if isinstance(child, WikiNode) and child.kind != NodeKind.LIST
    ) or not list_item.contain_node(NodeKind.LIST):
        # has bold node or doesn't have list child node
        has_example_template = False
        for t_node in list_item.find_child(NodeKind.TEMPLATE):
            if t_node.template_name in ["ux", "uxi"]:
                process_ux_template(wxr, t_node, sense)
                has_example_template = True
        if has_example_template:
            return

        expanded_nodes = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                list(list_item.invert_find_child(NodeKind.LIST))
            ),
            expand_all=True,
        )
        ruby, no_ruby = extract_ruby(wxr, expanded_nodes.children)
        example = Example(text=clean_node(wxr, None, no_ruby), ruby=ruby)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(no_ruby)),
            example.text,
            example,
            "bold_text_offsets",
        )
        for tr_list_item in list_item.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            example.translation = clean_node(wxr, None, tr_list_item.children)
        if len(parent_list_text) > 0:
            example.ref = parent_list_text
        else:
            for ref_start_str in ["（", "――"]:
                if ref_start_str in example.text:
                    ref_start = example.text.rindex(ref_start_str)
                    example.ref = example.text[ref_start:]
                    example.text = example.text[:ref_start].strip()
                    for ref_tag in expanded_nodes.find_html_recursively("ref"):
                        example.ref += " " + clean_node(
                            wxr, None, ref_tag.children
                        )
                    break
        sense.examples.append(example)
    else:
        list_item_text = clean_node(
            wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
        )
        for ref_tag in list_item.find_html("ref"):
            list_item_text += " " + clean_node(wxr, None, ref_tag.children)
        for next_list_item in list_item.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            extract_example_list_item(
                wxr, word_entry, sense, next_list_item, list_item_text
            )


def process_ux_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: Sense
) -> None:
    # https://ja.wiktionary.org/wiki/テンプレート:ux
    # https://ja.wiktionary.org/wiki/テンプレート:uxi
    example = Example()
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for i_tag in expanded_node.find_html_recursively("i"):
        i_tag_class = i_tag.attrs.get("class", "")
        if "e-example" in i_tag_class:
            example.text = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, example.text, example, "bold_text_offsets"
            )
        elif "e-transliteration" in i_tag_class:
            example.roman = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, example.roman, example, "bold_roman_offsets"
            )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_tag_class = span_tag.attrs.get("class", "")
        if "e-translation" in span_tag_class:
            example.translation = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example.translation,
                example,
                "bold_translation_offsets",
            )
    if example.text != "":
        sense.examples.append(example)
    clean_node(wxr, sense, t_node)
