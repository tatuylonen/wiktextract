import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode, WikiNodeChildrenList
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import AltForm, Sense, WordEntry
from .sense_data import process_sense_data_list
from .tags import translate_raw_tags


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
) -> None:
    for list_item in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_data = Sense()

        definition: WikiNodeChildrenList = []
        other: WikiNodeChildrenList = []

        if not list_item.definition:
            continue

        for node in list_item.definition:
            if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                other.append(node)
            else:
                definition.append(node)
            if isinstance(node, TemplateNode) and node.template_name.startswith(
                ("f.", "forma ")
            ):
                process_forma_template(wxr, gloss_data, node)

        gloss = clean_node(wxr, gloss_data, definition)
        if len(gloss) > 0:
            gloss_data.glosses.append(gloss)

        gloss_note = clean_node(wxr, gloss_data, list_item.children)
        match = re.match(r"^(\d+)", gloss_note)
        if match is not None:
            gloss_data.senseid = match.group(1)
            tag_string = gloss_note[len(match.group(1)) :].strip()
        else:
            tag_string = gloss_note.strip()

        # split tags by comma or "y"
        tags = re.split(r",|y", tag_string)
        for tag in tags:
            tag = (
                tag.strip()
                .removesuffix(".")
                .removesuffix("Main")
                .removeprefix("Main")
            )
            if tag:
                gloss_data.raw_tags.append(tag)

        translate_raw_tags(gloss_data)
        page_data[-1].senses.append(gloss_data)
        if len(other) > 0:
            for node in other:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                    process_sense_data_list(wxr, page_data[-1], node)
                else:
                    wxr.wtp.debug(
                        f"Found nodes that are not part of definition: {node}",
                        sortid="extractor/es/gloss/extract_gloss/46",
                    )


def process_uso_template(
    wxr: WiktextractContext, sense: Sense, template: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:uso
    from .tags import USO_TAGS

    for arg_name, arg_value in template.template_parameters.items():
        if isinstance(arg_name, int):
            arg_value = clean_node(wxr, None, arg_value)
            if arg_value in USO_TAGS:
                tr_tags = USO_TAGS[arg_value]
                if isinstance(tr_tags, str):
                    sense.tags.append(USO_TAGS[arg_value])
                elif isinstance(tr_tags, list):
                    sense.tags.extend(USO_TAGS[arg_value])
            else:
                sense.raw_tags.append(arg_value)

    clean_node(wxr, sense, template)  # save category links


def process_ambito_template(
    wxr: WiktextractContext, sense: Sense, template: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:ámbito
    # location data
    from .tags import AMBITO_TAGS

    for arg_name, arg_value in template.template_parameters.items():
        if isinstance(arg_name, int):
            arg_value = clean_node(wxr, None, arg_value)
            if arg_value in AMBITO_TAGS:
                tr_tags = AMBITO_TAGS[arg_value]
                if isinstance(tr_tags, str):
                    sense.tags.append(AMBITO_TAGS[arg_value])
                elif isinstance(tr_tags, list):
                    sense.tags.extend(tr_tags)

    clean_node(wxr, sense, template)  # save category links


def process_forma_template(
    wxr: WiktextractContext, sense: Sense, template: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:forma_verbo
    form_of = clean_node(wxr, None, template.template_parameters.get(1, ""))
    if form_of != "":
        sense.form_of.append(AltForm(word=form_of))
        if (
            "pronominal" in template.template_parameters
            or "pronom" in template.template_parameters
        ):
            sense.form_of.append(AltForm(word=form_of + "se"))
