from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Form, WordEntry
from .tags import translate_raw_tags


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
):
    from .example import extract_template_zh_x

    e_nodes = []
    for node in level_node.children:
        if isinstance(node, TemplateNode) and node.template_name in [
            "zh-x",
            "zh-q",
        ]:
            for example_data in extract_template_zh_x(
                wxr, node, Example(text="")
            ):
                base_data.etymology_examples.append(example_data)
            clean_node(wxr, base_data, node)
        elif isinstance(node, TemplateNode) and node.template_name.lower() in [
            "rfe",  # missing etymology
            "zh-forms",
            "zh-wp",
            "wp",
            "wikipedia",
        ]:
            continue
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            has_zh_x = False
            for template_node in node.find_child_recursively(NodeKind.TEMPLATE):
                if template_node.template_name in ["zh-x", "zh-q"]:
                    has_zh_x = True
                    for example_data in extract_template_zh_x(
                        wxr, template_node, Example(text="")
                    ):
                        base_data.etymology_examples.append(example_data)
                    clean_node(wxr, base_data, template_node)
            if not has_zh_x:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    e_text = clean_node(wxr, None, list_item.children)
                    if len(e_text) > 0:
                        base_data.etymology_texts.append(e_text)
        elif isinstance(node, TemplateNode) and node.template_name in [
            "ja-see",
            "ja-see-kango",
            "zh-see",
        ]:
            from .page import process_soft_redirect_template

            page_data.append(base_data.model_copy(deep=True))
            process_soft_redirect_template(wxr, node, page_data[-1])
        elif isinstance(node, TemplateNode) and (
            node.template_name.endswith("-kanjitab")
            or node.template_name == "ja-kt"
        ):
            extract_ja_kanjitab_template(wxr, node, base_data)
        elif isinstance(node, LevelNode):
            break
        else:
            e_nodes.append(node)

    if len(e_nodes) > 0:
        etymology_text = clean_node(wxr, base_data, e_nodes)
        if len(etymology_text) > 0:
            base_data.etymology_texts.append(etymology_text)


def extract_ja_kanjitab_template(
    wxr: WiktextractContext, t_node: TemplateNode, base_data: WordEntry
):
    # https://zh.wiktionary.org/wiki/Template:ja-kanjitab
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for table in expanded_node.find_child(NodeKind.TABLE):
        is_alt_form_table = False
        for row in table.find_child(NodeKind.TABLE_ROW):
            for header_node in row.find_child(NodeKind.TABLE_HEADER_CELL):
                header_text = clean_node(wxr, None, header_node)
                if header_text == "其他表記":
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
