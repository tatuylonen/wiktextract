from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry
from .tags import translate_raw_tags


def extract_head_line_nodes(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    nodes: list[WikiNode | str],
) -> None:
    is_first_bold = True
    for node in nodes:
        if isinstance(node, TemplateNode) and node.template_name in [
            "g",
            "gramática",
            "gênero",
            "m",
            "f",
            "n",
            "c",
            "c2g",
            "pr",
            "c.",
            "fp",
            "mp",
        ]:
            extract_gramática_template(wxr, word_entry, node)
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.BOLD
            and is_first_bold
        ):
            extract_head_line_bold_node(wxr, word_entry, node)
            is_first_bold = False


def extract_gramática_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
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


def extract_head_line_bold_node(
    wxr: WiktextractContext, word_entry: WordEntry, bold_node: WikiNode
):
    word = clean_node(wxr, None, bold_node)
    if word != "" and word != wxr.wtp.title:
        word_entry.forms.append(Form(form=word, tags=["canonical"]))
