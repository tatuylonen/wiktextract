from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .section_titles import LINKAGE_TITLES
from .tags import translate_raw_tags


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    level_node: LevelNode,
):
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not defined for word entry",
            sortid="extractor/ru/linkage/extract_linkages/10",
        )
        return
    sense_index = 0
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        if list_item.sarg == "#":
            sense_index += 1
        linkage = Linkage(sense_index=sense_index)
        for node in list_item.children:
            if isinstance(node, WikiNode):
                if node.kind == NodeKind.LINK:
                    linkage.word = clean_node(wxr, None, node)
                elif isinstance(node, TemplateNode):
                    find_linkage_tag(wxr, linkage, node)
            elif isinstance(node, str) and node.strip() in (";", ","):
                if len(linkage.word) > 0:
                    translate_raw_tags(linkage)
                    getattr(word_entry, linkage_type).append(linkage)
                    tags = linkage.raw_tags
                    linkage = Linkage(sense_index=sense_index)
                    if node.strip() == ",":
                        linkage.raw_tags = tags

        if len(linkage.word) > 0:
            translate_raw_tags(linkage)
            getattr(word_entry, linkage_type).append(linkage)
            linkage = Linkage(sense_index=sense_index)


def find_linkage_tag(
    wxr: WiktextractContext,
    linkage: Linkage,
    template_node: TemplateNode,
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for span_node in expanded_template.find_html_recursively("span"):
        tag = clean_node(wxr, None, span_node)
        if len(tag) > 0:
            linkage.raw_tags.append(tag)


def process_related_block_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
    # "Родственные слова" section
    # Шаблон:родств-блок
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for table_node in expanded_template.find_child(NodeKind.TABLE):
        table_header = ""
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    cell_text = clean_node(wxr, None, cell)
                    if cell_text.startswith("Список всех слов с корнем"):
                        table_header = cell_text
                elif cell.kind == NodeKind.TABLE_CELL:
                    if "block-head" in cell.attrs.get("class", ""):
                        table_header = clean_node(wxr, None, cell)
                    else:
                        for list_item in cell.find_child_recursively(
                            NodeKind.LIST_ITEM
                        ):
                            for node in list_item.find_child(
                                NodeKind.HTML | NodeKind.LINK
                            ):
                                if (
                                    isinstance(node, HTMLNode)
                                    and node.tag == "span"
                                ):
                                    row_header = clean_node(
                                        wxr, None, node
                                    ).removesuffix(":")
                                elif node.kind == NodeKind.LINK:
                                    linkage = Linkage(
                                        word=clean_node(wxr, None, node)
                                    )
                                    if table_header != "":
                                        linkage.raw_tags.append(table_header)
                                    if row_header != "":
                                        linkage.raw_tags.append(row_header)
                                    if linkage.word != "":
                                        translate_raw_tags(linkage)
                                        word_entry.related.append(linkage)


def extract_phrase_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: WikiNode,
    title_text: str,
) -> None:
    # "Фразеологизмы и устойчивые сочетания" section
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        # a template that adds links to words in list
        # https://ru.wiktionary.org/wiki/Шаблон:в_три_колонки
        if t_node.template_name.lower() in ["в три колонки", "фразеологизмы"]:
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(t_node), expand_all=True
            )
            for div_tag in expanded_node.find_html(
                "div", attr_name="class", attr_value="col3"
            ):
                extract_phrase_section(wxr, word_entry, div_tag, title_text)

    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child_recursively(NodeKind.LIST_ITEM):
            prefix_nodes = []
            before_link = True
            word_nodes = []
            inside_brackets = False
            for node in list_item.children:
                if isinstance(node, str) and len(node.strip()) > 0:
                    if before_link:
                        prefix_nodes.append(node)
                    elif node.strip().startswith("("):
                        inside_brackets = True
                        word_nodes.append(node)
                    elif node.strip().startswith(")"):
                        inside_brackets = False
                        word_nodes.append(node.strip(",; "))
                    elif inside_brackets:
                        word_nodes.append(node)

                    if not inside_brackets and node.strip().endswith(
                        (",", ";", "/")
                    ):
                        word = clean_node(wxr, None, prefix_nodes + word_nodes)
                        word_nodes.clear()
                        if len(word) > 0:
                            linkage = Linkage(word=word)
                            if title_text not in [
                                "фразеологизмы и устойчивые сочетания",
                                "пословицы и поговорки",
                            ]:
                                linkage.raw_tags.append(title_text)
                            translate_raw_tags(linkage)
                            if title_text == "пословицы и поговорки":
                                word_entry.proverbs.append(linkage)
                            else:
                                word_entry.derived.append(linkage)
                elif isinstance(node, WikiNode):
                    if node.kind == NodeKind.LIST:
                        continue
                    elif node.kind == NodeKind.LINK:
                        before_link = False
                    if before_link:
                        prefix_nodes.append(node)
                    else:
                        word_nodes.append(node)

            word = clean_node(wxr, None, prefix_nodes + word_nodes)
            if len(word) > 0:
                linkage = Linkage(word=word)
                if title_text not in [
                    "фразеологизмы и устойчивые сочетания",
                    "пословицы и поговорки",
                ]:
                    linkage.raw_tags.append(title_text)
                translate_raw_tags(linkage)
                if title_text == "пословицы и поговорки":
                    word_entry.proverbs.append(linkage)
                else:
                    word_entry.derived.append(linkage)


def process_semantics_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
    sense_index: int,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:семантика
    for key, value in template_node.template_parameters.items():
        if key in LINKAGE_TITLES and isinstance(value, str):
            for word in value.split(","):
                word = word.strip()
                if word not in ("", "-", "—"):
                    getattr(word_entry, LINKAGE_TITLES[key]).append(
                        Linkage(word=word, sense_index=sense_index)
                    )


def extract_alt_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    for link_node in level_node.find_child_recursively(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if word != "":
            word_entry.forms.append(Form(form=word, tags=tags))
