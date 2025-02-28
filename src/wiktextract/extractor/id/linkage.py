from itertools import count

from wikitextprocessor import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_syn_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    l_type: str,
) -> None:
    for index in count(2):
        if index not in t_node.template_parameters:
            break
        word = clean_node(wxr, None, t_node.template_parameters[index])
        if word != "":
            getattr(word_entry, l_type).append(
                Linkage(
                    word=word,
                    sense=word_entry.senses[-1].glosses[0]
                    if len(word_entry.senses) > 0
                    and len(word_entry.senses[-1].glosses) > 0
                    else "",
                )
            )
