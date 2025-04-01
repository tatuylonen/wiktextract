from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in ["ARchar", "Arab", "PSchar", "SDchar"]:
            word = clean_node(wxr, None, t_node)
            if word != "":
                word_entry.forms.append(Form(form=word, tags=tags))
