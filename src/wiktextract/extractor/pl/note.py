import re
from collections import defaultdict

from wikitextprocessor.parser import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_note_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    from .page import match_sense_index

    notes = defaultdict(list)
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_note_list_item(wxr, list_item, notes)
    for data in page_data:
        if data.lang_code == base_data.lang_code:
            for sense in data.senses:
                sense.notes.extend(notes.get("", []))
                for sense_index in notes.keys():
                    if match_sense_index(sense_index, sense):
                        sense.notes.extend(notes[sense_index])


def process_note_list_item(
    wxr: WiktextractContext, list_item: WikiNode, notes: dict[str, list[str]]
) -> None:
    sense_index = ""
    note_nodes = []
    for node in list_item.children:
        if isinstance(node, str):
            m = re.search(r"\([\d\s,-.]+\)", node)
            if m is not None:
                sense_index = m.group(0).strip("()")
                note_nodes.append(node[m.end() :])
            else:
                note_nodes.append(node)
        else:
            note_nodes.append(node)
    note_text = clean_node(wxr, None, note_nodes)
    if len(note_text) > 0:
        notes[sense_index].append(note_text)
