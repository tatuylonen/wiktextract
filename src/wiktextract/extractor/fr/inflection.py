from dataclasses import dataclass
from itertools import chain

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

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
    if t_node.template_name == "fr-verbe-flexion":
        extract_fr_verbe_flexion(wxr, page_data, t_node)
    else:
        extract_inf_table_template(wxr, page_data[-1], t_node)


IGNORE_TABLE_HEADERS = frozenset(
    {
        "terme",  # https://fr.wiktionary.org/wiki/Modèle:de-adj
        "forme",  # br-flex-adj
    }
)
IGNORE_TABLE_HEADER_PREFIXES = (
    "voir la conjugaison du verbe ",  # Modèle:fr-verbe-flexion
)
IGNORE_TABLE_CELL = frozenset(
    {
        "Déclinaisons",  # de-adj
        "—",  # https://fr.wiktionary.org/wiki/Modèle:vls-nom
    }
)
IGNORE_TABLE_CELL_PREFIXES = (
    "voir conjugaison ",  # en-conj, avk-conj
)


@dataclass
class TableHeader:
    text: str
    index: int
    span: int


def table_data_cell_is_header(
    wxr: WiktextractContext, cell_node: WikiNode, page_title: str
) -> bool:
    # first child is bold node
    if cell_node.kind == NodeKind.TABLE_CELL:
        for child in cell_node.filter_empty_str_child():
            cell_text = clean_node(wxr, None, child)
            return (
                isinstance(child, WikiNode)
                and child.kind == NodeKind.BOLD
                and len(cell_text) > 0
                and cell_text[0].isupper()
                and cell_text != page_title
            )

    return False


def extract_fr_verbe_flexion(
    wxr: WiktextractContext, page_data: list[WordEntry], t_node: TemplateNode
) -> None:
    from .form_line import is_conj_link, process_conj_link_node

    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    table_nodes = list(expanded_node.find_child(NodeKind.TABLE))
    if len(table_nodes) == 0:
        return
    table_node = table_nodes[0]
    column_headers = []
    rowspan_headers = []
    colspan_headers = []
    for row_num, table_row in enumerate(
        table_node.find_child(NodeKind.TABLE_ROW)
    ):
        # filter empty table cells
        table_row_nodes = [
            row_node_child
            for row_node_child in table_row.children
            if isinstance(row_node_child, WikiNode)
            and (
                row_node_child.kind == NodeKind.TABLE_HEADER_CELL
                or (
                    row_node_child.kind == NodeKind.TABLE_CELL
                    and len(list(row_node_child.filter_empty_str_child())) > 0
                )
            )
            and row_node_child.attrs.get("style") != "display:none"
            and "invisible" not in row_node_child.attrs.get("class", "")
        ]
        current_row_has_data_cell = any(
            isinstance(cell, WikiNode)
            and cell.kind == NodeKind.TABLE_CELL
            and not table_data_cell_is_header(wxr, cell, page_data[-1].word)
            for cell in table_row_nodes
        )
        if not current_row_has_data_cell:
            column_headers.clear()
        row_headers = []
        new_rowspan_headers = []
        for rowspan_text, rowspan_count in rowspan_headers:
            row_headers.append(rowspan_text)
            if rowspan_count - 1 > 0:
                new_rowspan_headers.append((rowspan_text, rowspan_count - 1))
        rowspan_headers = new_rowspan_headers

        column_cell_index = 0
        for column_num, table_cell in enumerate(table_row_nodes):
            form_data = Form()
            if isinstance(table_cell, WikiNode):
                if (
                    table_cell.kind == NodeKind.TABLE_HEADER_CELL
                    or table_data_cell_is_header(
                        wxr, table_cell, page_data[-1].word
                    )
                ):
                    table_header_text = clean_node(
                        wxr, None, table_cell
                    ).replace("\n", " ")
                    if (
                        table_header_text.lower() in IGNORE_TABLE_HEADERS
                        or table_header_text.lower().startswith(
                            IGNORE_TABLE_HEADER_PREFIXES
                        )
                        or len(table_header_text.strip()) == 0
                    ):
                        continue
                    rsplit_header = table_header_text.rsplit(maxsplit=1)
                    if len(rsplit_header) > 1 and rsplit_header[-1].isdecimal():
                        # "Pluriel 1" in template "br-nom"
                        table_header_text = rsplit_header[0]

                    if not current_row_has_data_cell:
                        # if all cells of the row are header cells
                        # then the header cells are column headers
                        if "colspan" in table_cell.attrs:
                            colspan_headers.append(
                                TableHeader(
                                    table_header_text,
                                    column_cell_index,
                                    int(table_cell.attrs.get("colspan")),
                                )
                            )
                        else:
                            column_headers.append(table_header_text)
                        column_cell_index += int(
                            table_cell.attrs.get("colspan", 1)
                        )
                    else:
                        if table_header_text not in row_headers:
                            row_headers.append(table_header_text)
                        if "rowspan" in table_cell.attrs:
                            rowspan_headers.append(
                                (
                                    table_header_text,
                                    int(table_cell.attrs.get("rowspan")) - 1,
                                )
                            )
                elif table_cell.kind == NodeKind.TABLE_CELL:
                    has_conj_link = False
                    for link_node in table_cell.find_child(NodeKind.LINK):
                        if is_conj_link(wxr, link_node):
                            process_conj_link_node(wxr, link_node, page_data)
                            has_conj_link = True
                            break
                    if has_conj_link:
                        continue
                    table_cell_lines = clean_node(wxr, None, table_cell)
                    for table_cell_line in table_cell_lines.splitlines():
                        if is_ipa_text(table_cell_line):
                            form_data.ipas.extend(split_ipa(table_cell_line))
                        elif (
                            table_cell_line != page_data[-1].word
                            and table_cell_line not in IGNORE_TABLE_CELL
                            and not table_cell_line.lower().startswith(
                                IGNORE_TABLE_CELL_PREFIXES
                            )
                        ):
                            if form_data.form == "":
                                form_data.form = table_cell_line
                            else:
                                form_data.form += "\n" + table_cell_line
                    for colspan_header in colspan_headers:
                        if (
                            column_cell_index >= colspan_header.index
                            and column_cell_index
                            < colspan_header.index + colspan_header.span
                        ):
                            form_data.raw_tags.append(colspan_header.text)
                    if (
                        "colspan" not in table_cell.attrs
                        and len(column_headers) > column_cell_index
                        and column_headers[column_cell_index].lower()
                        not in IGNORE_TABLE_HEADERS
                    ):
                        form_data.raw_tags.append(
                            column_headers[column_cell_index]
                        )

                    if len(row_headers) > 0:
                        form_data.raw_tags.extend(row_headers)
                    if form_data.form != "":
                        for form in form_data.form.splitlines():
                            if form.startswith("(") and form.endswith(")"):
                                form_data.raw_tags.append(form.strip("()"))
                                continue
                            new_form_data = form_data.model_copy(deep=True)
                            new_form_data.form = form.removeprefix("ou ")
                            translate_raw_tags(
                                new_form_data, t_node.template_name
                            )
                            if len(new_form_data.form.strip()) > 0:
                                page_data[-1].forms.append(new_form_data)

                    colspan_text = table_cell.attrs.get("colspan", "1")
                    if colspan_text.isdecimal():
                        column_cell_index += int(colspan_text)


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
                colspan = int(cell_node.attrs.get("colspan", "1"))
                rowspan = int(cell_node.attrs.get("rowspan", "1"))
                cell_text = clean_node(wxr, None, cell_node)
                for line in cell_text.splitlines():
                    line = line.removeprefix("ou ").strip()
                    if is_ipa_text(line):
                        if len(word_entry.forms) > 0:
                            word_entry.forms[-1].ipas.extend(split_ipa(line))
                        continue
                    form = Form(form=line)
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
                            and not col_header.text.lower().startswith(
                                IGNORE_TABLE_HEADER_PREFIXES
                            )
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
                            and not row_header.text.lower().startswith(
                                IGNORE_TABLE_HEADER_PREFIXES
                            )
                        ):
                            form.raw_tags.append(row_header.text)
                    if form.form not in [
                        "",
                        "—",
                        wxr.wtp.title,
                        "Déclinaisons",
                    ] and not form.form.startswith(IGNORE_TABLE_CELL_PREFIXES):
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                col_index += colspan
