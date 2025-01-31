from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_ku_tewîn_nav_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:ku-tewîn-nav
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    gender_tags = []
    gender_arg = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if gender_arg == "mê":
        gender_tags = ["feminine"]
    elif gender_arg == "nêr":
        gender_tags = ["masculine"]
    for table_node in expanded_node.find_child(NodeKind.TABLE):
        row_header = ""
        col_headers = []
        shared_tags = []
        for row in table_node.find_child(NodeKind.TABLE_ROW):
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if cell.kind == NodeKind.TABLE_HEADER_CELL:
                    header_str = clean_node(wxr, None, cell)
                    if len(row.children) == 1:
                        if header_str.endswith(" nebinavkirî"):
                            shared_tags = ["indefinite"]
                        elif header_str.endswith(" binavkirî"):
                            shared_tags = ["definite"]
                    elif row.contain_node(NodeKind.TABLE_CELL):
                        row_header = header_str
                    elif header_str not in ["Rewş", ""]:
                        col_headers.append(header_str)
                elif len(row.children) == 1:
                    continue
                else:
                    form_str = clean_node(wxr, None, cell)
                    if form_str not in ["", wxr.wtp.title]:
                        form = Form(
                            form=form_str, tags=gender_tags + shared_tags
                        )
                        if row_header != "":
                            form.raw_tags.append(row_header)
                        if col_index < len(col_headers):
                            form.raw_tags.append(col_headers[col_index])
                        translate_raw_tags(form)
                        word_entry.forms.append(form)
                    col_index += 1
