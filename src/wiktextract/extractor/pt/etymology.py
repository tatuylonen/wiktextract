from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Attestation, WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
) -> None:
    cats = {}
    e_nodes = []
    e_texts = []
    attestations = []
    for node in level_node.children:
        if isinstance(node, WikiNode) and node.kind in LEVEL_KIND_FLAGS:
            break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            e_text = clean_node(wxr, cats, e_nodes).lstrip(": ")
            if e_text != "":
                e_texts.append(e_text)
            e_nodes.clear()
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                e_text = clean_node(wxr, cats, list_item.children)
                if e_text != "":
                    e_texts.append(e_text)
        elif isinstance(node, TemplateNode) and node.template_name == "datação":
            attestations = extract_defdate_template(wxr, cats, node)
        else:
            e_nodes.append(node)

    if len(e_nodes) > 0:
        e_text = clean_node(wxr, cats, e_nodes).lstrip(": ")
        if e_text != "":
            e_texts.append(e_text)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.etymology_texts.extend(e_texts)
            data.categories.extend(cats.get("categories", []))
            data.attestations.extend(attestations)


def extract_defdate_template(
    wxr: WiktextractContext, cats: dict[str, list[str]], t_node: TemplateNode
) -> list[Attestation]:
    attestations = []
    date = (
        clean_node(wxr, cats, t_node)
        .removeprefix("(Datação:")
        .removesuffix(")")
        .strip()
    )
    if date != "":
        attestations.append(Attestation(date=date))
    return attestations
