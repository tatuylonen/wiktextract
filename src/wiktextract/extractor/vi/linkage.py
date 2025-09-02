from wikitextprocessor import (
    HTMLNode,
    TemplateNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .tags import translate_raw_tags

GLOSS_LIST_LINKAGE_TEMPLATES = {
    "antonyms": "antonyms",
    "def-ant": "antonyms",
    "antonym": "antonyms",
    "coordinate terms": "coordinate_terms",
    "def-cot": "coordinate_terms",
    "def-coo": "coordinate_terms",
    "cot": "coordinate_terms",
    "holonyms": "holonyms",
    "holonym": "holonyms",
    "holo": "holonyms",
    "hypernyms": "hypernyms",
    "hyper": "hypernyms",
    "hyponyms": "hyponyms",
    "hypo": "hyponyms",
    "inline alt forms": "alt_forms",
    "alti": "alt_forms",
    "meronyms": "meronyms",
    "mero": "meronyms",
    "synonyms": "synonyms",
    "synonym": "synonyms",
    "def-syn": "synonyms",
    "synsee": "synonyms",
}


def extract_gloss_list_linkage_template(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    linkage_type: str,
    sense: str,
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    l_list = []
    raw_tags = []
    for top_span_tag in expanded_node.find_html("span"):
        for node in top_span_tag.children:
            if isinstance(node, HTMLNode) and node.tag == "span":
                span_lang = node.attrs.get("lang", "")
                span_class = node.attrs.get("class", "").split()
                if span_lang == lang_code:
                    l_data = Linkage(
                        word=clean_node(wxr, None, node),
                        sense=sense,
                        raw_tags=raw_tags,
                    )
                    if "Hant" in span_class:
                        l_data.tags.append("Traditional-Chinese")
                    elif "Hans" in span_class:
                        l_data.tags.append("Simplified-Chinese")
                    if l_data.word != "":
                        translate_raw_tags(l_data)
                        l_list.append(l_data)
                elif span_lang == f"{lang_code}-Latn" or "tr" in span_class:
                    roman = clean_node(wxr, None, node)
                    for d in l_list:
                        d.roman = roman
                elif "mention-gloss" in span_class:
                    sense = clean_node(wxr, None, node)
                    for d in l_list:
                        d.sense = sense
                elif "qualifier-content" in span_class:
                    raw_tag_str = clean_node(wxr, None, node)
                    for raw_tag in raw_tag_str.split("，"):
                        raw_tag = raw_tag.strip()
                        if raw_tag != "":
                            raw_tags.append(raw_tag)
            elif isinstance(node, str) and node.strip() == ",":
                if linkage_type == "alt_forms":
                    for l_data in l_list:
                        word_entry.forms.append(
                            Form(
                                form=l_data.word,
                                sense=l_data.sense,
                                tags=l_data.tags + ["alternative"],
                                raw_tags=l_data.raw_tags,
                                roman=l_data.roman,
                            )
                        )
                else:
                    getattr(word_entry, linkage_type).extend(l_list)
                l_list.clear()

    if linkage_type == "alt_forms":
        for l_data in l_list:
            word_entry.forms.append(
                Form(
                    form=l_data.word,
                    sense=l_data.sense,
                    tags=l_data.tags + ["alternative"],
                    raw_tags=l_data.raw_tags,
                    roman=l_data.roman,
                )
            )
    else:
        getattr(word_entry, linkage_type).extend(l_list)
