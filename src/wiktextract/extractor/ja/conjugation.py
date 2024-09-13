from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_conjugation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in {
            "日本語形容動詞活用",
            "日本語五段活用",
            "日本語五段活用/表示",
            "日本語上一段活用",
            "日本語下一段活用",
            "日本語形容詞活用/表示",
            "日本語タルト活用",
            "日本語ダ活用",
            "日本語サ変活用",
            "日本語一段活用",
            "日本語カ変活用",
            "日本語ザ変活用",
        }:
            extract_ja_conjugation_table_template(wxr, word_entry, t_node)


def extract_ja_conjugation_table_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # extract templates use this Lua module
    # https://ja.wiktionary.org/wiki/モジュール:日本語活用表
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link_node)
    for table_index, table_node in enumerate(
        expanded_node.find_child_recursively(NodeKind.TABLE)
    ):
        table_name = ""
        column_headers = []
        row_header = ""
        for row_or_caption in table_node.find_child(
            NodeKind.TABLE_CAPTION | NodeKind.TABLE_ROW
        ):
            if row_or_caption.kind == NodeKind.TABLE_CAPTION:
                table_name = clean_node(wxr, None, row_or_caption.children)
            elif row_or_caption.kind == NodeKind.TABLE_ROW:
                for cell_index, cell_node in enumerate(
                    row_or_caption.find_child(
                        NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
                    )
                ):
                    if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                        if (
                            len(list(row_or_caption.filter_empty_str_child()))
                            == 1
                        ):
                            table_name = clean_node(wxr, None, cell_node)
                        else:
                            column_headers.append(
                                clean_node(wxr, None, cell_node)
                            )
                    elif cell_node.kind == NodeKind.TABLE_CELL:
                        if table_index == 1 and cell_index == 0:
                            row_header = clean_node(wxr, None, cell_node)
                        else:
                            for line in clean_node(
                                wxr, None, cell_node
                            ).splitlines():
                                form = Form(form=line)
                                form.raw_tags.append(table_name)
                                if cell_index < len(column_headers):
                                    form.raw_tags.append(
                                        column_headers[cell_index]
                                    )
                                if len(row_header) > 0:
                                    form.raw_tags.append(row_header)
                                word_entry.forms.append(form)
