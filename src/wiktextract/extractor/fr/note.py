from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_note(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
) -> None:
    # Save paragraph and list item texts to a list of string.
    note_paragraph_nodes = []
    for child in level_node.children:
        if isinstance(child, TemplateNode) and child.template_name.startswith(
            "note-"
        ):
            process_note_template(wxr, page_data, child)
            continue
        if isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            for list_item_node in child.find_child(NodeKind.LIST_ITEM):
                note_text = clean_node(
                    wxr, page_data[-1], list_item_node.children
                )
                if len(note_text) > 0:
                    page_data[-1].notes.append(note_text)
            continue

        note_paragraph_nodes.append(child)
        if isinstance(child, str) and child.endswith("\n"):
            note_text = clean_node(wxr, page_data[-1], note_paragraph_nodes)
            if len(note_text) > 0:
                page_data[-1].notes.append(note_text)
            note_paragraph_nodes.clear()


def process_note_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    template_node: TemplateNode,
) -> None:
    expaned_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    extract_note(wxr, page_data, expaned_template)


def extract_recognition_rate_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
) -> None:
    for node in level_node.find_child(NodeKind.TEMPLATE):
        if node.template_name == "nl-taux":
            # https://fr.wiktionary.org/wiki/Modèle:nl-taux
            # save Dutch vocabulary recognition rate category links
            clean_node(wxr, word_entry, node)
