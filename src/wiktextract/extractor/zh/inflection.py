from itertools import zip_longest

from wikitextprocessor import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry

# https://zh.wiktionary.org/wiki/Category:日語變格表模板
JAPANESE_INFLECTION_TEMPLATE_PREFIXES = (
    "ja-i",
    "ja-adj-infl",
    "ja-conj-bungo",
    "ja-go",
    "ja-honorific",
    "ja-ichi",
    "ja-kuru",
    "ja-suru",
    "ja-verbconj",
    "ja-zuru",
)


def extract_inflections(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
) -> None:
    for child in level_node.find_child(NodeKind.TEMPLATE):
        template_name = child.template_name.lower()
        if template_name.startswith(JAPANESE_INFLECTION_TEMPLATE_PREFIXES):
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(level_node), expand_all=True
            )
            for table_node in expanded_template.find_child_recursively(
                NodeKind.TABLE
            ):
                extract_ja_inf_table(wxr, page_data, table_node)


def extract_ja_inf_table(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    table_node: WikiNode,
) -> None:
    table_header = []
    small_tags_dict = {}
    for row_node in table_node.find_child(NodeKind.TABLE_ROW):
        if len(list(row_node.filter_empty_str_child())) == 1:
            has_small_tag = False
            # table end tags
            for small_tag in row_node.find_html_recursively("small"):
                has_small_tag = True
                tag_text = clean_node(wxr, None, small_tag)
                if tag_text.startswith(("¹", "²")):
                    small_tags_dict[tag_text[0]] = tag_text[1:].strip()
            if not has_small_tag:
                table_header = clean_node(wxr, None, row_node.children)
        else:
            form_list = []
            hiragana_list = []
            roman_list = []
            raw_tags = []
            small_tags = []
            cell_node_index = 0
            for row_child in row_node.find_child(
                NodeKind.TABLE_HEADER_CELL | NodeKind.TABLE_CELL
            ):
                if row_child.kind == NodeKind.TABLE_HEADER_CELL:
                    for line in clean_node(wxr, None, row_child).splitlines():
                        line = line.strip("（） ")
                        if len(line) > 0:
                            raw_tags.append(line)
                elif row_child.kind == NodeKind.TABLE_CELL:
                    cell_text = clean_node(wxr, None, row_child)
                    if len(cell_text) == 0:
                        continue
                    if cell_node_index >= 3:
                        break
                    for line in cell_text.splitlines():
                        if line.endswith(("¹", "²")):
                            if cell_node_index == 0:
                                small_tags.append(line[-1])
                            line = line[:-1]
                        if cell_node_index == 0:
                            form_list.append(line)
                        elif cell_node_index == 1:
                            hiragana_list.append(line)
                        elif cell_node_index == 2:
                            roman_list.append(line)
                    cell_node_index += 1

            for form, hiragana, roman, small_tag in zip_longest(
                form_list, hiragana_list, roman_list, small_tags
            ):
                form_data = Form(
                    raw_tags=[table_header] + raw_tags,
                    source="inflection table",
                    form=form,
                    hiragana=hiragana,
                    roman=roman,
                )
                if small_tag is not None:
                    form_data.raw_tags.append(small_tag)
                page_data[-1].forms.append(form_data)

    for form_data in page_data[-1].forms:
        if form_data.source == "inflection table":
            for index, raw_tag in enumerate(form_data.raw_tags):
                if raw_tag in small_tags_dict:
                    form_data.raw_tags[index] = small_tags_dict[raw_tag]
