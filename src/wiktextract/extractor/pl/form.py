import re

from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_zapis_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    # get around "preformatted" node
    for node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if node.template_name == "ptrad":
            form_text = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            if form_text != "":
                base_data.forms.append(
                    Form(form=form_text, tags=["Traditional Chinese"])
                )


def extract_transliteracja_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\([\d\s,-.]+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
                    roman = node[m.end() :].strip()
                    if roman != "":
                        base_data.forms.append(
                            Form(
                                form=roman,
                                sense_index=sense_index,
                                tags=["transliteration"],
                            )
                        )
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name == "translit":
            roman = clean_node(wxr, None, t_node)
            if roman != "":
                base_data.forms.append(
                    Form(form=roman, tags=["transliteration"])
                )
