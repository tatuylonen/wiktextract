import re

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import process_ejemplo_template
from .inflection import process_inflect_template
from .linkage import process_linkage_template
from .models import AltForm, Form, Sense, WordEntry
from .section_titles import LINKAGE_TITLES
from .tags import translate_raw_tags


def extract_pos_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    has_list = False
    for node in level_node.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            has_list = True
            if node.sarg == ";":
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_gloss_list_item(wxr, word_entry, list_item, Sense())
            elif re.fullmatch(r":+;", node.sarg) is not None:  # nested gloss
                parent_sense = Sense()
                parent_gloss_num = len(node.sarg) - 1
                for sense in word_entry.senses[::-1]:
                    if len(sense.glosses) == parent_gloss_num:
                        parent_sense = sense
                        break
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    sense = parent_sense.model_copy(deep=True)
                    sense.sense_index = ""
                    extract_gloss_list_item(wxr, word_entry, list_item, sense)
            elif node.sarg == ":" and len(word_entry.senses) > 0:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_gloss_list_item(
                        wxr, word_entry, list_item, word_entry.senses[-1]
                    )
        elif isinstance(node, TemplateNode):
            if node.template_name.startswith("inflect."):
                process_inflect_template(wxr, word_entry, node)
            elif node.template_name in ["es.sust", "es.adj", "es.v"]:
                extract_pos_header_template(wxr, word_entry, node)
            elif node.template_name.removesuffix("s") in LINKAGE_TITLES:
                process_linkage_template(wxr, word_entry, node)
            elif node.template_name == "ejemplo" and len(word_entry.senses) > 0:
                process_ejemplo_template(wxr, word_entry.senses[-1], node)
            elif node.template_name == "uso" and len(word_entry.senses) > 0:
                process_uso_template(wxr, word_entry.senses[-1], node)
            elif node.template_name == "ámbito" and len(word_entry.senses) > 0:
                process_ambito_template(wxr, word_entry.senses[-1], node)

    if not has_list:
        sense = Sense()
        gloss = clean_node(
            wxr, sense, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
        )
        if gloss != "":
            sense.glosses.append(gloss)
            word_entry.senses.append(sense)


def extract_gloss_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: Sense,
) -> None:
    if list_item.sarg.endswith(";"):
        raw_tag_text = clean_node(wxr, sense, list_item.children)
        for index, node in enumerate(list_item.children):
            if isinstance(node, str) and sense.sense_index == "":
                m = re.search(r"[\d.a-z]+", node)
                if m is not None:
                    sense.sense_index = m.group(0)
                    raw_tag_text = clean_node(
                        wxr, sense, list_item.children[index + 1 :]
                    )
                    break
        for raw_tag in raw_tag_text.split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                sense.raw_tags.append(raw_tag)

    gloss_nodes = []
    for node in (
        list_item.definition
        if list_item.definition is not None
        else list_item.children
    ):
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            ("f.", "forma ", "plural")
        ):
            process_forma_template(wxr, sense, node)
            gloss_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            gloss_nodes.append(node)

    gloss_text = clean_node(wxr, sense, gloss_nodes)
    if gloss_text != "":
        sense.glosses.append(gloss_text)
        translate_raw_tags(sense)
        if list_item.sarg.endswith(";"):
            word_entry.senses.append(sense)

    for node in (
        list_item.definition
        if list_item.definition is not None
        else list_item.children
    ):
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                child_sense = sense.model_copy(deep=True)
                child_sense.sense_index = ""
                extract_gloss_list_item(
                    wxr, word_entry, child_list_item, child_sense
                )


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
            if "form-of" not in sense.tags:
                sense.tags.append("form-of")


def process_uso_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:uso
    from .tags import USO_TAGS

    for arg_name, arg_value in t_node.template_parameters.items():
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

    clean_node(wxr, sense, t_node)  # save category links


def process_ambito_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:ámbito
    # location data
    from .tags import AMBITO_TAGS

    for arg_name, arg_value in t_node.template_parameters.items():
        if isinstance(arg_name, int):
            arg_value = clean_node(wxr, None, arg_value)
            if arg_value in AMBITO_TAGS:
                tr_tags = AMBITO_TAGS[arg_value]
                if isinstance(tr_tags, str):
                    sense.tags.append(AMBITO_TAGS[arg_value])
                elif isinstance(tr_tags, list):
                    sense.tags.extend(tr_tags)

    clean_node(wxr, sense, t_node)  # save category links


def extract_pos_header_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://es.wiktionary.org/wiki/Plantilla:es.sust
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tag = ""
    for node in expanded_node.children:
        if isinstance(node, str) and node.strip().endswith(":"):
            raw_tag = clean_node(wxr, None, node).strip(": ¦")
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            form = Form(form=clean_node(wxr, None, node))
            if form.form == "":
                continue
            if raw_tag != "":
                for r_tag in raw_tag.split():
                    form.raw_tags.append(r_tag)
                translate_raw_tags(form)
            word_entry.forms.append(form)
