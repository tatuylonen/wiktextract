from wikitextprocessor import LevelNode, NodeKind, TemplateNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_alt_form_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.children:
                if (
                    isinstance(node, TemplateNode)
                    and node.template_name == "alt"
                ):
                    extract_alt_template(wxr, word_entry, node)


def extract_alt_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )

    raw_tags = []
    for italic_node in expanded_node.find_child(NodeKind.ITALIC):
        raw_tags_str = clean_node(wxr, None, italic_node)
        for raw_tag in raw_tags_str.split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                raw_tags.append(raw_tag)
        break

    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html("span"):
        if span_tag.attrs.get("lang", "") == lang_code:
            form = Form(form=clean_node(wxr, None, span_tag), raw_tags=raw_tags)
            translate_raw_tags(form)
            word_entry.forms.append(form)
