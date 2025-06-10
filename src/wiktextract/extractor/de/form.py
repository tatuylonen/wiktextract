from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags
from .utils import extract_sense_index


def extracrt_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        sense_idx = ""
        raw_tags = []
        for child in list_item_node.children:
            if isinstance(child, str) and child.startswith("["):
                sense_idx, _ = extract_sense_index(child)
            elif isinstance(child, WikiNode) and child.kind == NodeKind.ITALIC:
                raw_tag = clean_node(wxr, None, child)
                if raw_tag.endswith(":"):
                    raw_tags.append(raw_tag.removesuffix(":").strip())
            elif (
                isinstance(child, WikiNode) and child.kind == NodeKind.LINK
            ) or (
                isinstance(child, TemplateNode)
                and child.template_name in ["Arab", "Arabische Schrift"]
            ):
                form_text = clean_node(wxr, None, child)
                if form_text != "":
                    form_data = Form(
                        form=form_text,
                        tags=tags,
                        sense_index=sense_idx,
                        raw_tags=raw_tags,
                    )
                    translate_raw_tags(form_data)
                    word_entry.forms.append(form_data)
                    raw_tags.clear()
            elif isinstance(child, TemplateNode):
                t_text = clean_node(wxr, word_entry, child)
                if t_text.endswith(":"):
                    raw_tags.append(t_text.removesuffix(":").strip())


def extract_transcription_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        text = clean_node(
            wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
        )
        raw_tag = ""
        for roman in text.split(","):
            if ":" in roman:
                raw_tag = roman[: roman.index(":")].strip()
                roman = roman[roman.index(":") + 1 :].strip()
            roman = roman.strip()
            if roman != "":
                form = Form(form=roman, tags=["transcription"])
                if raw_tag != "":
                    form.raw_tags.append(raw_tag)
                    translate_raw_tags(form)
                word_entry.forms.append(form)
