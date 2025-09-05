import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry


def is_translation_page(title: str) -> bool:
    return re.search(r"/Werger(?:\d+)?$", title) is not None


def extract_translation_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    source: str = "",
    tags: list[str] = [],
    sense: str = "",
    from_trans_see: bool = False,
) -> None:
    sense_index = 0
    for node in level_node.find_child(
        NodeKind.LIST | NodeKind.TEMPLATE | NodeKind.ITALIC | NodeKind.BOLD
    ):
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "werger-ser"
            and not (sense != "" and from_trans_see)
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
            sense_i_str = clean_node(
                wxr, None, node.template_parameters.get(2, "")
            )
            if re.fullmatch(r"\d+", sense_i_str):
                sense_index = int(sense_i_str)
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr,
                    word_entry,
                    list_item,
                    sense,
                    sense_index,
                    source,
                    tags=tags,
                )
        elif node.kind in (NodeKind.ITALIC | NodeKind.BOLD):
            for link_node in node.find_child(NodeKind.LINK):
                link_str = clean_node(wxr, None, link_node)
                if is_translation_page(link_str):
                    extract_translation_page(wxr, word_entry, link_str)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in ("werger-bnr", "bnr-werger")
            and not from_trans_see
        ):
            extract_trans_see_template(wxr, word_entry, node)


def extract_translation_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    sense: str,
    sense_index: int,
    source: str,
    tags: list[str] = [],
) -> None:
    lang_name = "unknown"
    lang_code = "unknown"
    before_colon = True
    for index, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and lang_name == "unknown":
            lang_name = clean_node(
                wxr,
                None,
                list_item.children[:index] + [node[: node.index(":")]],
            )
            if lang_name == "":
                lang_name = "unknown"
            before_colon = False
        elif isinstance(node, TemplateNode) and node.template_name == "Z":
            lang_code = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
        elif isinstance(node, TemplateNode) and node.template_name in [
            "W",
            "W+",
            "W-",
        ]:
            extract_w_template(
                wxr, word_entry, node, sense, sense_index, lang_name, source
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_translation_list_item(
                    wxr,
                    word_entry,
                    child_list_item,
                    sense,
                    sense_index,
                    source,
                    tags=tags,
                )
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and not before_colon
        ):
            if lang_code in ["", "unknown"]:
                new_code = name_to_code(lang_name, "ku")
                if new_code != "":
                    lang_code = new_code
            tr_data = Translation(
                word=clean_node(wxr, None, node),
                lang=lang_name,
                lang_code=lang_code,
                sense=sense,
                sense_index=sense_index,
                source=source,
                tags=tags,
            )
            if tr_data.word != "":
                word_entry.translations.append(tr_data)


def extract_w_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense: str,
    sense_index: int,
    lang_name: str,
    source: str,
    tags: list[str] = [],
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:W
    tr_data = Translation(
        lang=lang_name,
        lang_code=clean_node(
            wxr, None, t_node.template_parameters.get(1, "unknown")
        ),
        word=clean_node(
            wxr,
            None,
            t_node.template_parameters.get(
                "cuda", t_node.template_parameters.get(2, "")
            ),
        ),
        source=source,
        tags=tags,
        sense=sense,
        sense_index=sense_index,
    )
    tag_args = {
        "n": "masculine",
        "m": "feminine",
        "f": "feminine",
        "nt": "gender-neutral",
        "mn": ["feminine", "masculine"],
        "g": "common-gender",
        "p": "plural",
        "y": "singular",
    }
    for tag_arg in [3, 4]:
        tag_arg_value = clean_node(
            wxr, None, t_node.template_parameters.get(tag_arg, "")
        )
        if tag_arg_value in tag_args:
            tag = tag_args[tag_arg_value]
            if isinstance(tag, str):
                tr_data.tags.append(tag)
            elif isinstance(tag, list):
                tr_data.tags.extend(tag)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        if "Latn" in span_tag.attrs.get("class", ""):
            roman = clean_node(wxr, None, span_tag)
            if roman not in ["", tr_data.word]:
                tr_data.roman = roman
                break
    if tr_data.word != "":
        word_entry.translations.append(tr_data)


def extract_translation_page(
    wxr: WiktextractContext, word_entry: WordEntry, page_title: str
) -> None:
    page = wxr.wtp.get_page(page_title, 0)
    if page is None or page.body is None:
        return
    root = wxr.wtp.parse(page.body)
    target_node = find_subpage_section(wxr, root, "Werger")
    if target_node is not None:
        extract_translation_section(
            wxr, word_entry, target_node, source=page_title
        )


def extract_trans_see_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://ku.wiktionary.org/wiki/Şablon:werger-bnr
    sense = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    page_titles = []
    if 2 in t_node.template_parameters:
        for index in range(2, 11):
            if index not in t_node.template_parameters:
                break
            page_titles.append(
                clean_node(wxr, None, t_node.template_parameters[index])
            )
    else:
        page_titles.append(
            clean_node(wxr, None, t_node.template_parameters.get(1, ""))
        )
    for page_title in page_titles:
        if "#" in page_title:
            page_title = page_title[: page_title.index("#")]
        page = wxr.wtp.get_page(page_title)
        if page is None:
            return
        root = wxr.wtp.parse(page.body)
        target_node = find_subpage_section(wxr, root, "Werger")
        if target_node is not None:
            extract_translation_section(
                wxr,
                word_entry,
                target_node,
                source=page_title,
                sense=sense,
                from_trans_see=True,
            )


def find_subpage_section(
    wxr: WiktextractContext, root: WikiNode, target_section: str
) -> WikiNode | None:
    for level_node in root.find_child_recursively(LEVEL_KIND_FLAGS):
        section_title = clean_node(wxr, None, level_node.largs)
        if section_title == target_section:
            return level_node
    return None
