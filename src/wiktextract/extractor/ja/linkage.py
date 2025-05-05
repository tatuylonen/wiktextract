from mediawiki_langcodes import code_to_name, name_to_code
from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

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
            extract_l_template(wxr, word_entry, node, linkage_type)
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
    lang_name = ""
    lang_code = ""
    for index, child in enumerate(list_item.children):
        if isinstance(child, str) and ":" in child:
            lang_name = clean_node(wxr, None, list_item.children[:index])
            lang_code = name_to_code(lang_name, "ja")
        elif isinstance(child, TemplateNode) and child.template_name == "l":
            # https://ja.wiktionary.org/wiki/テンプレート:l
            l_args = {
                2: "word",
                3: "word",
                4: "sense",
                "gloss": "sense",
                "t": "sense",
                "tr": "roman",
            }
            if lang_code == "":
                lang_code = clean_node(
                    wxr, None, child.template_parameters.get(1, "")
                )
            if lang_name == "":
                lang_name = code_to_name(lang_code, "ja")
            desc_data = Descendant(lang=lang_name, lang_code=lang_code)
            for arg_name, field in l_args.items():
                arg_value = clean_node(
                    wxr, None, child.template_parameters.get(arg_name, "")
                )
                if arg_value != "":
                    setattr(desc_data, field, arg_value)
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(child), expand_all=True
            )
            for span_tag in expanded_node.find_html(
                "span", attr_name="class", attr_value="gender"
            ):
                raw_tag = clean_node(wxr, None, span_tag)
                if raw_tag != "":
                    desc_data.raw_tags.append(raw_tag)

            if desc_data.word != "":
                translate_raw_tags(desc_data)
                desc_list.append(desc_data)
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
    wxr: WiktextractContext,
    word_entry: WordEntry,
    t_node: TemplateNode,
    l_type: str,
) -> None:
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

    if l_data.word != "":
        translate_raw_tags(l_data)
        if l_type == "forms":
            word_entry.forms.append(
                Form(
                    form=l_data.word,
                    tags=l_data.tags,
                    raw_tags=l_data.raw_tags,
                    roman=l_data.roman,
                )
            )
        else:
            getattr(word_entry, l_type).append(l_data)


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
            extract_l_template(wxr, word_entry, node, "forms")
