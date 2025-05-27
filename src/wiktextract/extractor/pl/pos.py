import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import AltForm, Sense, WordEntry
from .tags import translate_raw_tags

# All POS categories
# https://pl.wiktionary.org/wiki/Kategoria:Części_mowy_wg_języków
# Polish POS
# https://pl.wiktionary.org/wiki/Kategoria:Części_mowy_języka_polskiego
POS_DATA = {
    "czasownik": {"pos": "verb"},
    "czasownika": {"pos": "verb"},
    # Szablon:szwedzki czasownik frazowy
    "czasownik frazowy (partikelverb)": {"pos": "verb", "tags": ["phrase"]},
    "fraza": {"pos": "phrase"},
    "klasyfikator": {"pos": "classifier"},
    "liczebnik": {"pos": "num"},
    "liczebnikowa": {"pos": "num"},
    "międzyrostek": {"pos": "interfix", "tags": ["morpheme"]},
    "morfem": {"pos": "unknown", "tags": ["morpheme"]},
    "określnik": {"pos": "det"},
    "partykuła": {"pos": "particle"},
    "partykułowa": {"pos": "particle"},
    # Szablon:phrasal verb
    "phrasal verb (czasownik frazowy)": {"pos": "verb", "tags": ["phrase"]},
    "przedimek": {"pos": "article"},
    "przedrostek": {"pos": "prefix", "tags": ["morpheme"]},
    "przyimek": {"pos": "prep"},
    "przyimkowa": {"pos": "prep_phrase"},
    "przymiotnik": {"pos": "adj"},
    "przymiotnikowym": {"pos": "adj"},
    "przymiotnikowa": {"pos": "adj_phrase"},
    "przyrostek": {"pos": "suffix", "tags": ["morpheme"]},
    "przysłówek": {"pos": "adv"},
    "przysłówkowa": {"pos": "adv_phrase"},
    "pytajny": {"pos": "pron", "tags": ["interrogative"]},  # "zaimek pytajny"
    "rodzajnik": {"pos": "article", "tags": ["gendered"]},
    "rzeczownik": {"pos": "noun"},
    "rzeczownikowa": {"pos": "noun"},
    "skrótowiec": {"pos": "abbrev", "tags": ["abbreviation"]},
    "spójnik": {"pos": "conj"},
    "symbol": {"pos": "symbol"},
    "wrostek": {"pos": "infix", "tags": ["morpheme"]},
    "wykrzyknik": {"pos": "intj"},
    "wykrzyknika": {"pos": "intj"},
    "wykrzyknikowa": {"pos": "intj"},
    "zaimka": {"pos": "pron"},
    "zaimek": {"pos": "pron"},
    "zaimkowy": {"pos": "pron"},
    "znak interpunkcyjny": {"pos": "punct", "tags": ["punctuation"]},
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
    level_node: LevelNode,
) -> None:
    for node in level_node.find_child(NodeKind.ITALIC | NodeKind.LIST):
        if node.kind == NodeKind.ITALIC:
            process_pos_line_italic_node(wxr, page_data, base_data, node)
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                if len(page_data) == 0:
                    page_data.append(base_data.model_copy(deep=True))
                process_gloss_list_item(wxr, page_data[-1], list_item)


def process_pos_line_italic_node(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    italic_node: WikiNode,
) -> None:
    has_pos = False
    page_data.append(base_data.model_copy(deep=True))
    for child in italic_node.children:
        if isinstance(child, TemplateNode):
            child_text = clean_node(wxr, page_data[-1], child)
            if child.template_name.startswith("forma "):
                # inflection form header templates
                # https://pl.wiktionary.org/wiki/Kategoria:Szablony_nagłówków_form_fleksyjnych
                pos_text = child_text.split(", ")[0]
                if pos_text in POS_DATA:
                    update_pos_data(page_data[-1], pos_text, POS_DATA[pos_text])
                    has_pos = True
                page_data[-1].tags.append("form-of")
            elif child_text in POS_DATA:
                update_pos_data(page_data[-1], child_text, POS_DATA[child_text])
                has_pos = True
            else:
                is_pos = False
                for prefix, pos_data in POS_PREFIXES.items():
                    if child_text.startswith(prefix):
                        update_pos_data(page_data[-1], child_text, pos_data)
                        is_pos = True
                        break
                if not is_pos and child_text not in IGNORE_POS_LINE_TEXT:
                    page_data[-1].raw_tags.append(child_text)
        elif isinstance(child, str):
            if child.strip() in POS_DATA:
                child = child.strip()
                update_pos_data(page_data[-1], child, POS_DATA[child])
                has_pos = True
            else:
                for text in child.strip(", ").split():
                    text = text.strip(", ")
                    if text in POS_DATA:
                        update_pos_data(page_data[-1], text, POS_DATA[text])
                        has_pos = True
                    elif text not in IGNORE_POS_LINE_TEXT:
                        page_data[-1].raw_tags.append(text)
    translate_raw_tags(page_data[-1])
    if not has_pos:
        page_data.pop()


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
            process_form_of_template(wxr, sense, gloss_node)
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_node), expand_all=True
            )
            expanded_text = clean_node(wxr, sense, expanded_node.children)
            if (
                expanded_text.endswith(".")
                and len(gloss_node.template_parameters) == 0
            ):
                # https://pl.wiktionary.org/wiki/Pomoc:Skróty_używane_w_Wikisłowniku
                raw_tags.append(expanded_text)
            else:
                gloss_nodes.extend(expanded_node.children)
        else:
            gloss_nodes.append(gloss_node)
    gloss_text = clean_node(wxr, sense, gloss_nodes)
    m = re.match(r"\(\d+\.\d+\)", gloss_text)
    sense_index = ""
    if m is not None:
        sense_index = m.group(0).strip("()")
        gloss_text = gloss_text[m.end() :].strip("=; ")
    if "form-of" in word_entry.tags and len(sense.form_of) == 0:
        form_of = ""
        for node in gloss_nodes:
            if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                form_of = clean_node(wxr, None, node)
        if len(form_of) > 0:
            sense.form_of.append(AltForm(word=form_of))
    if len(gloss_text) > 0:
        sense.raw_tags = raw_tags
        sense.sense_index = sense_index
        sense.glosses.append(gloss_text)
        translate_raw_tags(sense)
        word_entry.senses.append(sense)


def process_form_of_template(
    wxr: WiktextractContext, sense: Sense, template_node: TemplateNode
) -> None:
    if template_node.template_name == "zob-ekwiw-pupr":
        if "form-of" not in sense.tags:
            sense.tags.append("form-of")
        word = clean_node(
            wxr, None, template_node.template_parameters.get(1, "")
        )
        sense.form_of.append(AltForm(word=word))
