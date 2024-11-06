import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .example import (
    EXAMPLE_TEMPLATES,
    extract_example_list_item,
    extract_example_template,
)
from .models import AltForm, Sense, WordEntry
from .section_titles import POS_DATA
from .tags import (
    GLOSS_TAG_TEMPLATES,
    LIST_ITEM_TAG_TEMPLATES,
    translate_raw_tags,
)


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    forms_data: WordEntry,
    level_node: LevelNode,
    pos_title: str,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    page_data[-1].pos_title = pos_title
    pos_data = POS_DATA[pos_title]
    page_data[-1].pos = pos_data["pos"]
    page_data[-1].tags.extend(pos_data.get("tags", []))
    if forms_data.pos == "unknown":
        forms_data.pos = page_data[-1].pos
    if forms_data.pos == page_data[-1].pos:
        page_data[-1].forms.extend(forms_data.forms)
        page_data[-1].categories.extend(forms_data.categories)
    else:
        forms_data.forms.clear()
        forms_data.categories.clear()
    extract_pos_section_nodes(wxr, page_data, base_data, forms_data, level_node)


def extract_pos_section_nodes(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    forms_data: WordEntry,
    level_node: LevelNode,
) -> None:
    gloss_list_start = 0
    for index, node in enumerate(level_node.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LIST
            and node.sarg.endswith("#")
        ):
            if gloss_list_start == 0:
                gloss_list_start = index
                extract_pos_header_line_nodes(
                    wxr, page_data[-1], level_node.children[:index]
                )
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, page_data[-1], list_item)
        elif isinstance(node, LevelNode):
            title_text = clean_node(wxr, None, node.largs)
            if title_text in POS_DATA:
                # expanded from "eng-onv-d" form-of template
                from .page import parse_section

                parse_section(wxr, page_data, base_data, forms_data, node)
            else:
                break
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in EXAMPLE_TEMPLATES
            and len(page_data[-1].senses) > 0
        ):
            extract_example_template(wxr, page_data[-1].senses[-1], node)
        elif isinstance(node, TemplateNode) and (
            node.template_name
            in [
                "noun-pl",
                "nl-advb-form",
                "noun-dim",
                "noun-dim-pl",
                "num-form",
                "ordn-form",
                "prep-form",
                "pronom-dem-form",
                "pronom-pos-form",
                "xh-pronom-pos-form",
                "oudeschrijfwijze",
            ]
            or node.template_name.endswith(
                ("adjc-form", "adverb-form", "noun-form")
            )
            or re.search(r"-dec\d+", node.template_name) is not None
        ):
            extract_noun_form_of_template(wxr, page_data[-1], node)
        elif isinstance(node, TemplateNode) and (
            node.template_name.startswith(
                (
                    "1ps",
                    "2ps",
                    "aanv-w",
                    "onv-d",
                    "ott-",
                    "ovt-",
                    "tps",
                    "volt-d",
                    "eng-onv-d",
                )
            )
            or node.template_name.endswith("verb-form")
        ):
            extract_verb_form_of_template(
                wxr, page_data, base_data, forms_data, node
            )


def extract_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    sense = Sense()
    gloss_nodes = []
    for child in list_item.children:
        if isinstance(child, TemplateNode):
            if child.template_name in GLOSS_TAG_TEMPLATES:
                sense.raw_tags.append(clean_node(wxr, sense, child))
            elif child.template_name in LIST_ITEM_TAG_TEMPLATES:
                sense.tags.append(LIST_ITEM_TAG_TEMPLATES[child.template_name])
            else:
                expanded_text = clean_node(wxr, sense, child)
                if expanded_text.startswith("(") and expanded_text.endswith(
                    ")"
                ):
                    sense.raw_tags.append(expanded_text.strip("() "))
                else:
                    gloss_nodes.append(expanded_text)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            if child.sarg.endswith("*"):
                for next_list_item in child.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(wxr, sense, next_list_item)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.ITALIC:
            italic_text = clean_node(wxr, sense, child)
            if italic_text.startswith("(") and italic_text.endswith(")"):
                sense.raw_tags.append(italic_text.strip("() "))
            else:
                gloss_nodes.append(italic_text)
        else:
            gloss_nodes.append(child)

    gloss_text = clean_node(wxr, sense, gloss_nodes)
    while gloss_text.startswith(","):  # between qualifier templates
        gloss_text = gloss_text.removeprefix(",").strip()
    m = re.match(r"\(([^()]+)\)", gloss_text)
    if m is not None:  # expanded "verouderd" template in "2ps" template
        gloss_text = gloss_text[m.end() :].strip()
        sense.raw_tags.append(m.group(1))
    if len(gloss_text) > 0:
        sense.glosses.append(gloss_text)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def extract_pos_header_line_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode | str]
) -> None:
    for node in nodes:
        if isinstance(node, str) and word_entry.etymology_index == "":
            m = re.search(r"\[(.+)\]", node.strip())
            if m is not None:
                word_entry.etymology_index = m.group(1).strip()
        elif isinstance(node, TemplateNode):
            if node.template_name == "-l-":
                extract_l_template(wxr, word_entry, node)
            elif node.template_name == "dimt":
                word_entry.raw_tags.append(clean_node(wxr, word_entry, node))
    translate_raw_tags(word_entry)


def extract_l_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:-l-
    first_arg = clean_node(wxr, None, node.template_parameters.get(1, ""))
    gender_args = {
        "n": "neuter",
        "m": "masculine",
        "fm": ["feminine", "masculine"],
        "p": "plural",
    }
    tag = gender_args.get(first_arg, [])
    if isinstance(tag, str):
        word_entry.tags.append(tag)
    elif isinstance(tag, list):
        word_entry.tags.extend(tag)


# https://nl.wiktionary.org/wiki/Sjabloon:noun-pl
# https://nl.wiktionary.org/wiki/Sjabloon:noun-form
# https://nl.wiktionary.org/wiki/Sjabloon:oudeschrijfwijze
# "getal" and "gesl" args
NOUN_FORM_OF_TEMPLATE_NUM_TAGS = {
    "s": "singular",
    "p": "plural",
    "d": "dual",
    "c": "collective",
    "a": "animate",
    "i": "inanimate",
}
NOUN_FORM_OF_TEMPLATE_GENDER_TAGS = {
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",
    "fm": ["feminine", "masculine"],
    "mf": ["feminine", "masculine"],
    "mn": ["masculine", "neuter"],
}


def extract_noun_form_of_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Categorie:Vormsjablonen
    sense = Sense(tags=["form-of"])
    if t_node.template_name.endswith("-pl"):
        sense.tags.append("plural")
    else:
        num_arg = t_node.template_parameters.get("getal", "")
        if num_arg in NOUN_FORM_OF_TEMPLATE_NUM_TAGS:
            sense.tags.append(NOUN_FORM_OF_TEMPLATE_NUM_TAGS[num_arg])

    gender_arg = t_node.template_parameters.get("gesl", "")
    if gender_arg in NOUN_FORM_OF_TEMPLATE_GENDER_TAGS:
        gender_tag = NOUN_FORM_OF_TEMPLATE_GENDER_TAGS[gender_arg]
        if isinstance(gender_tag, str):
            sense.tags.append(gender_tag)
        elif isinstance(gender_tag, list):
            sense.tags.extend(gender_tag)

    # Sjabloon:oudeschrijfwijze
    g_arg = t_node.template_parameters.get("g", "")
    for tags_dict in [
        NOUN_FORM_OF_TEMPLATE_GENDER_TAGS,
        NOUN_FORM_OF_TEMPLATE_NUM_TAGS,
    ]:
        if g_arg in tags_dict:
            tag = tags_dict[g_arg]
            if isinstance(tag, str):
                sense.tags.append(tag)
            elif isinstance(tag, list):
                sense.tags.extend(tag)

    form_of = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if form_of != "":
        sense.form_of.append(AltForm(word=form_of))

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        sense.glosses.append(clean_node(wxr, None, list_item.children))
        break
    clean_node(wxr, sense, expanded_node)
    word_entry.senses.append(sense)


def extract_verb_form_of_template(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    forms_data: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://nl.wiktionary.org/wiki/Categorie:Werkwoordsvormsjablonen_voor_het_Nederlands
    # https://nl.wiktionary.org/wiki/Categorie:Werkwoordsvormsjablonen
    from .page import extract_section_categories

    orig_data_len = len(page_data)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    extract_pos_section_nodes(
        wxr, page_data, base_data, forms_data, expanded_node
    )
    form_of = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for word_entry in page_data[orig_data_len - len(page_data) - 1 :]:
        for sense in word_entry.senses:
            sense.tags.append("form-of")
            if form_of != "":
                sense.form_of.append(AltForm(word=form_of))
        extract_section_categories(wxr, word_entry, expanded_node)
        word_entry.tags.append("form-of")
