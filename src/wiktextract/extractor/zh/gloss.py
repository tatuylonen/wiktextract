from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .example import extract_examples
from .models import AltForm, Sense, WordEntry
from .tags import translate_raw_tags

# https://zh.wiktionary.org/wiki/Template:Label
LABEL_TEMPLATES = frozenset(["lb", "lbl", "label"])


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    parent_gloss_data: Sense,
) -> None:
    lang_code = page_data[-1].lang_code
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = []
        raw_tags = []
        gloss_data = parent_gloss_data.model_copy(deep=True)
        for node in list_item_node.children:
            if isinstance(node, TemplateNode):
                raw_tag = clean_node(wxr, None, node)
                if node.template_name in LABEL_TEMPLATES:
                    raw_tags.append(raw_tag.strip("()"))
                elif raw_tag.startswith("〈") and raw_tag.endswith("〉"):
                    raw_tags.append(raw_tag.strip("〈〉"))
                elif (
                    node.template_name in FORM_OF_TEMPLATES
                    or node.template_name.endswith(" of")
                ) and process_form_of_template(
                    wxr, node, gloss_data, page_data
                ):
                    pass
                else:
                    gloss_nodes.append(node)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                continue
            else:
                gloss_nodes.append(node)

        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            gloss_text = clean_node(wxr, gloss_data, nodes_without_ruby)
        else:
            ruby_data = []
            gloss_text = clean_node(wxr, gloss_data, gloss_nodes)

        gloss_data.raw_tags.extend(raw_tags)
        if len(gloss_text) > 0:
            gloss_data.glosses.append(gloss_text)
        if len(ruby_data) > 0:
            gloss_data.ruby = ruby_data

        has_nested_gloss = False
        if list_item_node.contain_node(NodeKind.LIST):
            for child_node in list_item_node.find_child(NodeKind.LIST):
                if child_node.sarg.endswith("#"):  # nested gloss
                    has_nested_gloss = True
                    extract_gloss(wxr, page_data, child_node, gloss_data)
                else:  # example list
                    extract_examples(wxr, gloss_data, child_node, page_data)

        if not has_nested_gloss and len(gloss_data.glosses) > 0:
            translate_raw_tags(gloss_data)
            page_data[-1].senses.append(gloss_data)


def process_form_of_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: Sense,
    page_data: list[WordEntry],
) -> bool:
    # Return `True` if template expands to list
    form_of_text = ""
    is_alt_of = template_node.template_name.startswith("alt")
    for param_key in (1, 2, 3, "alt"):
        param_value = clean_node(
            wxr, None, template_node.template_parameters.get(param_key, "")
        )
        if len(param_value) > 0:
            form_of_text = param_value

    for form_of_word in form_of_text.split(","):
        form_of_word = form_of_word.strip()
        if len(form_of_word) > 0:
            form_of = AltForm(word=form_of_word)
            if is_alt_of:
                sense.alt_of.append(form_of)
            else:
                sense.form_of.append(form_of)

    sense.tags.append("alt-of" if is_alt_of else "form-of")

    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    if expanded_template.contain_node(NodeKind.LIST):
        shared_gloss = clean_node(
            wxr, None, list(expanded_template.invert_find_child(NodeKind.LIST))
        )
        for list_item_node in expanded_template.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            new_sense = sense.model_copy(deep=True)
            new_sense.glosses.append(shared_gloss)
            new_sense.glosses.append(
                clean_node(wxr, None, list_item_node.children)
            )
            page_data[-1].senses.append(new_sense)
        return True

    return False


# https://zh.wiktionary.org/wiki/Category:/Category:之形式模板
FORM_OF_TEMPLATES = {
    "alt case, altcaps",
    "alt form, altform",
    "alt sp",
    "construed with",
    "honor alt case",
    "missp",
    "obs sp",
    "rare sp",
    "rfform",
    "short for",
    "stand sp",
    "sup sp",
}
