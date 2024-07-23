import re

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .tags import translate_raw_tags

POS_DATA = {
    "rzeczownik": {"pos": "noun"},
    "czasownik": {"pos": "verb"},
    "przyimek": {"pos": "prep"},
    "przymiotnik": {"pos": "adj"},
    "przyrostek": {"pos": "suffix", "tags": ["morpheme"]},
    "wrostek": {"pos": "infix", "tags": ["morpheme"]},
    "przedrostek": {"pos": "prefix", "tags": ["morpheme"]},
    "przysłówek": {"pos": "adv"},
    "przedimek": {"pos": "article"},
    "klasyfikator": {"pos": "classifier"},
    "spójnik": {"pos": "conj"},
    "określnik": {"pos": "det"},
    "międzyrostek": {"pos": "interfix", "tags": ["morpheme"]},
    "morfem": {"pos": "unknown", "tags": ["morpheme"]},
    "wykrzyknik": {"pos": "intj"},
    "symbol": {"pos": "symbol"},
    "liczebnik": {"pos": "num"},
    "partykuła": {"pos": "particle"},
    "skrótowiec": {"pos": "abbrev", "tags": ["abbreviation"]},
    "zaimek": {"pos": "pron"},
}


def extract_pos_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    for node in level_node.find_child(NodeKind.ITALIC | NodeKind.LIST):
        if node.kind == NodeKind.ITALIC:
            pos_line_text = clean_node(wxr, None, node)
            pos_text_list = pos_line_text.split()
            if len(pos_text_list) == 0:
                continue
            pos_text = pos_text_list[0].removesuffix(",")
            page_data.append(base_data.model_copy(deep=True))
            if pos_text in POS_DATA:
                pos_data = POS_DATA[pos_text]
                page_data[-1].pos = pos_data["pos"]
                page_data[-1].tags.extend(pos_data.get("tags", []))
            else:
                wxr.wtp.debug(
                    f"Unknown POS: {pos_text}", sortid="extractor/pl/pos"
                )
            page_data[-1].pos_text = pos_text
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                process_gloss_list_item(wxr, page_data[-1], list_item)


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
