from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry
from .tags import translate_raw_tags


def extract_head_line_nodes(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    nodes: list[WikiNode | str],
) -> None:
    for node in nodes:
        if isinstance(node, TemplateNode):
            match node.template_name:
                case "g" | "gramática":
                    extract_gramática_template(wxr, word_entry, node)


def extract_gramática_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
) -> None:
    # https://pt.wiktionary.org/wiki/Predefinição:gramática
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for italic_node in expanded_node.find_child(NodeKind.ITALIC):
        raw_tag = clean_node(wxr, None, italic_node)
        if raw_tag != "":
            word_entry.raw_tags.append(raw_tag)
    translate_raw_tags(word_entry)
