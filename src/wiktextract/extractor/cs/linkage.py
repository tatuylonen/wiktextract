from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .tags import translate_raw_tags


def extract_alt_form_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            for node in list_item.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "":
                        form = Form(
                            form=word, tags=["alternative"], raw_tags=raw_tags
                        )
                        translate_raw_tags(form)
                        base_data.forms.append(form)
                        raw_tags.clear()
                elif (
                    isinstance(node, TemplateNode)
                    and node.template_name == "Příznak2"
                ):
                    from .sound import extract_příznak2_template

                    raw_tags.extend(extract_příznak2_template(wxr, node))


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
):
    l_list = []
    sense_index = 0
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            if list_item.sarg == "#":
                sense_index += 1
            l_list.extend(
                extract_linkage_list_item(wxr, list_item, sense_index)
            )
    getattr(word_entry, linkage_type).extend(l_list)


def extract_linkage_list_item(
    wxr: WiktextractContext, list_item: WikiNode, sense_index: int
) -> list[Linkage]:
    l_list = []
    raw_tags = []
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "Příznak2":
            from .sound import extract_příznak2_template

            raw_tags.extend(extract_příznak2_template(wxr, node))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                l_data = Linkage(
                    word=word, raw_tags=raw_tags, sense_index=sense_index
                )
                translate_raw_tags(l_data)
                l_list.append(l_data)
                raw_tags.clear()

    return l_list
