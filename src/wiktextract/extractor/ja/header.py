import re

from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry

FORM_OF_CLASS_TAGS = frozenset(["kanji", "plural"])


def extract_header_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode]
) -> None:
    extracted_forms = set()
    use_nodes = []
    for node in nodes:
        if isinstance(node, TemplateNode) and node.template_name in (
            "jachar",
            "kochar",
            "vichar",
            "zhchar",
        ):
            pass
        else:
            use_nodes.append(node)
    expanded_nodes = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(use_nodes), expand_all=True
    )
    is_first_bold = True
    for node in expanded_nodes.find_child_recursively(
        NodeKind.HTML | NodeKind.BOLD
    ):
        if isinstance(node, HTMLNode) and not (
            node.tag == "strong"
            or "headword" in node.attrs.get("class", "")
            or "form-of" in node.attrs.get("class", "")
        ):
            continue
        form_text = clean_node(wxr, None, node).strip("（）【】 ")
        add_form_data(
            node,
            form_text,
            extracted_forms,
            word_entry,
            is_canonical=is_first_bold,
        )
        is_first_bold = False
    texts = clean_node(wxr, word_entry, expanded_nodes)
    for form_text in re.findall(r"[（【][^（）【】]+[）】]", texts):
        add_form_data(
            expanded_nodes,
            form_text.strip("（）【】 "),
            extracted_forms,
            word_entry,
        )


def add_form_data(
    node: WikiNode,
    forms_text: str,
    extracted_forms: set[str],
    word_entry: WordEntry,
    is_canonical: bool = False,
) -> None:
    for form_text in re.split(r"・|、|,", forms_text):
        form_text = form_text.strip()
        if (
            form_text == word_entry.word
            or form_text.replace(" ", "") == word_entry.word
            or len(form_text) == 0
            or form_text in extracted_forms
        ):
            continue
        extracted_forms.add(form_text)
        form = Form(form=form_text)
        if (
            node.kind == NodeKind.BOLD
            or (isinstance(node, HTMLNode) and node.tag == "strong")
        ) and is_canonical:
            form.tags.append("canonical")
            is_canonical = False
        if isinstance(node, HTMLNode):
            class_names = node.attrs.get("class", "")
            for class_name in FORM_OF_CLASS_TAGS:
                if class_name in class_names:
                    form.tags.append(class_name)
        word_entry.forms.append(form)
