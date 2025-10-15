import re
from collections import defaultdict

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .etymology import ATTESTATION_TEMPLATES, extract_date_template
from .models import AltForm, AttestationData, Example, Sense, WordEntry
from .tags import translate_raw_tags


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    parent_sense: Sense | None = None,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = list(
            list_item_node.invert_find_child(
                NodeKind.LIST, include_empty_str=True
            )
        )
        gloss_data = (
            parent_sense.model_copy(deep=True)
            if parent_sense is not None
            else Sense()
        )
        gloss_data.examples.clear()
        # process modifier, theme tempaltes before gloss text
        # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles/Précisions_de_sens
        tag_indexes = set()
        for index, gloss_node in enumerate(gloss_nodes):
            if (
                isinstance(gloss_node, TemplateNode)
                and gloss_node.template_name in ATTESTATION_TEMPLATES
            ):
                gloss_data.attestations = extract_date_template(
                    wxr, gloss_data, gloss_node
                )
                tag_indexes.add(index)
            elif (
                isinstance(gloss_node, TemplateNode)
                and gloss_node.template_name != "équiv-pour"
            ):
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
        gloss_text = find_alt_of_form(
            wxr, gloss_only_nodes[:note_index], page_data[-1], gloss_data
        )
        if "form-of" in page_data[-1].tags:
            find_form_of_word(wxr, gloss_only_nodes[:note_index], gloss_data)
        gloss_text = gloss_text.strip("— \n")
        if gloss_text != "":
            gloss_data.glosses.append(gloss_text)
        gloss_data.note = clean_node(
            wxr, gloss_data, gloss_only_nodes[note_index + 1 :]
        ).strip(" ().")
        if len(gloss_data.glosses) > 0:
            page_data[-1].senses.append(gloss_data)

        for nest_gloss_list in list_item_node.find_child(NodeKind.LIST):
            if nest_gloss_list.sarg.endswith("#"):
                extract_gloss(wxr, page_data, nest_gloss_list, gloss_data)
            elif nest_gloss_list.sarg.endswith("*"):
                for e_list_item in nest_gloss_list.find_child(
                    NodeKind.LIST_ITEM
                ):
                    extract_example_list_item(wxr, gloss_data, e_list_item)

        translate_raw_tags(gloss_data)


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
):
    has_exemple_template = False
    e_data = Example()
    e_nodes = []
    raw_tags = []
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name.endswith("exemple"):
                process_exemple_template(wxr, node, sense, raw_tags=raw_tags)
                has_exemple_template = True
            elif node.template_name == "source":
                e_data.ref = clean_node(wxr, sense, node).strip("— ()")
            else:
                t_text = clean_node(wxr, sense, node)
                if t_text.startswith("(") and t_text.endswith(")"):
                    raw_tags.append(t_text.strip("() "))
                else:
                    e_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for tr_item in node.find_child(NodeKind.LIST_ITEM):
                e_data.translation = clean_node(wxr, None, tr_item.children)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(tr_item.children)),
                    e_data.translation,
                    e_data,
                    "bold_translation_offsets",
                )
        else:
            e_nodes.append(node)

    if not has_exemple_template:
        e_data.text = clean_node(wxr, sense, e_nodes)
        if e_data.text != "":
            e_data.raw_tags.extend(raw_tags)
            translate_raw_tags(e_data)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(e_nodes)),
                e_data.text,
                e_data,
                "bold_text_offsets",
            )
            sense.examples.append(e_data)


def process_exemple_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    gloss_data: Sense | None,
    attestations: list[AttestationData] = [],
    raw_tags: list[str] = [],
) -> Example:
    # https://fr.wiktionary.org/wiki/Modèle:exemple
    # https://fr.wiktionary.org/wiki/Modèle:ja-exemple
    # https://fr.wiktionary.org/wiki/Modèle:zh-exemple
    text_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get(1, ""))
    )
    text = clean_node(wxr, None, text_arg)
    trans_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(
            node.template_parameters.get(
                2, node.template_parameters.get("sens", "")
            )
        )
    )
    translation = clean_node(wxr, None, trans_arg)
    roman_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(
            node.template_parameters.get(
                3, node.template_parameters.get("tr", "")
            )
        )
    )
    transcription = clean_node(wxr, None, roman_arg)
    source = clean_node(wxr, None, node.template_parameters.get("source", ""))
    example_data = Example(
        text=text,
        translation=translation,
        roman=transcription,
        ref=source,
        attestations=attestations,
        raw_tags=raw_tags,
    )
    calculate_bold_offsets(
        wxr, text_arg, text, example_data, "bold_text_offsets"
    )
    calculate_bold_offsets(
        wxr, trans_arg, translation, example_data, "bold_translation_offsets"
    )
    calculate_bold_offsets(
        wxr, roman_arg, transcription, example_data, "bold_roman_offsets"
    )
    if len(example_data.text) > 0 and isinstance(gloss_data, Sense):
        gloss_data.examples.append(example_data)
    if gloss_data is not None:
        clean_node(wxr, gloss_data, node)
    translate_raw_tags(example_data)
    return example_data


def find_alt_of_form(
    wxr: WiktextractContext,
    gloss_nodes: list[str | WikiNode],
    word_entry: WordEntry,
    gloss_data: Sense,
) -> str:
    """
    Return gloss text, remove tag template expanded from "variante *" templates.
    """
    from .form_line import process_equiv_pour_template

    alt_of = ""
    filtered_gloss_nodes = []
    for gloss_node in gloss_nodes:
        # https://fr.wiktionary.org/wiki/Modèle:variante_de
        # https://fr.wiktionary.org/wiki/Modèle:variante_kyujitai_de
        if isinstance(
            gloss_node, TemplateNode
        ) and gloss_node.template_name.startswith("variante "):
            alt_of = clean_node(
                wxr, None, gloss_node.template_parameters.get("dif", "")
            )
            if len(alt_of) == 0:
                alt_of = clean_node(
                    wxr, None, gloss_node.template_parameters.get(1, "")
                )
            if len(alt_of) > 0:
                gloss_data.alt_of.append(AltForm(word=alt_of))
                gloss_data.tags.append("alt-of")
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_node),
                pre_expand=True,
                additional_expand={gloss_node.template_name},
            )
            for node in expanded_template.children:
                if (
                    isinstance(node, TemplateNode)
                    and node.template_name == "désuet"
                ):
                    raw_tag = clean_node(wxr, gloss_data, node).strip(" ()")
                    gloss_data.raw_tags.append(raw_tag)
                else:
                    filtered_gloss_nodes.append(node)
        elif (
            isinstance(gloss_node, TemplateNode)
            and gloss_node.template_name == "équiv-pour"
        ):
            for form_data in process_equiv_pour_template(wxr, gloss_node, []):
                form_data.sense_index = len(word_entry.senses) + 1
                word_entry.forms.append(form_data)
        else:
            filtered_gloss_nodes.append(gloss_node)

    if alt_of == "" and word_entry.pos == "typographic variant":
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
            if "alt-of" not in gloss_data.tags:
                gloss_data.tags.append("alt-of")

    gloss_text = clean_node(wxr, gloss_data, filtered_gloss_nodes)
    gloss_text = re.sub(r"\s+\.$", ".", gloss_text)
    brackets = 0
    for char in gloss_text:
        if char == "(":
            brackets += 1
        elif char == ")":
            brackets -= 1
    if brackets != 0:
        gloss_text = gloss_text.strip(" ()")
    return gloss_text


def find_form_of_word(
    wxr: WiktextractContext,
    gloss_nodes: list[str | WikiNode],
    gloss_data: Sense,
) -> None:
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_variantes
    form_of = ""
    for node in gloss_nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            form_of = clean_node(wxr, None, node)
        elif isinstance(node, TemplateNode):
            if node.template_name in ("mutation de", "lien"):
                # https://fr.wiktionary.org/wiki/Modèle:mutation_de
                form_of = clean_node(
                    wxr, None, node.template_parameters.get(1, "")
                )
    if len(form_of) > 0:
        gloss_data.form_of.append(AltForm(word=form_of))
        if "form-of" not in gloss_data.tags:
            gloss_data.tags.append("form-of")
