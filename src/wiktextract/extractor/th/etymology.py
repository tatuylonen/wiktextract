from wikitextprocessor import HTMLNode, LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    e_nodes = []
    for node in level_node.children:
        if isinstance(node, TemplateNode) and (
            node.template_name.endswith("-kanjitab")
            or node.template_name == "ja-kt"
        ):
            extract_ja_kanjitab_template(wxr, node, base_data)
        elif not (
            isinstance(node, LevelNode)
            or (
                isinstance(node, TemplateNode)
                and node.template_name in ["ja-see", "ja-see-kango"]
            )
        ):
            e_nodes.append(node)

    e_str = clean_node(wxr, base_data, e_nodes)
    if e_str != "":
        base_data.etymology_text = e_str


def extract_ja_kanjitab_template(
    wxr: WiktextractContext, t_node: TemplateNode, base_data: WordEntry
):
    # https://th.wiktionary.org/wiki/Template:ja-kanjitab
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        is_alt_form_table = False
        for row in table.find_child(NodeKind.TABLE_ROW):
            for header_node in row.find_child(NodeKind.TABLE_HEADER_CELL):
                header_text = clean_node(wxr, None, header_node)
                if header_text.startswith("การสะกดแบบอื่น"):
                    is_alt_form_table = True
        if not is_alt_form_table:
            continue
        forms = []
        for row in table.find_child(NodeKind.TABLE_ROW):
            for cell_node in row.find_child(NodeKind.TABLE_CELL):
                for child_node in cell_node.children:
                    if isinstance(child_node, HTMLNode):
                        if child_node.tag == "span":
                            word = clean_node(wxr, None, child_node)
                            if word != "":
                                forms.append(
                                    Form(
                                        form=word, tags=["alternative", "kanji"]
                                    )
                                )
                        elif child_node.tag == "small":
                            raw_tag = clean_node(wxr, None, child_node).strip(
                                "()"
                            )
                            if raw_tag != "" and len(forms) > 0:
                                forms[-1].raw_tags.append(raw_tag)
                                translate_raw_tags(forms[-1])
        base_data.forms.extend(forms)
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, base_data, link_node)
