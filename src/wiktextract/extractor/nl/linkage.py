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
            elif node.template_name == "L-top":
                second_arg = clean_node(
                    wxr, None, node.template_parameters.get(2, "")
                )
                m = re.search(r"\[(\d+)\]", second_arg)
                if m is not None:
                    sense_index = int(m.group(1))
                    sense = second_arg[m.end() :].strip()
                else:
                    sense = second_arg
            elif node.template_name == "L-bottom":
                sense = ""
                sense_index = 0
            elif node.template_name.startswith("nld-"):
                extract_nld_template(wxr, word_entry, node, linkage_type)
            elif node.template_name in ["expr", "fras"]:
                extract_expr_template(wxr, word_entry, node, linkage_type)
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
            elif node.strip().startswith("="):
                sense = node.strip().removeprefix("=").strip()
                linkage_list = getattr(word_entry, linkage_type)
                if len(linkage_list) > 0:
                    linkage_list[-1].sense = sense
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, sense=sense, sense_index=sense_index)
                )


def extract_nld_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:nld-rashonden
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    sense_index_str = clean_node(
        wxr, None, t_node.template_parameters.get(1, "")
    )
    sense_index = 0
    if re.fullmatch(r"\d+", sense_index_str):
        sense_index = int(sense_index_str)
    sense = ""
    for italic_node in expanded_node.find_child_recursively(NodeKind.ITALIC):
        for link_node in italic_node.find_child(NodeKind.LINK):
            sense = clean_node(wxr, None, link_node)
        break

    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        for link_node in list_item.find_child(NodeKind.LINK):
            word = clean_node(wxr, None, link_node)
            if word != "":
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, sense_index=sense_index, sense=sense)
                )


def extract_expr_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:expr
    # https://nl.wiktionary.org/wiki/Sjabloon:fras
    sense_index_str = t_node.template_parameters.get("n", "")
    sense_index = 0
    if re.fullmatch(r"\d+", sense_index_str) is not None:
        sense_index = int(sense_index_str)
    sense_arg = 2 if t_node.template_name == "expr" else 3
    word_arg = 1 if t_node.template_name == "expr" else 2
    sense = clean_node(wxr, None, t_node.template_parameters.get(sense_arg, ""))
    word = clean_node(wxr, None, t_node.template_parameters.get(word_arg, ""))
    m = re.match(r"\[?(\d+)\]?", word)
    if m is not None:  # should use "n" arg
        sense_index = int(m.group(1))
        word = word[m.end() :].strip()
    if word != "":
        getattr(word_entry, linkage_type).append(
            Linkage(word=word, sense=sense, sense_index=sense_index)
        )


def extract_fixed_preposition_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        word = clean_node(wxr, None, list_item.children)
        if len(word) > 0:
            word_entry.derived.append(
                Linkage(word=word, tags=["prepositional"])
            )
