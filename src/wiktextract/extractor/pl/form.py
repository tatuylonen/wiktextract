import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_zapis_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    # get around "preformatted" node
    for node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if node.template_name == "ptrad":
            form_text = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            if form_text != "":
                base_data.forms.append(
                    Form(form=form_text, tags=["Traditional Chinese"])
                )


def extract_transliteracja_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\([\d\s,-.]+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
                    roman = node[m.end() :].strip()
                    if roman != "":
                        base_data.forms.append(
                            Form(
                                form=roman,
                                sense_index=sense_index,
                                tags=["transliteration"],
                            )
                        )
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name == "translit":
            roman = clean_node(wxr, None, t_node)
            if roman != "":
                base_data.forms.append(
                    Form(form=roman, tags=["transliteration"])
                )


def extract_alt_form_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for link_node in list_item.find_child(NodeKind.LINK):
                form = clean_node(wxr, None, link_node)
                if form != "":
                    base_data.forms.append(
                        Form(form=form, tags=["alternative"])
                    )
    # "preformatted" node
    for t_node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if t_node.template_name.startswith("ortografie"):
            extract_ortografie_template(wxr, base_data, t_node)


def extract_ortografie_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    extract_ortografie_list_item(wxr, base_data, expanded_node)
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_ortografie_list_item(wxr, base_data, list_item)


def extract_ortografie_list_item(
    wxr: WiktextractContext, base_data: WordEntry, list_item: WikiNode
) -> None:
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            node_str = clean_node(wxr, None, node)
            if node_str.endswith(":"):
                raw_tag = node_str.strip(": ")
        elif isinstance(node, str) and node.strip() != "":
            form = Form(form=node.strip(), tags=["alternative"])
            if raw_tag != "":
                form.raw_tags.append(raw_tag)
                translate_raw_tags(form)
            base_data.forms.append(form)


def extract_transkrypcja_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name == "hep":
                    extract_hep_template(wxr, base_data, t_node)


def extract_hep_template(
    wxr: WiktextractContext, base_data: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    raw_tag = ""
    for node in expanded_node.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            node_str = clean_node(wxr, None, node)
            if node_str.endswith(":"):
                raw_tag = node_str.strip(":")
        elif isinstance(node, str) and node.strip() != "":
            form = Form(form=node.strip(), tags=["transcription"])
            if raw_tag != "":
                form.raw_tags.append(raw_tag)
                translate_raw_tags(form)
            base_data.forms.append(form)
