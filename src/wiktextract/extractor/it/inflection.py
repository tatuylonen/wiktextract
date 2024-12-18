from wikitextprocessor import NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_tabs_template(
    wxr: WiktextractContext, word_entry: WordEntry, node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:Tabs
    tags = [
        ["masculine", "singular"],
        ["masculine", "plural"],
        ["feminine", "singular"],
        ["feminine", "plural"],
    ]
    for arg_name in range(1, 5):
        arg_value = clean_node(
            wxr, None, node.template_parameters.get(arg_name, "")
        )
        if arg_value not in ["", wxr.wtp.title]:
            form = Form(form=arg_value, tags=tags[arg_name - 1])
            word_entry.forms.append(form)


def extract_it_decl_agg_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    # https://it.wiktionary.org/wiki/Template:It-decl-agg4
    # https://it.wiktionary.org/wiki/Template:It-decl-agg2
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        raw_tag = ""
        col_tags = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            row_tag = ""
            col_index = 0
            for cell in row.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                match cell.kind:
                    case NodeKind.TABLE_HEADER_CELL:
                        col_span = cell.attrs.get("colspan", "")
                        if col_span != "":
                            raw_tag = clean_node(wxr, None, cell)
                        elif (
                            len(
                                [
                                    n
                                    for n in row.find_child(
                                        NodeKind.TABLE_HEADER_CELL
                                    )
                                ]
                            )
                            == 1
                        ):
                            row_tag = clean_node(wxr, None, cell)
                        else:
                            col_header = clean_node(wxr, None, cell)
                            if col_header != "":
                                col_tags.append(col_header)
                    case NodeKind.TABLE_CELL:
                        word = clean_node(wxr, None, cell)
                        if word not in ["", wxr.wtp.title]:
                            form = Form(form=word)
                            if raw_tag != "":
                                form.raw_tags.append(raw_tag)
                            if row_tag != "":
                                form.raw_tags.append(row_tag)
                            if col_index < len(col_tags):
                                form.raw_tags.append(col_tags[col_index])
                            translate_raw_tags(form)
                            word_entry.forms.append(form)
                        col_index += 1
