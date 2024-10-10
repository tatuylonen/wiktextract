import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    sense_index = 0
    sense = ""
    raw_tags = []
    for node in level_node.children:
        if isinstance(node, TemplateNode):
            if node.template_name == "intens":
                # https://nl.wiktionary.org/wiki/Sjabloon:intens
                raw_tags = ["intensivering"]
                s_index_str = node.template_parameters.get(2, "").strip()
                if re.fullmatch(r"\d+", s_index_str):
                    sense_index = int(s_index_str)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                word = clean_node(wxr, None, node)
                if word != "":
                    getattr(word_entry, linkage_type).append(
                        Linkage(
                            word=word,
                            sense=sense,
                            sense_index=sense_index,
                            raw_tags=raw_tags,
                        )
                    )
            elif node.kind == NodeKind.LIST:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_linkage_list_item(
                        wxr,
                        word_entry,
                        list_item,
                        linkage_type,
                        sense,
                        sense_index,
                    )


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WordEntry,
    linkage_type: str,
    sense: str,
    sense_index: str,
) -> None:
    for node in list_item.children:
        if isinstance(node, str):
            m = re.search(r"\[(\d+)\]", node)
            if m is not None:
                sense_index = int(m.group(1))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, sense=sense, sense_index=sense_index)
                )
