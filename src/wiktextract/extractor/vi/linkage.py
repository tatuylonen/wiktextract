import re

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    WikiNode,
    NodeKind,
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

QUALIFIER_TEMPALTES = ["qualifier", "qual", "q", "qf", "i"]


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
                raw_tags.clear()

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


def extract_alt_form_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            for node in list_item.children:
                if isinstance(node, TemplateNode) and node.template_name in [
                    "alter",
                    "def-alt",
                ]:
                    extract_alter_template(wxr, base_data, node, raw_tags)
                elif (
                    isinstance(node, TemplateNode)
                    and node.template_name in QUALIFIER_TEMPALTES
                ):
                    raw_tags.extend(extract_qualifier_template(wxr, node))


def extract_alter_template(
    wxr: WiktextractContext,
    base_data: WordEntry,
    t_node: TemplateNode,
    raw_tags: list[str],
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            form = Form(form=word, tags=["alternative"], raw_tags=raw_tags)
            translate_raw_tags(form)
            base_data.forms.append(form)


def extract_qualifier_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[str]:
    raw_tags = []
    for raw_tag in clean_node(wxr, None, t_node).strip("()").split(","):
        raw_tag = raw_tag.strip()
        if raw_tag != "":
            raw_tags.append(raw_tag)
    return raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
):
    l_data = []
    for node in level_node.children:
        if isinstance(node, TemplateNode) and (
            re.fullmatch(r"(?:col|der|rel)(?:\d+)?", node.template_name)
            or node.template_name in ["columns", "column"]
        ):
            l_data.extend(extract_col_template(wxr, node))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                l_data.extend(extract_linkage_list_item(wxr, list_item))

    if level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                getattr(data, linkage_type).extend(l_data)
    elif len(page_data) > 0:
        getattr(page_data[-1], linkage_type).extend(l_data)


def extract_col_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Linkage]:
    l_list = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for li_tag in expanded_template.find_html_recursively("li"):
        first_word = True
        translation = ""
        for node in li_tag.children:
            if isinstance(node, str):
                m = re.search(r"“(.+)”", node)
                if m is not None:
                    translation = m.group(1).strip()
        for span_tag in li_tag.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            span_class = span_tag.attrs.get("class", "")
            if span_lang.endswith("-Latn") and len(l_list) > 0:
                l_list[-1].roman = clean_node(wxr, None, span_tag)
            elif span_lang == lang_code:
                if lang_code == "zh":
                    l_data = Linkage(word=clean_node(wxr, None, span_tag))
                    if "Hant" in span_class:
                        l_data.tags.append("Traditional-Chinese")
                    elif "Hans" in span_class:
                        l_data.tags.append("Simplified-Chinese")
                    l_list.append(l_data)
                elif not first_word:
                    l_list[-1].other = clean_node(wxr, None, span_tag)
                else:
                    l_list.append(
                        Linkage(
                            word=clean_node(wxr, None, span_tag),
                            translation=translation,
                        )
                    )
                    first_word = False

    return l_list


def extract_linkage_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Linkage]:
    l_list = []
    sense = ""
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["sense", "s"]:
                sense = clean_node(wxr, None, node).strip("(): ")
            elif node.template_name in ["l", "link"]:
                l_list.extend(extract_link_template(wxr, node, sense))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                l_list.append(Linkage(word=word, sense=sense))
    return l_list


def extract_link_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: str
) -> list[Linkage]:
    l_list = []
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_template.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        if span_lang == lang_code:
            l_list.append(
                Linkage(word=clean_node(wxr, None, span_tag), sense=sense)
            )

    return l_list
