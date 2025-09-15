from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_declension_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.startswith("Substantivum "):
            extract_substantivum_template(wxr, word_entry, t_node)


def extract_substantivum_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://cs.wiktionary.org/wiki/Šablona:Substantivum_(cs)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            is_column_header = not row.contain_node(NodeKind.TABLE_CELL)
            for index, cell in enumerate(
                row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_text == "":
                    continue
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if is_column_header and index != 0:
                        col_headers.append(cell_text)
                    elif not is_column_header:
                        row_header = cell_text
                else:
                    for word in cell_text.split("/"):
                        word = word.strip()
                        if word in ["", wxr.wtp.title]:
                            continue
                        form = Form(form=word)
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if index - 1 < len(col_headers):
                            form.raw_tags.append(col_headers[index - 1])
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
