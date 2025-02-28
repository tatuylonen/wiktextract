from itertools import count

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .tags import translate_raw_tags


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


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    l_type: str,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item, l_type)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    l_type: str,
) -> None:
    raw_tags = []
    linkages = []
    sense = ""
    for index, node in enumerate(list_item.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                linkages.append(Linkage(word=word))
        elif isinstance(node, TemplateNode):
            if node.template_name in ["qualifier", "q", "qual"]:
                raw_tag = clean_node(wxr, None, node).strip("()")
                if raw_tag != "":
                    raw_tags.append(raw_tag)
            elif node.template_name == "l":
                l_data = extract_l_template(wxr, node)
                if l_data.word != "":
                    linkages.append(l_data)
            elif node.template_name == "m":
                l_data = extract_m_template(wxr, node)
                if l_data.word != "":
                    linkages.append(l_data)
            elif node.template_name == "alter":
                linkages.extend(extract_alter_template(wxr, node))
        elif isinstance(node, str) and ":" in node:
            sense = clean_node(
                wxr,
                None,
                [node[node.index(":") + 1 :]] + list_item.children[index + 1 :],
            )

    for l_data in linkages:
        l_data.sense = sense
        l_data.raw_tags.extend(raw_tags)
        translate_raw_tags(l_data)

    if l_type == "forms":
        for l_data in linkages:
            if l_data.word == wxr.wtp.title:
                continue
            word_entry.forms.append(
                Form(
                    form=l_data.word, raw_tags=l_data.raw_tags, tags=l_data.tags
                )
            )
    else:
        getattr(word_entry, l_type).extend(linkages)


def extract_l_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> Linkage:
    return Linkage(
        word=clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    )


def extract_m_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> Linkage:
    l_data = Linkage(
        word=clean_node(
            wxr,
            None,
            t_node.template_parameters.get(
                3, t_node.template_parameters.get(2, "")
            ),
        ),
        roman=clean_node(wxr, None, t_node.template_parameters.get("t", "")),
    )
    return l_data


def extract_alter_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Linkage]:
    l_list = []
    for index in count(2):
        if index not in t_node.template_parameters:
            break
        word = clean_node(wxr, None, t_node.template_parameters[index])
        if word != "":
            l_list.append(Linkage(word=word))
    return l_list
