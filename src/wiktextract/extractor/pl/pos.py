import re

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .tags import translate_raw_tags

POS_DATA = {
    "czasownik": {"pos": "verb"},
    # Szablon:szwedzki czasownik frazowy
    "czasownik frazowy (partikelverb)": {"pos": "verb", "tags": ["phrase"]},
    "klasyfikator": {"pos": "classifier"},
    "liczebnik": {"pos": "num"},
    "międzyrostek": {"pos": "interfix", "tags": ["morpheme"]},
    "morfem": {"pos": "unknown", "tags": ["morpheme"]},
    "określnik": {"pos": "det"},
    "partykuła": {"pos": "particle"},
    # Szablon:phrasal verb
    "phrasal verb (czasownik frazowy)": {"pos": "verb", "tags": ["phrase"]},
    "przyimek": {"pos": "prep"},
    "przymiotnik": {"pos": "adj"},
    "przyrostek": {"pos": "suffix", "tags": ["morpheme"]},
    "przedrostek": {"pos": "prefix", "tags": ["morpheme"]},
    "przysłówek": {"pos": "adv"},
    "przedimek": {"pos": "article"},
    "rzeczownik": {"pos": "noun"},
    "skrótowiec": {"pos": "abbrev", "tags": ["abbreviation"]},
    "spójnik": {"pos": "conj"},
    "symbol": {"pos": "symbol"},
    "wrostek": {"pos": "infix", "tags": ["morpheme"]},
    "wykrzyknik": {"pos": "intj"},
    "zaimek": {"pos": "pron"},
}

# Category:Proverb Templates
# https://pl.wiktionary.org/wiki/Kategoria:Szablony_przysłów
POS_PREFIXES = {
    "przysłowie": {"pos": "proverb"},
    "sentencja": {"pos": "phrase"},
}

IGNORE_POS_LINE_TEXT = frozenset(["rodzaj"])


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    for node in level_node.find_child(NodeKind.ITALIC | NodeKind.LIST):
        if node.kind == NodeKind.ITALIC:
            process_pos_line_italic_node(wxr, page_data, base_data, node)
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                process_gloss_list_item(wxr, page_data[-1], list_item)


def process_pos_line_italic_node(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    italic_node: WikiNode,
) -> None:
    page_data.append(base_data.model_copy(deep=True))
    for child in italic_node.children:
        if isinstance(child, TemplateNode):
            child_text = clean_node(wxr, page_data[-1], child)
            if child_text in POS_DATA:
                update_pos_data(page_data[-1], child_text, POS_DATA[child_text])
            else:
                is_pos = False
                for prefix, pos_data in POS_PREFIXES.items():
                    if child_text.startswith(prefix):
                        update_pos_data(
                            page_data[-1], child_text, POS_DATA[child_text]
                        )
                        is_pos = True
                        break
                if not is_pos and child_text not in IGNORE_POS_LINE_TEXT:
                    page_data[-1].raw_tags.append(child_text)
        elif isinstance(child, str):
            for text in child.strip(", ").split():
                text = text.strip(", ")
                if text in POS_DATA:
                    update_pos_data(page_data[-1], text, POS_DATA[text])
                elif text not in IGNORE_POS_LINE_TEXT:
                    page_data[-1].raw_tags.append(text)
    translate_raw_tags(page_data[-1])


def update_pos_data(
    word_entry: WordEntry, pos_text: str, pos_data: dict
) -> None:
    word_entry.pos = pos_data["pos"]
    word_entry.tags.extend(pos_data.get("tags", []))
    word_entry.pos_text = pos_text


def process_gloss_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item_node: WikiNode
) -> None:
    sense = Sense()
    gloss_nodes = []
    raw_tags = []
    for gloss_node in list_item_node.children:
        if isinstance(gloss_node, TemplateNode):
            if gloss_node.template_name == "wikipedia":
                continue
            expanded_text = clean_node(wxr, sense, gloss_node)
            if expanded_text.endswith("."):
                # https://pl.wiktionary.org/wiki/Pomoc:Skróty_używane_w_Wikisłowniku
                raw_tags.append(expanded_text)
            else:
                gloss_nodes.append(expanded_text)
        else:
            gloss_nodes.append(gloss_node)
    gloss_text = clean_node(wxr, sense, gloss_nodes)
    m = re.match(r"\(\d+\.\d+\)", gloss_text)
    sense_index = ""
    if m is not None:
        sense_index = m.group(0).strip("()")
        gloss_text = gloss_text[m.end() :].strip("=; ")
    if len(gloss_text) > 0:
        sense.raw_tags = raw_tags
        sense.sense_index = sense_index
        sense.glosses.append(gloss_text)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)
