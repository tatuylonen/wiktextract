import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_conjugation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    # https://ja.wiktionary.org/wiki/テンプレートの一覧/ja
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in (
            "日本語形容動詞活用",
            "日本語五段活用",
            "日本語五段活用/表示",
            "日本語上一段活用",
            "日本語上一段活用2",
            "日本語下一段活用",
            "日本語形容詞活用",
            "日本語形容詞活用/表示",
            "日本語形容詞活用2",
            "日本語タルト活用",
            "日本語ダ活用",
            "日本語サ変活用",
            "日本語一段活用",
            "日本語カ変活用",
            "日本語サ変活用",
            "日本語ザ変活用",
            "日本語変格活用",  # has delete request
            "古典日本語四段活用",
            "古典日本語上一段活用",
            "古典日本語上二段活用",
            "古典日本語下一段活用",
            "古典日本語下二段活用",
            "古典日本語変格活用",
        ):
            extract_ja_conj_template(wxr, word_entry, t_node)
        elif t_node.template_name in (
            "日本語助動詞活用",
            "古典日本語助動詞活用",
        ):
            extract_ja_auxiliary_verb_conj_template(wxr, word_entry, t_node)
        elif t_node.template_name in (
            "古典日本語ク活用",
            "古典日本語シク活用",
            "古典日本語ナリ活用",
            "古典日本語タリ活用",
        ):
            extract_classical_ja_conj_template(wxr, word_entry, t_node)


def extract_ja_conj_template(
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
    ruby = []
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
                    ruby, no_ruby_nodes = extract_ruby(wxr, cell_node)
                    no_ruby_text = clean_node(wxr, None, no_ruby_nodes).strip(
                        "()"
                    )
                    if no_ruby_text != "語幹無し":
                        stem = no_ruby_text
                else:
                    for line in cell_text.splitlines():
                        line = line.strip("()")
                        if line != "無し":
                            form = Form(form=stem + line, ruby=ruby)
                            if table_caption != "":
                                form.raw_tags.append(table_caption)
                            if len(top_header_tags) > 0:
                                form.tags.extend(top_header_tags)
                            elif top_header != "":
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
                ruby, no_ruby_nodes = extract_ruby(wxr, cell_node)
                cell_text = clean_node(wxr, None, no_ruby_nodes)
                if col_index == 0:
                    row_header = cell_text
                elif col_index == 1:
                    for line in cell_text.splitlines():
                        form = Form(form=line, ruby=ruby)
                        if table_caption != "":
                            form.raw_tags.append(table_caption)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if form.form != "":
                            forms.append(form)
                elif col_index == 2 and len(cell_text) > 3:
                    for form in forms:
                        form.raw_tags.append(cell_text)
                        raw_tag = cell_text.removesuffix("のみ")
                        if "+" in raw_tag:
                            raw_tag = (
                                raw_tag[: raw_tag.index("+")]
                                .strip()
                                .removesuffix("音便")
                            )
                        if raw_tag != "":
                            form.raw_tags.append(raw_tag)
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
        "上二段": ["kaminidan", "nidan"],
        "下二段": ["shimonidan", "nidan"],
        "四段": ["yodan"],
        "五段": ["godan"],
        "変格": ["irregular"],
    }
    katakana, verb_type = m.groups()
    if katakana in katakana_map:
        tags.append(f"{katakana_map[katakana]}-row")
    tags.extend(verb_tags.get(verb_type, []))
    return tags


def extract_ja_auxiliary_verb_conj_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    col_headers = []
    raw_tag = ""
    for table in expanded_node.find_child(NodeKind.TABLE):
        for row in table.find_child(NodeKind.TABLE_ROW):
            for col_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    col_headers.append(cell_text)
                elif col_index == 6:
                    raw_tag = cell_text
                else:
                    for line in cell_text.splitlines():
                        word = line.strip("()○")
                        if word != "":
                            form = Form(form=word)
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            forms.append(form)
    for form in forms:
        if raw_tag != "":
            form.raw_tags.append(raw_tag)
        translate_raw_tags(form)
    word_entry.forms.extend(forms)


def extract_classical_ja_conj_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    forms = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    col_headers = []
    stem = ""
    raw_tag = ""
    for table in expanded_node.find_child(NodeKind.TABLE):
        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            for col_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    col_headers.append(cell_text)
                elif row_index == 1 and col_index == 1:
                    stem = cell_text
                elif row_index == 1 and col_index == 8:
                    raw_tag = cell_text
                elif not (row_index == 1 and col_index == 0):
                    for line in cell_text.splitlines():
                        line = line.strip("()○-")
                        if line != "":
                            form = Form(form=stem + line)
                            if row_index == 2:
                                col_index += 2
                            if col_index < len(col_headers):
                                form.raw_tags.append(col_headers[col_index])
                            if form.form != "":
                                forms.append(form)
    for form in forms:
        if raw_tag != "":
            form.raw_tags.append(raw_tag)
        translate_raw_tags(form)
    for link in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, word_entry, link)
    word_entry.forms.extend(forms)
