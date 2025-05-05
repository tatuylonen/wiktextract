import re

from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags

FORM_OF_CLASS_TAGS = frozenset(["kanji", "plural"])


def extract_header_nodes(
    wxr: WiktextractContext, word_entry: WordEntry, nodes: list[WikiNode]
) -> None:
    extracted_forms = {}
    use_nodes = []
    is_first_bold = True
    for node in nodes:
        if isinstance(node, TemplateNode) and node.template_name in (
            "jachar",
            "kochar",
            "vichar",
            "zhchar",
        ):
            is_first_bold = False
        else:
            use_nodes.append(node)
    expanded_nodes = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(use_nodes), expand_all=True
    )
    raw_tags = []
    for node in expanded_nodes.find_child_recursively(
        NodeKind.HTML | NodeKind.BOLD | NodeKind.ITALIC
    ):
        if (
            isinstance(node, HTMLNode)
            and "gender" in node.attrs.get("class", "").split()
        ):
            raw_tag_text = clean_node(wxr, None, node)
            for raw_tag in raw_tag_text.split():
                if raw_tag != "":
                    word_entry.raw_tags.append(raw_tag)
        if isinstance(node, HTMLNode) and not (
            node.tag in ["strong", "small", "i", "b"]
            or "headword" in node.attrs.get("class", "")
            or "form-of" in node.attrs.get("class", "")
        ):
            continue
        if isinstance(node, HTMLNode) and node.tag in ["small", "i"]:
            raw_tag = clean_node(wxr, None, node).strip("(): ")
            if raw_tag != "又は" and raw_tag not in raw_tags:
                # ignore "又は"(or) in "ja-noun" template
                raw_tags.append(raw_tag)
        else:
            form_text = clean_node(wxr, None, node).strip("（）【】 ")
            add_form_data(
                node,
                form_text,
                extracted_forms,
                word_entry,
                raw_tags,
                is_canonical=is_first_bold,
            )
            if node.kind == NodeKind.BOLD:
                is_first_bold = False
            raw_tags.clear()
    clean_node(wxr, word_entry, expanded_nodes)
    translate_raw_tags(word_entry)


def add_form_data(
    node: WikiNode,
    forms_text: str,
    extracted_forms: dict[str, Form],
    word_entry: WordEntry,
    raw_tags: list[str],
    is_canonical: bool = False,
) -> None:
    for form_text in re.split(r"・|、|,|•", forms_text):
        form_text = form_text.strip()
        if form_text in extracted_forms:
            form = extracted_forms[form_text]
            for raw_tag in raw_tags:
                if raw_tag not in form.raw_tags:
                    form.raw_tags.append(raw_tag)
            translate_raw_tags(form)
            continue
        elif (
            form_text == word_entry.word
            or form_text.replace(" ", "") == word_entry.word
            or len(form_text) == 0
        ):
            continue
        form = Form(form=form_text, raw_tags=raw_tags)
        extracted_forms[form_text] = form
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
        if "tr Latn" in node.attrs.get("class", ""):
            form.tags.append("transliteration")
        translate_raw_tags(form)
        word_entry.forms.append(form)
