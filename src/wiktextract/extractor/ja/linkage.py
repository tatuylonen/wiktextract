from mediawiki_langcodes import name_to_code
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
from .models import Descendant, Form, Linkage, WordEntry
from .section_titles import LINKAGES
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    if linkage_type in ["cognates", "descendants"]:
        extract_descendant_section(wxr, word_entry, level_node, linkage_type)
        return

    sense = ""
    for node in level_node.find_child(NodeKind.LIST | NodeKind.TEMPLATE):
        if isinstance(node, TemplateNode) and node.template_name.startswith(
            "rel-top"
        ):
            sense = clean_node(wxr, None, node.template_parameters.get(1, ""))
        elif node.kind == NodeKind.LIST:
            for list_item in node.find_child_recursively(NodeKind.LIST_ITEM):
                linkage_type = process_linkage_list_item(
                    wxr, word_entry, list_item, linkage_type, sense
                )


def process_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
    sense: str,
) -> str:
    after_colon = False
    for node_idx, node in enumerate(list_item.children):
        if isinstance(node, str) and ":" in node and not after_colon:
            linkage_type_text = clean_node(
                wxr, None, list_item.children[:node_idx]
            )
            linkage_type = LINKAGES.get(linkage_type_text, linkage_type)
            after_colon = True
        elif isinstance(node, TemplateNode) and node.template_name.startswith(
            ("おくりがな", "ふりがな", "xlink")
        ):
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node), expand_all=True
            )
            ruby, no_ruby = extract_ruby(wxr, expanded_node.children)
            if node.template_name == "xlink":
                ruby.clear()
            word = clean_node(wxr, None, no_ruby)
            if len(word) > 0:
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, ruby=ruby, sense=sense)
                )
        elif isinstance(node, TemplateNode) and node.template_name == "l":
            l_data = extract_l_template(wxr, node)
            if l_data.word != "":
                getattr(word_entry, linkage_type).append(l_data)
        elif isinstance(node, TemplateNode) and node.template_name == "zh-l":
            getattr(word_entry, linkage_type).extend(
                extract_zh_l_template(wxr, node)
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if len(word) > 0:
                getattr(word_entry, linkage_type).append(
                    Linkage(word=word, sense=sense)
                )
        elif isinstance(node, TemplateNode) and node.template_name == "sense":
            sense = clean_node(wxr, None, node).strip("(): ")

    return linkage_type


def extract_descendant_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    desc_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            desc_list.extend(process_desc_list_item(wxr, list_item, []))
    getattr(word_entry, linkage_type).extend(desc_list)


def process_desc_list_item(
    wxr: WiktextractContext, list_item: WikiNode, parent_list: list[Descendant]
) -> list[Descendant]:
    desc_list = []
    lang_name = "unknown"
    lang_code = "unknown"
    for index, child in enumerate(list_item.children):
        if isinstance(child, str) and ":" in child and lang_name == "unknown":
            lang_name = clean_node(wxr, None, list_item.children[:index])
            lang_code = name_to_code(lang_name, "ja")
        elif isinstance(child, TemplateNode) and child.template_name == "etyl":
            lang_name = clean_node(wxr, None, child)
            lang_code = clean_node(
                wxr, None, child.template_parameters.get(1, "")
            )
        elif isinstance(child, TemplateNode) and child.template_name == "l":
            l_data = extract_l_template(wxr, child)
            if l_data.word != "":
                desc_list.append(
                    Descendant(
                        word=l_data.word,
                        lang=lang_name,
                        lang_code=lang_code
                        or clean_node(
                            wxr, None, child.template_parameters.get(1, "")
                        ),
                        tags=l_data.tags,
                        raw_tags=l_data.raw_tags,
                        roman=l_data.roman,
                        sense=l_data.sense,
                    )
                )
        elif isinstance(child, TemplateNode) and child.template_name == "desc":
            new_descs, lang_code, lang_name = extract_desc_template(wxr, child)
            desc_list.extend(new_descs)
        elif isinstance(child, TemplateNode) and child.template_name == "zh-l":
            for l_data in extract_zh_l_template(wxr, child):
                if l_data.word != "":
                    desc_list.append(
                        Descendant(
                            word=l_data.word,
                            lang=lang_name,
                            lang_code=lang_code,
                            tags=l_data.tags,
                            roman=l_data.roman,
                        )
                    )
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LIST:
            for next_list_item in child.find_child(NodeKind.LIST_ITEM):
                process_desc_list_item(wxr, next_list_item, desc_list)

    for p_data in parent_list:
        p_data.descendants.extend(desc_list)
    return desc_list


# カテゴリ:文法テンプレート
LINKAGE_TEMPLATES = {
    "syn": "synonyms",
    "ant": "antonyms",
    "hyper": "hypernyms",
    "hypo": "hyponyms",
    "hyponyms": "hyponyms",
    "mero": "meronyms",
    "cot": "coordinate_terms",
}


def extract_gloss_list_linkage_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html(
        "span", attr_name="lang", attr_value=lang_code
    ):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            getattr(word_entry, LINKAGE_TEMPLATES[t_node.template_name]).append(
                Linkage(
                    word=word,
                    sense=" ".join(word_entry.senses[-1].glosses)
                    if len(word_entry.senses) > 0
                    and len(word_entry.senses[-1].glosses) > 0
                    else "",
                )
            )


def extract_l_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> Linkage:
    # https://ja.wiktionary.org/wiki/テンプレート:l
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    l_data = Linkage(word="")
    for span_tag in expanded_node.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        span_class = span_tag.attrs.get("class", "")
        if span_lang == lang_code:
            l_data.word = clean_node(wxr, None, span_tag)
        elif span_lang == lang_code + "-Latn":
            l_data.roman = clean_node(wxr, None, span_tag)
        elif span_class == "gender":
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                l_data.raw_tags.append(raw_tag)

    if "lit" in t_node.template_parameters:
        l_data.literal_meaning = clean_node(
            wxr, None, t_node.template_parameters["t"]
        )
    for arg_name in (4, "gloss", "t"):
        if arg_name in t_node.template_parameters:
            l_data.sense = clean_node(
                wxr, None, t_node.template_parameters[arg_name]
            )
    translate_raw_tags(l_data)
    return l_data


def extract_alt_form_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for node in level_node.find_child_recursively(
        NodeKind.LINK | NodeKind.TEMPLATE
    ):
        if node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                word_entry.forms.append(Form(form=word, tags=["alt-of"]))
        elif isinstance(node, TemplateNode) and node.template_name == "l":
            l_data = extract_l_template(wxr, node)
            if l_data.word != "":
                word_entry.forms.append(
                    Form(
                        form=l_data.word,
                        tags=l_data.tags,
                        raw_tags=l_data.raw_tags,
                        roman=l_data.roman,
                    )
                )


def extract_desc_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> tuple[list[Descendant], str, str]:
    d_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    lang_name = "unknown"
    for node in expanded_node.children:
        if isinstance(node, str) and node.strip().endswith(":"):
            lang_name = node.strip(": ")
        elif (
            isinstance(node, HTMLNode)
            and node.tag == "span"
            and lang_code == node.attrs.get("lang", "")
        ):
            for link_node in node.find_child(NodeKind.LINK):
                word = clean_node(wxr, None, link_node)
                if word != "":
                    d_list.append(
                        Descendant(
                            lang=lang_name, lang_code=lang_code, word=word
                        )
                    )

    return d_list, lang_code, lang_name


def extract_zh_l_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Linkage]:
    l_list = []
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    roman = ""
    for i_tag in expanded_node.find_html("i"):
        roman = clean_node(wxr, None, i_tag)
    for index, span_tag in enumerate(
        expanded_node.find_html("span", attr_name="lang", attr_value="zh")
    ):
        word = clean_node(wxr, None, span_tag)
        if word != "":
            l_list.append(
                Linkage(
                    word=word,
                    tags=[
                        "Traditional Chinese"
                        if index == 0
                        else "Simplified Chinese"
                    ],
                    roman=roman,
                )
            )
    return l_list
