from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from .example import extract_examples
from .models import Sense, WordEntry
from .tags import translate_raw_tags

# https://zh.wiktionary.org/wiki/Template:Label
LABEL_TEMPLATES = frozenset(["lb", "lbl", "label"])


def extract_gloss(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    list_node: WikiNode,
    gloss_data: Sense,
) -> None:
    lang_code = page_data[-1].lang_code
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = []
        raw_tags = []
        for node in list_item_node.children:
            if isinstance(node, TemplateNode):
                raw_tag = clean_node(wxr, None, node)
                if node.template_name in LABEL_TEMPLATES:
                    raw_tags.append(raw_tag.strip("()"))
                elif raw_tag.startswith("〈") and raw_tag.endswith("〉"):
                    raw_tags.append(raw_tag.strip("〈〉"))
                else:
                    gloss_nodes.append(node)
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                continue
            else:
                gloss_nodes.append(node)

        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            gloss_text = clean_node(wxr, gloss_data, nodes_without_ruby)
        else:
            ruby_data = []
            gloss_text = clean_node(wxr, gloss_data, gloss_nodes)
        new_gloss_data = gloss_data.model_copy(deep=True)
        new_gloss_data.raw_tags.extend(raw_tags)
        new_gloss_data.glosses.append(gloss_text)
        if len(ruby_data) > 0:
            new_gloss_data.ruby = ruby_data

        has_nested_gloss = False
        if list_item_node.contain_node(NodeKind.LIST):
            for child_node in list_item_node.find_child(NodeKind.LIST):
                if child_node.sarg.endswith("#"):  # nested gloss
                    has_nested_gloss = True
                    extract_gloss(wxr, page_data, child_node, new_gloss_data)
                else:  # example list
                    extract_examples(wxr, new_gloss_data, child_node)

        if not has_nested_gloss:
            translate_raw_tags(new_gloss_data)
            page_data[-1].senses.append(new_gloss_data)
