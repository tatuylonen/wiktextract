import re

from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import AltForm, Sense, WordEntry
from .tags import GRAMMATICAL_TAGS, translate_raw_tags
from .utils import extract_sense_index


def extract_glosses(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    sense = Sense()
    section_title = clean_node(wxr, None, level_node.largs)
    for list_node in level_node.find_child(NodeKind.LIST):
        sense = process_gloss_list_item(
            wxr, word_entry, list_node, sense, section_title
        )

    if not level_node.contain_node(NodeKind.LIST):
        gloss_text = clean_node(wxr, sense, level_node.children)
        if len(gloss_text) > 0:
            sense.glosses.append(gloss_text)
            word_entry.senses.append(sense)


def process_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_node: WikiNode,
    parent_sense: Sense,
    section_title: str,
) -> Sense:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        item_type = list_item_node.sarg
        if (
            "form-of" in word_entry.tags
            or section_title == "Grammatische Merkmale"
        ):
            process_form_of_list_item(wxr, word_entry, list_item_node)
        elif item_type.endswith("*"):
            # only contains modifier template
            has_tag_template = False
            for template in list_item_node.find_child(NodeKind.TEMPLATE):
                raw_tag = clean_node(wxr, parent_sense, template).removesuffix(
                    ":"
                )
                parent_sense = Sense()
                parent_sense.raw_tags.append(raw_tag)
                has_tag_template = True
            if not has_tag_template:
                new_sense = Sense()
                gloss_text = clean_node(wxr, new_sense, list_item_node.children)
                if len(gloss_text) > 0:
                    new_sense.glosses.append(gloss_text)
                    word_entry.senses.append(new_sense)
        elif item_type.endswith(":"):
            sense_data = parent_sense.model_copy(deep=True)
            gloss_nodes = []
            for gloss_node in list_item_node.children:
                if isinstance(gloss_node, TemplateNode):
                    if gloss_node.template_name == "K":
                        for (
                            k_arg,
                            k_arg_value,
                        ) in gloss_node.template_parameters.items():
                            if k_arg == "ft":
                                gloss_nodes.append(
                                    clean_node(wxr, None, k_arg_value)
                                )
                                gloss_nodes.append(":")
                            elif isinstance(k_arg, int):
                                raw_tag = clean_node(wxr, None, k_arg_value)
                                if raw_tag != "von":
                                    sense_data.raw_tags.append(raw_tag)
                        clean_node(wxr, sense_data, gloss_node)
                    elif gloss_node.template_name.endswith("."):
                        raw_tag = clean_node(
                            wxr, sense_data, gloss_node
                        ).removesuffix(":")
                        sense_data.raw_tags.append(raw_tag)
                    elif gloss_node.template_name in (
                        "QS Herkunft",
                        "QS Bedeutungen",
                    ):
                        continue
                    else:
                        gloss_nodes.append(gloss_node)
                elif (
                    isinstance(gloss_node, WikiNode)
                    and gloss_node.kind == NodeKind.ITALIC
                ):
                    italic_text = clean_node(wxr, None, gloss_node)
                    if italic_text.endswith(":") or (
                        italic_text.startswith("(")
                        and italic_text.endswith(")")
                    ):
                        for raw_tag in re.split(
                            r":|,", italic_text.strip(":() ")
                        ):
                            raw_tag = raw_tag.strip()
                            if len(raw_tag) > 0:
                                sense_data.raw_tags.append(raw_tag)
                    else:
                        gloss_nodes.append(italic_text)
                elif not (
                    isinstance(gloss_node, WikiNode)
                    and gloss_node.kind == NodeKind.LIST
                ):
                    gloss_nodes.append(gloss_node)

            gloss_text = clean_node(wxr, sense_data, gloss_nodes)
            sense_idx, gloss_text = extract_sense_index(gloss_text)
            if sense_idx != "":
                if (
                    not sense_idx[0].isnumeric()
                    and parent_sense is not None
                    and len(parent_sense.sense_index) != ""
                ):
                    sense_idx = parent_sense.sense_index + sense_idx
                sense_data.sense_index = sense_idx
            elif len(gloss_text.strip()) > 0:
                wxr.wtp.debug(
                    "Failed to extract sense number from gloss node",
                    sortid="extractor/de/glosses/extract_glosses/28",
                )

            if len(gloss_text) > 0:
                sense_data.glosses.append(
                    re.sub(r"^[,—]*\s*", "", gloss_text.strip())
                )
                translate_raw_tags(sense_data)
                word_entry.senses.append(sense_data)

            for sub_list_node in list_item_node.find_child(NodeKind.LIST):
                process_gloss_list_item(
                    wxr,
                    word_entry,
                    sub_list_node,
                    sense_data,
                    section_title,
                )

        else:
            wxr.wtp.debug(
                f"Unexpected list item in glosses: {list_item_node}",
                sortid="extractor/de/glosses/extract_glosses/29",
            )
            continue
    return parent_sense


# plain text POS string used in form-of gloss, usually in genitive case
FORM_OF_POS_STRINGS = {
    "Adjektivs": {"pos": "adj"},
    "Verbs": {"pos": "verb"},
    "Suffixes": {"pos": "suffix", "tags": ["morpheme"]},
    "Substantivs": {"pos": "noun"},
}


def process_form_of_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item_node: WikiNode
) -> None:
    from .section_titles import POS_SECTIONS

    sense = Sense()
    gloss_text = clean_node(wxr, None, list_item_node.children)
    for node in list_item_node.find_child(NodeKind.BOLD | NodeKind.TEMPLATE):
        if isinstance(node, TemplateNode) and node.template_name == "Ü":
            # https://de.wiktionary.org/wiki/Vorlage:Ü
            form_of = clean_node(wxr, None, node.template_parameters.get(2, ""))
            if len(form_of) > 0:
                sense.form_of.append(AltForm(word=form_of))
                break
        elif node.kind == NodeKind.BOLD:
            bold_text = clean_node(wxr, None, node)
            if bold_text != "":
                sense.form_of.append(AltForm(word=bold_text))
                break
    if gloss_text != "":
        sense.glosses.append(gloss_text)
        for str_node in list_item_node.children:
            if isinstance(str_node, str) and len(str_node.strip()) > 0:
                pos_data = {}
                for sense_word in str_node.split():
                    if sense_word in FORM_OF_POS_STRINGS:
                        pos_data = FORM_OF_POS_STRINGS[sense_word]
                    elif sense_word in POS_SECTIONS:
                        pos_data = POS_SECTIONS[sense_word]
                    elif sense_word in GRAMMATICAL_TAGS:
                        tr_tag = GRAMMATICAL_TAGS[sense_word]
                        if isinstance(tr_tag, str):
                            sense.tags.append(tr_tag)
                        elif isinstance(tr_tag, list):
                            sense.tags.extend(tr_tag)
                if len(pos_data) > 0 and word_entry.pos == "unknown":
                    word_entry.pos = pos_data["pos"]
                    word_entry.tags.extend(pos_data.get("tags", []))

        if "form-of" not in word_entry.tags:
            word_entry.tags.append("form-of")
        word_entry.senses.append(sense)
