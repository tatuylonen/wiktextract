from collections import defaultdict
from typing import Dict, List


from wikitextprocessor import NodeKind, WikiNode
from wiktextract.extractor.de.utils import find_and_remove_child, match_senseid

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_examples(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        example_data = defaultdict(str)

        ref_nodes = find_and_remove_child(
            list_item_node,
            NodeKind.HTML,
            lambda html_node: html_node.tag == "ref",
        )
        for ref_node in ref_nodes:
            extract_reference(wxr, example_data, ref_node)

        example_text = clean_node(wxr, {}, list_item_node.children)

        senseid, example_text = match_senseid(example_text)

        if example_text:
            example_data["text"] = example_text

        if senseid:
            sense_data = [
                sense
                for sense in page_data[-1]["senses"]
                if sense["senseid"] == senseid
            ]

            for sense in sense_data:
                sense["examples"].append(example_data)

        else:
            if example_data:
                wxr.wtp.debug(
                    f"Found example data without senseid and text: {example_data}",
                    sortid="extractor/de/examples/extract_examples/28",
                )


def extract_reference(
    wxr: WiktextractContext, example_data: Dict[str, str], ref_node: WikiNode
):
    reference_data = defaultdict()

    reference_data["raw_ref"] = clean_node(wxr, {}, ref_node.children)

    template_nodes = list(ref_node.find_child(NodeKind.TEMPLATE))

    if len(template_nodes) > 1:
        wxr.wtp.debug(
            f"Found unexpected number of templates in example: {template_nodes}",
            sortid="extractor/de/examples/extract_examples/64",
        )
    elif len(template_nodes) == 1:
        template_node = template_nodes[0]

        # Sometimes the title is dynamically generated from the template name,
        # so we preset the title. If specified in the template, it will be
        # overwritten.
        reference_data["titel"] = template_node.largs[0][0].strip()

        for arg in template_node.largs[1:]:
            arg = clean_node(wxr, {}, arg)
            if not arg.strip():
                continue
            splits = arg.split("=", 1)
            if len(splits) != 2:
                continue
            arg_name, arg_value = arg.split("=", 1)
            if arg_name.strip() and arg_value.strip():
                reference_data[arg_name.lower()] = arg_value

    example_data["ref"] = reference_data
