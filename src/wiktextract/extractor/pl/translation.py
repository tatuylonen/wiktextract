import re
from collections import defaultdict

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Translation, WordEntry
from .tags import translate_raw_tags


def extract_translation_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    lang_code: str,
) -> None:
    from .page import match_sense_index

    translations = defaultdict(list)
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_translation_list_item(wxr, list_item, translations)

    matched_indexes = set()
    for data in page_data:
        if data.lang_code == lang_code:
            for sense_index in translations.keys():
                if match_sense_index(sense_index, data):
                    data.translations.extend(translations[sense_index])
                    matched_indexes.add(sense_index)
            data.translations.extend(translations.get("", []))

    if "" in translations:
        del translations[""]
    for data in page_data:
        if data.lang_code == lang_code:
            for sense_index, translation_list in translations.items():
                if sense_index not in matched_indexes:
                    data.translations.extend(translation_list)
            break


def process_translation_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    translations: dict[str, list[Translation]],
) -> None:
    lang_name = ""
    lang_code = ""
    sense_index = ""
    last_tr_data = None
    last_node = None
    raw_tags = []
    for index, node in enumerate(list_item.children):
        if isinstance(node, str):
            if index == 0 and ":" in node:
                lang_name = node[: node.index(":")].strip()
                lang_code = name_to_code(lang_name, "pl")
                if lang_code == "":
                    lang_code = "unknown"
            m_index = re.search(r"\(\d+\.\d+\)", node)
            if m_index is not None:
                sense_index = m_index.group(0).strip("()")
            m_roman = re.search(r"\([^()]+\)", node)
            if (
                m_roman is not None
                and last_tr_data is not None
                and (m_index is None or m_index.start() != m_roman.start())
            ):
                last_tr_data.roman = m_roman.group(0).strip("()")
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if len(word) == 0:
                continue
            if (
                isinstance(last_node, WikiNode)
                and last_node.kind == NodeKind.LINK
                and last_tr_data is not None
            ):
                # two links directly next to each other form one word
                last_tr_data.word += word
            else:
                new_tr_data = Translation(
                    word=word,
                    sense_index=sense_index,
                    lang=lang_name,
                    lang_code=lang_code,
                    raw_tags=raw_tags,
                )
                translate_raw_tags(new_tr_data)
                translations[sense_index].append(new_tr_data)
                last_tr_data = new_tr_data
                raw_tags.clear()
        elif isinstance(node, TemplateNode):
            if node.template_name == "furi":
                word, furigana = extract_furi_template(wxr, node)
                if (
                    isinstance(last_node, WikiNode)
                    and last_node.kind == NodeKind.LINK
                    and last_tr_data is not None
                ):
                    last_tr_data.word += word
                    last_tr_data.ruby = [(word, furigana)]
                else:
                    new_tr_data = Translation(
                        word=word,
                        sense_index=sense_index,
                        lang=lang_name,
                        lang_code=lang_code,
                        raw_tags=raw_tags,
                        ruby=[(word, furigana)],
                    )
                    translate_raw_tags(new_tr_data)
                    translations[sense_index].append(new_tr_data)
                    last_tr_data = new_tr_data
                    raw_tags.clear()
            elif isinstance(last_node, str) and (
                "," in last_node or ";" in last_node
            ):
                raw_tag = clean_node(wxr, None, node)
                if len(raw_tag) > 0:
                    raw_tags.append(raw_tag)
            elif last_tr_data is not None:
                raw_tag = clean_node(wxr, None, node)
                if len(raw_tag) > 0:
                    last_tr_data.raw_tags.append(raw_tag)
                    translate_raw_tags(last_tr_data)
        last_node = node


def extract_furi_template(
    wxr: WiktextractContext, node: TemplateNode
) -> tuple[str, str]:
    # https://pl.wiktionary.org/wiki/Szablon:furi
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    kanji = clean_node(wxr, None, node.template_parameters.get(1, ""))
    furigana = ""
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="furigana-caption"
    ):
        furigana = clean_node(wxr, None, span_tag).strip("()")
    return kanji, furigana
