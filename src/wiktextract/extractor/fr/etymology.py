from collections import defaultdict
from dataclasses import dataclass, field

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, WordEntry


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
        if node.kind in LEVEL_KIND_FLAGS and node_index < level_node_index:
            level_node_index = node_index
        elif node.kind == NodeKind.LIST:
            for etymology_item in node.find_child(NodeKind.LIST_ITEM):
                pos_id, pos_title = extract_etymology_list_item(
                    wxr, etymology_item, etymology_dict, pos_id, pos_title
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


def extract_etymology_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    etymology_dict: EtymologyDict,
    pos_id: str,
    pos_title: str,
) -> tuple[str, str]:
    etymology_data = find_pos_in_etymology_list(wxr, list_item)
    if etymology_data is not None:
        pos_id, pos_title, etymology_text, categories = etymology_data
        if len(etymology_text) > 0:
            etymology_dict[(pos_id, pos_title)].texts.append(etymology_text)
            etymology_dict[(pos_id, pos_title)].categories.extend(categories)
    else:
        categories = {}
        etymology_text = clean_node(
            wxr,
            categories,
            list(
                list_item.invert_find_child(
                    NodeKind.LIST, include_empty_str=True
                )
            ),
        )
        if len(etymology_text) > 0:
            etymology_dict[(pos_id, pos_title)].texts.append(etymology_text)
            etymology_dict[(pos_id, pos_title)].categories.extend(
                categories.get("categories", [])
            )

    for child_list in list_item.find_child(NodeKind.LIST):
        for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
            extract_etymology_list_item(
                wxr, child_list_item, etymology_dict, pos_id, pos_title
            )

    return pos_id, pos_title


def find_pos_in_etymology_list(
    wxr: WiktextractContext, list_item_node: WikiNode
) -> tuple[str, str, str, list[str]] | None:
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
                                [
                                    n
                                    for n in list_item_node.children[
                                        index + 1 :
                                    ]
                                    if not (
                                        isinstance(n, WikiNode)
                                        and n.kind == NodeKind.LIST
                                    )
                                ],
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
                    wxr,
                    categories,
                    [
                        n
                        for n in list_item_node.children[index + 1 :]
                        if not (
                            isinstance(n, WikiNode) and n.kind == NodeKind.LIST
                        )
                    ],
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
                            [
                                n
                                for n in list_item_node.children[index + 1 :]
                                if not (
                                    isinstance(n, WikiNode)
                                    and n.kind == NodeKind.LIST
                                )
                            ],
                        ).lstrip(") "),
                        categories.get("categories", []),
                    )
            italic_text = clean_node(wxr, None, node)
            if (
                index <= 1  # first node is empty string
                and italic_text.startswith("(")
                and italic_text.endswith(")")
            ):
                return (
                    "",
                    italic_text.strip("() "),
                    clean_node(
                        wxr,
                        categories,
                        [
                            n
                            for n in list_item_node.children[index + 1 :]
                            if not (
                                isinstance(n, WikiNode)
                                and n.kind == NodeKind.LIST
                            )
                        ],
                    ),
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
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_etymology_example_list_item(wxr, list_item, base_data, "")


def extract_etymology_example_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    base_data: WordEntry,
    note: str,
) -> None:
    from .gloss import process_exemple_template

    time = ""
    source = ""
    example_nodes = []
    has_exemple_template = False
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["siècle", "circa", "date"]:
                time = clean_node(wxr, base_data, node).strip("() ")
            elif node.template_name == "exemple":
                has_exemple_template = True
                example_data = process_exemple_template(
                    wxr, node, base_data, time
                )
                if example_data.text != "":
                    example_data.note = note
                    base_data.etymology_examples.append(example_data)
            elif node.template_name == "source":
                source = clean_node(wxr, base_data, node).strip("— ()")
            else:
                example_nodes.append(node)
        else:
            example_nodes.append(node)

    if not has_exemple_template:
        if time == "" and list_item.contain_node(NodeKind.LIST):
            note = clean_node(
                wxr,
                base_data,
                list(
                    list_item.invert_find_child(
                        NodeKind.LIST, include_empty_str=True
                    )
                ),
            )
            for next_list in list_item.find_child(NodeKind.LIST):
                for next_list_item in next_list.find_child(NodeKind.LIST_ITEM):
                    extract_etymology_example_list_item(
                        wxr, next_list_item, base_data, note
                    )
        elif len(example_nodes) > 0:
            example_str = clean_node(wxr, base_data, example_nodes)
            if example_str != "":
                example_data = Example(
                    text=example_str, time=time, ref=source, note=note
                )
                base_data.etymology_examples.append(example_data)
