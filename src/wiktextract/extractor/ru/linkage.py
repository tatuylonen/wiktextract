from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    level_node: WikiNode,
):
    if linkage_type not in word_entry.model_fields:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not defined for word entry",
            sortid="extractor/ru/linkage/extract_linkages/10",
        )
        return
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        linkage = Linkage()
        for node in list_item.children:
            if isinstance(node, WikiNode):
                if node.kind == NodeKind.LINK:
                    linkage.word = clean_node(wxr, None, node)
                elif isinstance(node, TemplateNode):
                    find_linkage_tag(wxr, linkage, node)
            elif isinstance(node, str) and node.strip() in (";", ","):
                if len(linkage.word) > 0:
                    getattr(word_entry, linkage_type).append(linkage)
                    tags = linkage.raw_tags
                    linkage = Linkage()
                    if node.strip() == ",":
                        linkage.raw_tags = tags

        if len(linkage.word) > 0:
            getattr(word_entry, linkage_type).append(linkage)
            linkage = Linkage()


def find_linkage_tag(
    wxr: WiktextractContext,
    linkage: Linkage,
    template_node: TemplateNode,
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for span_node in expanded_template.find_html_recursively("span"):
        if "title" in span_node.attrs:
            tag = span_node.attrs["title"]
        else:
            tag = clean_node(wxr, None, span_node)
        if len(tag) > 0:
            linkage.raw_tags.append(tag)


def process_related_block_template(
    wxr: WiktextractContext, word_entry: WordEntry, template_node: TemplateNode
) -> None:
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
                                        word_entry.related.append(linkage)
