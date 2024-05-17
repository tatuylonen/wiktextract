from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, WordEntry
from .utils import find_and_remove_child, match_senseid

REF_KEY_MAP = {
    "autor": "author",
    "a": "author",
    "titel": "title",
    "titelerg": "title_complement",
    "auflage": "edition",
    "verlag": "publisher",
    "ort": "place",
    "jahr": "year",
    "seiten": "pages",
    "isbn": "isbn",
    "übersetzer": "translator",
    "herausgeber": "editor",
    "sammelwerk": "collection",
    "werk": "collection",
    "band": "volume",
    "kommentar": "comment",
    "online": "url",
    "tag": "day",
    "monat": "month",
    "zugriff": "accessdate",
    "nummer": "number",
    "datum": "date",
    "hrsg": "editor",
}


def extract_examples(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
            example_data = Example()

            ref_nodes = find_and_remove_child(
                list_item_node,
                NodeKind.HTML,
                lambda html_node: html_node.tag == "ref",
            )
            for ref_node in ref_nodes:
                extract_reference(wxr, example_data, ref_node)

            example_text = clean_node(wxr, None, list_item_node.children)

            senseid, example_text = match_senseid(example_text)

            if len(example_text) > 0:
                example_data.text = example_text
                if len(senseid) > 0:
                    for sense in word_entry.senses:
                        if sense.senseid == senseid:
                            sense.examples.append(
                                example_data.model_copy(deep=True)
                            )
                else:
                    wxr.wtp.debug(
                        f"Found example data without senseid: {example_data}",
                        sortid="extractor/de/examples/extract_examples/28",
                    )

    for non_list_node in level_node.invert_find_child(NodeKind.LIST):
        wxr.wtp.debug(
            f"Found unexpected non-list node in examples: {non_list_node}",
            sortid="extractor/de/examples/extract_examples/33",
        )


def extract_reference(
    wxr: WiktextractContext, example_data: Example, ref_node: WikiNode
):
    example_data.raw_ref = clean_node(wxr, None, ref_node.children)

    template_nodes = list(ref_node.find_child(NodeKind.TEMPLATE))

    if len(template_nodes) > 1:
        wxr.wtp.debug(
            f"Found unexpected number of templates in example: {template_nodes}",
            sortid="extractor/de/examples/extract_examples/64",
        )
    elif len(template_nodes) == 1:
        template_node = template_nodes[0]

        # Most reference templates follow the Literatur template and use named
        # parameters. We extract them here.
        # https://de.wiktionary.org/wiki/Vorlage:Literatur
        for key, value in template_node.template_parameters.items():
            if isinstance(key, str):
                key_english = REF_KEY_MAP.get(key.lower(), key.lower())
                if key_english in example_data.model_fields:
                    setattr(
                        example_data, key_english, clean_node(wxr, {}, value)
                    )
                else:
                    wxr.wtp.debug(
                        f"Unexpected key in reference: {key_english}",
                        sortid="extractor/de/examples/extract_examples/77",
                    )

        # XXX: Treat other templates as well.
        # E.g. https://de.wiktionary.org/wiki/Vorlage:Ref-OWID
