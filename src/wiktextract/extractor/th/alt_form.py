from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

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
                elif isinstance(node, TemplateNode) and node.template_name in [
                    "l",
                    "link",
                ]:
                    extract_l_template(wxr, word_entry, node)

    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name == "lo-alt":
            extract_lo_alt_template(wxr, word_entry, t_node)


def extract_alt_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    extract_alt_expanded_nodes(wxr, word_entry, expanded_node, lang_code)


def extract_alt_expanded_nodes(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    root: WikiNode,
    lang_code: str,
) -> None:
    raw_tags = []
    for italic_node in root.find_child(NodeKind.ITALIC):
        raw_tags_str = clean_node(wxr, None, italic_node)
        for raw_tag in raw_tags_str.split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                raw_tags.append(raw_tag)
        break

    for span_tag in root.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        if span_lang == lang_code:
            form = Form(form=clean_node(wxr, None, span_tag), raw_tags=raw_tags)
            if form.form != "":
                translate_raw_tags(form)
                word_entry.forms.append(form)
        elif span_lang.endswith("-Latn") and len(word_entry.forms) > 0:
            word_entry.forms[-1].roman = clean_node(wxr, None, span_tag)

    clean_node(wxr, word_entry, root)


def extract_lo_alt_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for list_node in expanded_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_alt_expanded_nodes(wxr, word_entry, list_item, "lo")


def extract_l_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    form = Form(
        form=clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    )
    if form.form != "":
        word_entry.forms.append(form)
