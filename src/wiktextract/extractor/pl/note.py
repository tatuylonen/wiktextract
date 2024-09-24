import re
from typing import Optional

from wikitextprocessor import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Note, WordEntry


def extract_note_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    from .page import match_sense_index

    notes = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        note = process_note_list_item(wxr, list_item)
        if note is not None:
            notes.append(note)
    for data in page_data:
        if data.lang_code == base_data.lang_code:
            for note in notes:
                if note.sense_index == "" or match_sense_index(
                    note.sense_index, data
                ):
                    data.notes.append(note)


def process_note_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> Optional[Note]:
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
        return Note(sense_index=sense_index, text=note_text)
    return None
