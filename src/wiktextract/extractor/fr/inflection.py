from dataclasses import dataclass
from itertools import chain

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .pronunciation import is_ipa_text
from .tags import translate_raw_tags


def extract_inflection(
    wxr: WiktextractContext, page_data: list[WordEntry], t_node: TemplateNode
):
    # inflection templates
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_d’accord_en_français
    if t_node.template_name == "avk-tab-conjug":
        extract_avk_tab_conjug(wxr, page_data[-1], t_node)
    else:
        extract_inf_table_template(wxr, page_data[-1], t_node)


IGNORE_TABLE_HEADERS = frozenset(
    {
        "terme",  # https://fr.wiktionary.org/wiki/Modèle:de-adj
        "forme",  # br-flex-adj
    }
)


def split_ipa(text: str) -> list[str]:
    # break IPA text if it contains "ou"(or)
    if " ou " in text:
        # two ipa texts in the same line: "en-conj-rég" template
        return text.split(" ou ")
    if text.startswith("ou "):
        return [text.removeprefix("ou ")]
    if text.endswith("\\Prononciation ?\\"):
        # inflection table templates use a edit link when the ipa data is
        # missing, and the link usually ends with "\Prononciation ?\"
        return []
    return [text]


@dataclass
class TableSpanHeader:
    text: str
    col_index: int = 0
    colspan: int = 1
    row_index: int = 0
    rowspan: int = 1


def extract_inf_table_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://fr.wiktionary.org/wiki/Modèle:fro-adj
    from .form_line import is_conj_link, process_conj_link_node

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        row_headers = []
        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            row_has_data = row.contain_node(NodeKind.TABLE_CELL)
            col_index = 0
            for header in chain(col_headers, row_headers):
                if (
                    row_index >= header.row_index
                    and row_index < header.row_index + header.rowspan
                ):
                    col_index += header.colspan
            for cell_node in row.find_child(NodeKind.TABLE_HEADER_CELL):
                if cell_node.attrs.get("style") == "display:none":
                    continue
                has_conj_link = False
                for link_node in cell_node.find_child_recursively(
                    NodeKind.LINK
                ):
                    if is_conj_link(wxr, link_node):
                        if "form-of" not in word_entry.tags:
                            # Template:fr-verbe-flexion
                            process_conj_link_node(wxr, link_node, [word_entry])
                        has_conj_link = True
                        break
                if has_conj_link:
                    continue
                cell_text = clean_node(wxr, None, cell_node)
                colspan = int(cell_node.attrs.get("colspan", "1"))
                rowspan = int(cell_node.attrs.get("rowspan", "1"))
                if not row_has_data:
                    col_headers.append(
                        TableSpanHeader(
                            cell_text, col_index, colspan, row_index, rowspan
                        )
                    )
                else:
                    row_headers.append(
                        TableSpanHeader(
                            cell_text, col_index, colspan, row_index, rowspan
                        )
                    )
                col_index += colspan

        for row_index, row in enumerate(table.find_child(NodeKind.TABLE_ROW)):
            col_index = 0
            last_col_header_row = 0
            for col_header in col_headers[::-1]:
                if col_header.row_index < row_index:
                    last_col_header_row = col_header.row_index
                    break
            for row_header in row_headers:
                if (
                    row_index >= row_header.row_index
                    and row_index < row_header.row_index + row_header.rowspan
                ):
                    col_index += row_header.colspan
            for cell_node in row.find_child(NodeKind.TABLE_CELL):
                if cell_node.attrs.get("style") == "display:none":
                    continue
                has_conj_link = False
                for link_node in cell_node.find_child_recursively(
                    NodeKind.LINK
                ):
                    if is_conj_link(wxr, link_node):
                        if "form-of" not in word_entry.tags:
                            process_conj_link_node(wxr, link_node, [word_entry])
                        has_conj_link = True
                        break
                if has_conj_link:
                    continue
                colspan = int(cell_node.attrs.get("colspan", "1"))
                rowspan = int(cell_node.attrs.get("rowspan", "1"))
                filtered_cell = []
                cell_tags = []
                for cell_child in cell_node.children:
                    if (
                        isinstance(cell_child, HTMLNode)
                        and cell_child.tag == "small"
                    ):
                        # Modèle:fr-verbe-flexion
                        raw_tag = clean_node(wxr, None, cell_child)
                        if raw_tag.startswith("(") and raw_tag.endswith(")"):
                            cell_tags.append(raw_tag.strip("() "))
                        else:
                            filtered_cell.append(cell_child)
                    else:
                        filtered_cell.append(cell_child)
                cell_text = clean_node(wxr, None, filtered_cell)
                if cell_text == "":
                    continue
                for line in cell_text.splitlines():
                    line = line.removeprefix("ou ").strip()
                    if is_ipa_text(line):
                        if len(word_entry.forms) > 0:
                            word_entry.forms[-1].ipas.extend(split_ipa(line))
                        continue
                    form = Form(form=line, raw_tags=cell_tags)
                    use_col_tags = []
                    for col_header in col_headers[::-1]:
                        if (
                            col_header.col_index < col_index + colspan
                            and col_index
                            < col_header.col_index + col_header.colspan
                            and col_header.text not in form.raw_tags
                            and col_header.text not in use_col_tags
                            and col_header.text.lower()
                            not in IGNORE_TABLE_HEADERS
                            # column header above cell and above last header
                            # don't use headers for other top sections
                            # Modèle:eo-conj
                            and col_header.row_index + col_header.rowspan
                            in [last_col_header_row, last_col_header_row + 1]
                        ):
                            use_col_tags.append(col_header.text)
                    form.raw_tags.extend(use_col_tags[::-1])
                    for row_header in row_headers:
                        if (
                            row_header.row_index < row_index + rowspan
                            and row_index
                            < row_header.row_index + row_header.rowspan
                            and row_header.text not in form.raw_tags
                            and row_header.text.lower()
                            not in IGNORE_TABLE_HEADERS
                        ):
                            form.raw_tags.append(row_header.text)
                    if form.form not in [
                        "",
                        "—",
                        "non comparable",  # Template:de-adj
                        wxr.wtp.title,
                    ]:
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                col_index += colspan


def extract_avk_tab_conjug(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    # https://fr.wiktionary.org/wiki/Modèle:avk-tab-conjug
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        col_headers = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_header = ""
            is_row_header = row.contain_node(NodeKind.TABLE_CELL)
            for col_index, cell in enumerate(
                row.find_child(NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL)
            ):
                cell_text = clean_node(wxr, None, cell)
                if cell_text == "":
                    continue
                elif cell.kind == NodeKind.TABLE_HEADER_CELL:
                    if is_row_header:
                        row_header = cell_text
                    elif cell_text != "Conjugaison Présent Indicatif":
                        col_headers.append(cell_text)
                else:
                    form = Form(form=cell_text, tags=["present", "indicative"])
                    if col_index < len(col_headers):
                        form.raw_tags.append(col_headers[col_index])
                    if row_header != "":
                        form.raw_tags.append(row_header)
                    translate_raw_tags(form)
                    word_entry.forms.append(form)
