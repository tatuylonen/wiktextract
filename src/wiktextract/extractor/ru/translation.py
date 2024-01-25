from mediawiki_langcodes import name_to_code
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import HTMLNode, TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import Translation, WordEntry


def extract_translations(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level3_node: WikiNode,
):
    for template_node in level3_node.find_child(NodeKind.TEMPLATE):
        if template_node.template_name == "перев-блок":
            process_translate_block_template(wxr, word_entry, template_node)
        else:
            wxr.wtp.debug(
                f"Found unexpected template {template_node.template_name} in translation section",
                sortid="extractor/ru/translation/extract_translations/100",
            )
            pass


def process_translate_block_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    template_node: TemplateNode,
) -> None:
    # https://ru.wiktionary.org/wiki/Шаблон:перев-блок
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    sense = clean_node(wxr, None, template_node.template_parameters.get(1, ""))
    for list_item in expanded_template.find_child_recursively(
        NodeKind.LIST_ITEM
    ):
        translation = Translation(word="", lang="", sense=sense)
        for node in list_item.children:
            if isinstance(node, WikiNode):
                if node.kind == NodeKind.HTML:
                    if node.tag == "sub":
                        translation.lang_code = clean_node(
                            wxr, None, node.children
                        )
                    elif node.tag == "sup":
                        # language index
                        title = node.attrs.get("title", "")
                        if len(title) > 0:
                            translation.tags.append(title)
                    elif node.tag == "span":
                        process_translate_list_span_tag(
                            wxr, word_entry, translation, node
                        )
                elif node.kind == NodeKind.LINK:
                    translation.lang = clean_node(wxr, None, node)
            elif isinstance(node, str) and len(node.strip(" ():\n")) > 0:
                translation.tags.append(node.strip(" ():\n"))

        if translation.word != "" and translation.lang != "":
            if translation.lang_code == "":
                translation.lang_code = name_to_code(translation.lang, "ru")
            word_entry.translations.append(translation)


def process_translate_list_span_tag(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    translation: Translation,
    span_node: HTMLNode,
) -> None:
    added_tags_num = 0
    for node in span_node.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.LINK:
                translation.word = clean_node(wxr, None, node)
            elif isinstance(node, HTMLNode) and node.tag in ["span", "i"]:
                # gender tag
                title = node.attrs.get("title", "")
                if len(title) > 0:
                    translation.tags.append(title)
                    added_tags_num += 1
                else:
                    tag = clean_node(wxr, None, node)
                    if len(tag) > 0:
                        translation.tags.append(tag)
                        added_tags_num += 1
            elif node.kind == NodeKind.ITALIC:
                translation.tags.append(clean_node(wxr, None, node))
                added_tags_num += 1
        elif isinstance(node, str):
            # convert escaped characters like "&nbsp;"
            text = clean_node(wxr, None, node)
            if text.endswith((",", ";")):
                # this list item has multiple translation words
                striped_text = text.strip(",: ")
                if striped_text.startswith("(") and striped_text.endswith(")"):
                    translation.roman = striped_text.strip("()")
                if translation.word != "" and translation.lang != "":
                    if translation.lang_code == "":
                        translation.lang_code = name_to_code(
                            translation.lang, "ru"
                        )
                    word_entry.translations.append(
                        translation.model_copy(deep=True)
                    )
                # remove data of the last word
                for _ in range(added_tags_num):
                    translation.tags.pop()
                translation.roman = ""
                added_tags_num = 0
            elif text.startswith("(") and text.endswith(")"):
                translation.roman = text.strip("()")
