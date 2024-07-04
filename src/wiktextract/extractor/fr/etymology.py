from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import WordEntry


@dataclass
class EtymologyData:
    texts: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)


EtymologyDict = dict[tuple[str, str], EtymologyData]


def extract_etymology(
    wxr: WiktextractContext, level_node: LevelNode, base_data: WordEntry
) -> EtymologyDict:
    etymology_dict: EtymologyDict = defaultdict(EtymologyData)
    level_node_index = len(level_node.children)
    pos_id = ""
    pos_title = ""
    for node_index, node in level_node.find_child(
        NodeKind.LIST | LEVEL_KIND_FLAGS, True
    ):
        if node.kind in LEVEL_KIND_FLAGS:
            level_node_index = node_index
            title_text = clean_node(wxr, None, node.largs)
            if title_text == "Attestations historiques":
                extract_etymology_examples(wxr, node, base_data)
        elif node.kind == NodeKind.LIST:
            for etymology_item in node.find_child(NodeKind.LIST_ITEM):
                etymology_data = find_pos_in_etymology_list(wxr, etymology_item)
                if etymology_data is not None:
                    pos_id, pos_title, etymology_text, categories = (
                        etymology_data
                    )
                    if len(etymology_text) > 0:
                        etymology_dict[(pos_id, pos_title)].texts.append(
                            etymology_text
                        )
                        etymology_dict[(pos_id, pos_title)].categories.extend(
                            categories
                        )
                else:
                    categories = {}
                    etymology_text = clean_node(
                        wxr, categories, etymology_item.children
                    )
                    if len(etymology_text) > 0:
                        etymology_dict[(pos_id, pos_title)].texts.append(
                            etymology_text
                        )
                        etymology_dict[(pos_id, pos_title)].categories.extend(
                            categories.get("categories", [])
                        )

    if len(etymology_dict) == 0:
        categories = {}
        etymology_text = clean_node(
            wxr, categories, level_node.children[:level_node_index]
        )
        if len(etymology_text) > 0:
            etymology_dict[("", "")].texts.append(etymology_text)
            etymology_dict[(pos_id, pos_title)].categories.extend(
                categories.get("categories", [])
            )

    if ("", "") in etymology_dict and etymology_dict.get(("", "")).texts == [
        " "
    ]:
        # remove "ébauche-étym" template placeholder
        del etymology_dict[("", "")]

    return etymology_dict


def find_pos_in_etymology_list(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> Optional[tuple[str, str, str, list[str]]]:
    """
    Return tuple of POS id, title, etymology text, categories if the passed
    list item node starts with italic POS node or POS template, otherwise
    return `None`.
    """
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "ébauche-étym":
            return ("", "", " ", [])  # missing etymology

    categories = {}

    for index, node in list_item_node.find_child(
        NodeKind.TEMPLATE | NodeKind.LINK | NodeKind.ITALIC, True
    ):
        if isinstance(node, TemplateNode) and node.template_name in (
            "lien-ancre-étym",
            "laé",
        ):
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node), expand_all=True
            )
            for italic_node in expanded_template.find_child(NodeKind.ITALIC):
                for link_node in italic_node.find_child(NodeKind.LINK):
                    if isinstance(
                        link_node.largs[0][0], str
                    ) and link_node.largs[0][0].startswith("#"):
                        pos_id = link_node.largs[0][0].removeprefix("#")
                        return (
                            pos_id,
                            clean_node(wxr, None, link_node).strip(": "),
                            clean_node(
                                wxr,
                                categories,
                                list_item_node.children[index + 1 :],
                            ),
                            categories.get("categories", []),
                        )
        elif (
            node.kind == NodeKind.LINK
            and isinstance(node.largs[0][0], str)
            and node.largs[0][0].startswith("#")
        ):
            pos_id = node.largs[0][0].removeprefix("#")
            return (
                pos_id,
                clean_node(wxr, None, node).strip(": "),
                clean_node(
                    wxr, categories, list_item_node.children[index + 1 :]
                ),
                categories.get("categories", []),
            )
        elif node.kind == NodeKind.ITALIC:
            for link_node in node.find_child(NodeKind.LINK):
                if isinstance(link_node.largs[0][0], str) and link_node.largs[
                    0
                ][0].startswith("#"):
                    pos_id = link_node.largs[0][0].removeprefix("#")
                    return (
                        pos_id,
                        clean_node(wxr, None, link_node).strip(": "),
                        clean_node(
                            wxr,
                            categories,
                            list_item_node.children[index + 1 :],
                        ).lstrip(") "),
                        categories.get("categories", []),
                    )


def insert_etymology_data(
    lang_code: str, page_data: list[WordEntry], etymology_dict: EtymologyDict
) -> None:
    """
    Insert list of etymology data extracted from the level 3 node to each sense
    dictionary matches the language and POS.
    """
    sense_dict = defaultdict(list)  # group by pos title and id
    for sense_data in page_data:
        if sense_data.lang_code == lang_code:
            sense_dict[sense_data.pos_title].append(sense_data)
            sense_dict[sense_data.pos_id].append(sense_data)
            if sense_data.pos_id.endswith("-1"):
                # extra ids for the first title
                sense_dict[sense_data.pos_title.replace(" ", "_")].append(
                    sense_data
                )
                sense_dict[sense_data.pos_id.removesuffix("-1")].append(
                    sense_data
                )

    for pos_id_title, etymology_data in etymology_dict.items():
        if pos_id_title == ("", ""):  # add to all sense dictionaries
            for sense_data_list in sense_dict.values():
                for sense_data in sense_data_list:
                    sense_data.etymology_texts = etymology_data.texts
                    sense_data.categories.extend(etymology_data.categories)
        else:
            for pos_key in pos_id_title:
                if pos_key in sense_dict:
                    for sense_data in sense_dict[pos_key]:
                        sense_data.etymology_texts = etymology_data.texts
                        sense_data.categories.extend(etymology_data.categories)


def extract_etymology_examples(
    wxr: WiktextractContext,
    level_node: LevelNode,
    base_data: WordEntry,
) -> None:
    from .gloss import process_exemple_template

    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        time = ""
        for template_node in list_item.find_child(NodeKind.TEMPLATE):
            if template_node.template_name == "siècle":
                time = clean_node(wxr, None, template_node).strip("() ")
            elif template_node.template_name == "exemple":
                example_data = process_exemple_template(
                    wxr, template_node, base_data, time
                )
                if example_data.text != "":
                    base_data.etymology_examples.append(example_data)
