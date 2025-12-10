import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


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
            "日本語変格活用",  # has delete request
        }:
            extract_ja_conjugation_table_template(wxr, word_entry, t_node)


def extract_ja_conjugation_table_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
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
        if table_index == 0:
            extract_ja_first_conj_table(wxr, word_entry, table_node)
        elif table_index == 1:
            extract_ja_second_conj_table(wxr, word_entry, table_node)


def extract_ja_first_conj_table(
    wxr: WiktextractContext, word_entry: WordEntry, table: WikiNode
):
    table_caption = ""
    top_header_tags = []
    top_header = ""
    col_headers = []
    stem = ""
    for row_or_caption in table.find_child(
        NodeKind.TABLE_CAPTION | NodeKind.TABLE_ROW
    ):
        if row_or_caption.kind == NodeKind.TABLE_CAPTION:
            table_caption = clean_node(wxr, None, row_or_caption.children)
        elif row_or_caption.kind == NodeKind.TABLE_ROW:
            for col_index, cell_node in enumerate(
                row_or_caption.find_child(
                    NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
                )
            ):
                cell_text = clean_node(wxr, None, cell_node)
                if cell_node.kind == NodeKind.TABLE_HEADER_CELL:
                    if "colspan" in cell_node.attrs:
                        top_header = cell_text
                        top_header_tags = convert_ja_first_conj_table_header(
                            top_header
                        )
                    else:
                        col_headers.append(cell_text)
                elif col_index == 0:
                    cell_text = cell_text.strip("()")
                    if cell_text != "語幹無し":
                        stem = cell_text
                else:
                    for line in cell_text.splitlines():
                        line = line.strip("()")
                        if line != "無し":
                            form = Form(form=stem + line)
                            if table_caption != "":
                                form.raw_tags.append(table_caption)
                            if len(top_header_tags) > 0:
                                form.tags.extend(top_header_tags)
                            else:
                                form.raw_tags.append(top_header)
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            if form.form != "":
                                translate_raw_tags(form)
                                word_entry.forms.append(form)
    word_entry.tags.extend(top_header_tags)


def extract_ja_second_conj_table(
    wxr: WiktextractContext, word_entry: WordEntry, table: WikiNode
):
    table_caption = ""
    for row_or_caption in table.find_child(
        NodeKind.TABLE_CAPTION | NodeKind.TABLE_ROW
    ):
        if row_or_caption.kind == NodeKind.TABLE_CAPTION:
            table_caption = clean_node(wxr, None, row_or_caption.children)
        elif row_or_caption.kind == NodeKind.TABLE_ROW:
            row_header = ""
            forms = []
            for col_index, cell_node in enumerate(
                row_or_caption.find_child(NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell_node)
                if col_index == 0:
                    row_header = cell_text
                elif col_index == 1:
                    for line in cell_text.splitlines():
                        form = Form(form=line)
                        if table_caption != "":
                            form.raw_tags.append(table_caption)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if form.form != "":
                            forms.append(form)
                elif col_index == 2 and len(cell_text) > 3:
                    for form in forms:
                        form.raw_tags.append(cell_text[:3])
                        form.raw_tags.append(cell_text)
                        translate_raw_tags(form)
            word_entry.forms.extend(forms)


def convert_ja_first_conj_table_header(header: str) -> list[str]:
    # https://en.wikipedia.org/wiki/Japanese_conjugation
    m = re.fullmatch(r"(.+?)行(.+?)活用", header)
    if m is None:
        return []
    tags = []
    katakana_map = {
        "ア": "a",
        "カ": "ka",
        "ガ": "ga",
        "サ": "sa",
        "ザ": "za",
        "タ": "ta",
        "ダ": "da",
        "ナ": "na",
        "ハ": "ha",
        "バ": "ba",
        "マ": "ma",
        "ラ": "ra",
        "ワ": "wa",
    }
    verb_tags = {
        "上一段": ["kamiichidan", "ichidan"],
        "下一段": ["shimoichidan", "ichidan"],
        "五段": ["godan"],
        "変格": ["irregular"],
    }
    katakana, verb_type = m.groups()
    if katakana in katakana_map:
        tags.append(f"{katakana_map[katakana]}-row")
    tags.extend(verb_tags.get(verb_type, []))
    return tags
