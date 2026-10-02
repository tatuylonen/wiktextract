from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
):
    sense_index = 0
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sense_index += 1
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if (
                    t_node.template_name == "Překlady"
                    and len(t_node.template_parameters) > 0
                ):
                    extract_překlady_template(
                        wxr, word_entry, t_node, sense_index
                    )


def extract_překlady_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    sense_index: int,
):
    # https://cs.wiktionary.org/wiki/Šablona:Překlady
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    sense = ""
    translations = []
    for dfn_tag in expanded_node.find_html_recursively("dfn"):
        sense = clean_node(wxr, None, dfn_tag)
    for li_tag in expanded_node.find_html_recursively("li"):
        lang_name = "unknown"
        # A multi-word translation is often written as one `P` template per
        # word, separated by a space: "{{P|fr|le}} {{P|fr|meilleur}}" is
        # "le meilleur", while a comma separates two translations.
        joinable = False
        joined = False
        for node in li_tag.children:
            if (
                isinstance(node, HTMLNode)
                and node.tag == "span"
                and "translation-item" in node.attrs.get("class", "").split()
            ):
                word = clean_node(wxr, None, node)
                if word == "":
                    continue
                lang_code = node.attrs.get("lang", "unknown")
                if joinable and translations[-1].lang_code == lang_code:
                    # no space after an elision: "{{P|fr|d’}}{{P|fr|avion}}"
                    if not translations[-1].word.endswith(("'", "’")):
                        translations[-1].word += " "
                    translations[-1].word += word
                    joined = True
                else:
                    translations.append(
                        Translation(
                            word=word,
                            lang=lang_name,
                            lang_code=lang_code,
                            sense=sense,
                            sense_index=sense_index,
                        )
                    )
                    joined = False
                joinable = True
            elif (
                isinstance(node, HTMLNode)
                and node.tag == "abbr"
                and "genus" in node.attrs.get("class", "").split()
            ):
                # The gender after the first word is the head noun's; after
                # a later word it belongs to an inner noun ("une fois")
                raw_tag = node.attrs.get("title", "")
                if raw_tag != "" and len(translations) > 0 and not joined:
                    translations[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(translations[-1])
            else:
                if (
                    isinstance(node, str)
                    and lang_name == "unknown"
                    and node.strip().endswith(":")
                ):
                    lang_name = node.strip().removesuffix(":") or "unknown"
                # category links expand to nothing and don't break a phrase
                if clean_node(wxr, None, node) != "":
                    joinable = False

    word_entry.translations.extend(translations)
    clean_node(wxr, word_entry, expanded_node)
