import re

from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
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
    wxr: WiktextractContext,
    base_data: WordEntry,
    page_data: list[WordEntry],
    level_node: LevelNode,
):
    forms = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            raw_tags = []
            for node in list_item.children:
                if isinstance(node, TemplateNode) and node.template_name in [
                    "alter",
                    "def-alt",
                ]:
                    forms.extend(extract_alter_template(wxr, node, raw_tags))
                elif (
                    isinstance(node, TemplateNode)
                    and node.template_name in QUALIFIER_TEMPALTES
                ):
                    raw_tags.extend(extract_qualifier_template(wxr, node))

    if len(page_data) == 0 or page_data[-1].lang != base_data.lang:
        base_data.forms.extend(forms)
    else:
        page_data[-1].forms.extend(forms)


def extract_alter_template(
    wxr: WiktextractContext, t_node: TemplateNode, raw_tags: list[str]
) -> list[Form]:
    forms = []
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
            forms.append(form)
    return forms


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
    l_list = []
    sense = ""
    if linkage_type == "idioms":
        l_list.extend(extract_idiom_section(wxr, level_node))
        linkage_type = "related"
    else:
        for node in level_node.children:
            if isinstance(node, TemplateNode) and (
                re.fullmatch(r"(?:col|der|rel)(?:\d+)?", node.template_name)
                or node.template_name in ["columns", "column"]
            ):
                l_list.extend(extract_col_template(wxr, node))
            elif isinstance(
                node, TemplateNode
            ) and node.template_name.startswith("der-top"):
                sense = clean_node(
                    wxr, None, node.template_parameters.get(1, "")
                )
            elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                for list_item in node.find_child(NodeKind.LIST_ITEM):
                    l_list.extend(
                        extract_linkage_list_item(wxr, list_item, sense)
                    )

    if level_node.kind == NodeKind.LEVEL3:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                getattr(data, linkage_type).extend(l_list)
                for l_data in l_list:
                    data.categories.extend(l_data.categories)
    elif len(page_data) > 0:
        getattr(page_data[-1], linkage_type).extend(l_list)
        for l_data in l_list:
            page_data[-1].categories.extend(l_data.categories)


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
    wxr: WiktextractContext, list_item: WikiNode, sense: str
) -> list[Linkage]:
    l_list = []
    raw_tags = []
    for index, node in enumerate(list_item.children):
        if isinstance(node, TemplateNode):
            if node.template_name in ["sense", "s"]:
                sense = clean_node(wxr, None, node).strip("(): ")
            elif node.template_name in ["l", "link"]:
                l_list.extend(extract_link_template(wxr, node, sense))
            elif node.template_name in ["qualifier", "qual"]:
                raw_tags.append(clean_node(wxr, None, node).strip("()"))
            elif node.template_name in ["zh-l", "zho-l"]:
                l_list.extend(extract_zh_l_template(wxr, node, sense, raw_tags))
                raw_tags.clear()
            elif node.template_name in ["ja-r", "jpn-r"]:
                l_list.append(extract_ja_r_template(wxr, node, sense, raw_tags))
                raw_tags.clear()
            elif node.template_name in ["vi-l", "vie-l"]:
                l_list.append(extract_vi_l_template(wxr, node, sense, raw_tags))
                raw_tags.clear()
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                l_data = Linkage(word=word, sense=sense, raw_tags=raw_tags)
                translate_raw_tags(l_data)
                l_list.append(l_data)
        elif (
            isinstance(node, str)
            and node.strip().startswith("-")
            and len(l_list) > 0
        ):
            l_list[-1].sense = clean_node(
                wxr, None, list_item.children[index:]
            ).strip("- \n")
            break
    if len(raw_tags) > 0 and len(l_list) > 0:
        l_list[-1].raw_tags.extend(raw_tags)
        translate_raw_tags(l_list[-1])
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


def extract_idiom_section(
    wxr: WiktextractContext, level_node: LevelNode
) -> list[Linkage]:
    l_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            l_list.extend(extract_idiom_list_item(wxr, list_item))

    return l_list


def extract_idiom_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Linkage]:
    l_list = []
    bold_index = 0
    sense_nodes = []
    for index, node in enumerate(list_item.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            word = clean_node(wxr, None, node)
            if word != "":
                bold_index = index
                l_list.append(Linkage(word=word, tags=["idiomatic"]))
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                sense = clean_node(wxr, None, child_list_item.children)
                if sense != "" and len(l_list) > 0:
                    l_list[-1].senses.append(sense)
        elif index > bold_index:
            sense_nodes.append(node)

    sense = clean_node(wxr, None, sense_nodes).strip(": ")
    if sense != "" and len(l_list) > 0:
        l_list[-1].sense = sense

    return l_list


def extract_zh_l_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> list[Linkage]:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    roman = ""
    linkage_list = []
    for i_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="Latn"
    ):
        roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value="zh"
    ):
        linkage_data = Linkage(
            sense=sense,
            raw_tags=raw_tags,
            roman=roman,
            word=clean_node(wxr, None, span_tag),
        )
        lang_attr = span_tag.attrs.get("lang", "")
        if lang_attr == "zh-Hant":
            linkage_data.tags.append("Traditional-Chinese")
        elif lang_attr == "zh-Hans":
            linkage_data.tags.append("Simplified-Chinese")
        if len(linkage_data.word) > 0 and linkage_data.word != "／":
            translate_raw_tags(linkage_data)
            linkage_list.append(linkage_data)
    return linkage_list


def extract_ja_r_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense: str,
    raw_tags: list[str] = [],
) -> Linkage:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    linkage_data = Linkage(word="", sense=sense, raw_tags=raw_tags)
    for span_node in expanded_node.find_html("span"):
        span_class = span_node.attrs.get("class", "")
        if "lang" in span_node.attrs:
            ruby_data, no_ruby_nodes = extract_ruby(wxr, span_node)
            linkage_data.word = clean_node(wxr, None, no_ruby_nodes)
            linkage_data.ruby = ruby_data
        elif "tr" in span_class:
            linkage_data.roman = clean_node(wxr, None, span_node)
        elif "mention-gloss" == span_class:
            linkage_data.sense = clean_node(wxr, None, span_node)

    translate_raw_tags(linkage_data)
    return linkage_data


def extract_vi_l_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense: str,
    raw_tags: list[str],
) -> Linkage:
    l_data = Linkage(word="", sense=sense, raw_tags=raw_tags)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        match span_lang:
            case "vi":
                l_data.word = clean_node(wxr, None, span_tag)
            case "vi-Latn":
                l_data.roman = clean_node(wxr, None, span_tag)
    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, l_data, link_node)
    return l_data
