import re
from collections import defaultdict
from typing import Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import AltForm, Example, Sense, WordEntry
from .tags import translate_raw_tags


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    parent_glosses: list[str] = [],
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = list(
            list_item_node.invert_find_child(
                NodeKind.LIST, include_empty_str=True
            )
        )
        gloss_data = Sense()
        # process modifier, theme tempaltes before gloss text
        # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles/Précisions_de_sens
        tag_indexes = set()
        for index, gloss_node in enumerate(gloss_nodes):
            if isinstance(gloss_node, TemplateNode):
                categories_data = defaultdict(list)
                expanded_text = clean_node(wxr, categories_data, gloss_node)
                if (
                    expanded_text.startswith("(")
                    and expanded_text.endswith(")")
                    and "(" not in expanded_text[1:-1]
                ):
                    tags = expanded_text.strip("() \n").split(", ")
                    if len(tags) > 0:
                        gloss_data.raw_tags.extend(tags)
                    if "categories" in categories_data:
                        gloss_data.categories.extend(
                            categories_data["categories"]
                        )
                    tag_indexes.add(index)
            # if an italic node is between parentheses then it's a tag, also
            # don't add the parenthese strings to `gloss_only_nodes`
            elif (
                isinstance(gloss_node, WikiNode)
                and gloss_node.kind == NodeKind.ITALIC
                and isinstance(gloss_nodes[index - 1], str)
                and gloss_nodes[index - 1].strip() == "("
                and index + 1 < len(gloss_nodes)
                and isinstance(gloss_nodes[index + 1], str)
                and gloss_nodes[index + 1].strip() == ")"
            ):
                gloss_data.raw_tags.append(clean_node(wxr, None, gloss_node))
                tag_indexes |= {index - 1, index, index + 1}

        gloss_only_nodes = [
            node
            for index, node in enumerate(gloss_nodes)
            if index not in tag_indexes
        ]
        note_index = len(gloss_only_nodes)
        for index in range(note_index):
            if (
                isinstance(gloss_only_nodes[index], TemplateNode)
                and gloss_only_nodes[index].template_name == "note"
            ):
                note_index = index
        find_alt_of_form(
            wxr, gloss_only_nodes[:note_index], page_data[-1].pos, gloss_data
        )
        if "form-of" in page_data[-1].tags:
            find_form_of_word(wxr, gloss_only_nodes[:note_index], gloss_data)
        gloss_text = clean_node(wxr, gloss_data, gloss_only_nodes[:note_index])
        if not (gloss_text.startswith("(") and gloss_text.endswith(")")):
            gloss_text = gloss_text.strip(" ()")
        gloss_data.glosses = parent_glosses + [gloss_text]
        gloss_data.note = clean_node(
            wxr, gloss_data, gloss_only_nodes[note_index + 1 :]
        ).strip(" ().")
        page_data[-1].senses.append(gloss_data)
        for nest_gloss_list in list_item_node.find_child(NodeKind.LIST):
            if nest_gloss_list.sarg.endswith("#"):
                extract_gloss(
                    wxr, page_data, nest_gloss_list, gloss_data.glosses
                )
            elif nest_gloss_list.sarg.endswith("*"):
                extract_examples(wxr, gloss_data, nest_gloss_list)
        translate_raw_tags(gloss_data)


def extract_examples(
    wxr: WiktextractContext,
    gloss_data: Sense,
    example_list_node: WikiNode,
) -> None:
    for example_node in example_list_node.find_child(NodeKind.LIST_ITEM):
        example_node_children = list(example_node.filter_empty_str_child())
        if len(example_node_children) == 0:
            continue
        first_child = example_node_children[0]
        if (
            isinstance(first_child, WikiNode)
            and first_child.kind == NodeKind.TEMPLATE
            and first_child.template_name == "exemple"
        ):
            process_exemple_template(wxr, first_child, gloss_data)
        else:
            example_data = Example()
            ignored_nodes = []
            for node in example_node.find_child(
                NodeKind.TEMPLATE | NodeKind.LIST
            ):
                if (
                    node.kind == NodeKind.TEMPLATE
                    and node.template_name == "source"
                ):
                    example_data.ref = clean_node(wxr, None, node).strip("— ()")
                    ignored_nodes.append(node)
                elif node.kind == NodeKind.LIST:
                    for tr_item in node.find_child(NodeKind.LIST_ITEM):
                        example_data.translation = clean_node(
                            wxr, None, tr_item.children
                        )
                    ignored_nodes.append(node)
            example_nodes = [
                node
                for node in example_node_children
                if node not in ignored_nodes
            ]
            example_data.text = clean_node(wxr, None, example_nodes)
            gloss_data.examples.append(example_data)


def process_exemple_template(
    wxr: WiktextractContext, node: TemplateNode, gloss_data: Sense
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:exemple
    # https://fr.wiktionary.org/wiki/Modèle:ja-exemple
    # https://fr.wiktionary.org/wiki/Modèle:zh-exemple
    text = clean_node(wxr, None, node.template_parameters.get(1, ""))
    translation = clean_node(
        wxr,
        None,
        node.template_parameters.get(
            2, node.template_parameters.get("sens", "")
        ),
    )
    transcription = clean_node(
        wxr,
        None,
        node.template_parameters.get(3, node.template_parameters.get("tr", "")),
    )
    source = clean_node(wxr, None, node.template_parameters.get("source", ""))
    example_data = Example(
        text=clean_node(wxr, None, text),
        translation=clean_node(wxr, None, translation),
        roman=clean_node(wxr, None, transcription),
        ref=clean_node(wxr, None, source),
    )
    if len(example_data.text) > 0:
        gloss_data.examples.append(example_data)


def find_alt_of_form(
    wxr: WiktextractContext,
    gloss_nodes: list[Union[str, WikiNode]],
    pos_type: str,
    gloss_data: Sense,
):
    alt_of = ""
    for template_node in filter(
        lambda n: isinstance(n, TemplateNode), gloss_nodes
    ):
        # https://fr.wiktionary.org/wiki/Modèle:variante_de
        # https://fr.wiktionary.org/wiki/Modèle:variante_kyujitai_de
        if re.fullmatch(r"variante \w*\s*de", template_node.template_name):
            alt_of = clean_node(
                wxr, None, template_node.template_parameters.get("dif", "")
            )
            if len(alt_of) == 0:
                alt_of = clean_node(
                    wxr, None, template_node.template_parameters.get(1, "")
                )
            if len(alt_of) > 0:
                gloss_data.alt_of.append(AltForm(word=alt_of))
                gloss_data.tags.append("alt-of")

    if alt_of == "" and pos_type == "typographic variant":
        for gloss_node in filter(
            lambda n: isinstance(n, WikiNode), gloss_nodes
        ):
            # use the last link
            if gloss_node.kind == NodeKind.LINK:
                alt_of = clean_node(wxr, None, gloss_node)
            if isinstance(gloss_node, TemplateNode):
                gloss_node = wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(gloss_node), expand_all=True
                )
            for link in gloss_node.find_child_recursively(NodeKind.LINK):
                alt_of = clean_node(wxr, None, link)
        if len(alt_of) > 0:
            gloss_data.alt_of.append(AltForm(word=alt_of))


def find_form_of_word(
    wxr: WiktextractContext,
    gloss_nodes: list[Union[str, WikiNode]],
    gloss_data: Sense,
) -> None:
    form_of = ""
    for node in gloss_nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            form_of = clean_node(wxr, None, node)
    if len(form_of) > 0:
        gloss_data.form_of.append(AltForm(word=form_of))
